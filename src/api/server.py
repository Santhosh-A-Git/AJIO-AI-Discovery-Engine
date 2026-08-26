import os
import sqlite3
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from pydantic import BaseModel
# pyrefly: ignore [missing-import]
from typing import List, Optional

app = FastAPI(title="AJIO Product Discovery API", version="1.0.0")

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for easier deployment, restrict in production if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "warehouse", "ajio_warehouse.db")
    if not os.path.exists(db_path):
        raise HTTPException(status_code=500, detail="Database not found. Please run the backend pipeline first.")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Returns dict-like rows
    return conn

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AJIO Product Discovery API is running!"}

@app.get("/api/stats")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(DISTINCT cluster_id) as total_clusters FROM insights WHERE purchase_stage IN ('Pre-purchase', 'Browsing', 'Checkout')")
    total_clusters = cursor.fetchone()['total_clusters']
    
    cursor.execute("SELECT COUNT(*) as total_insights FROM insights WHERE purchase_stage IN ('Pre-purchase', 'Browsing', 'Checkout')")
    total_insights = cursor.fetchone()['total_insights']
    
    conn.close()
    
    return {
        "total_clusters": total_clusters,
        "total_insights_processed": total_insights
    }

@app.get("/api/clusters")
def get_clusters():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.cluster_id, c.cluster_name, COUNT(i.id) as prevalence, c.intent_relevance, c.severity, ROUND(c.opportunity_score, 2) as opportunity_score 
        FROM clusters c
        JOIN insights i ON c.cluster_id = i.cluster_id
        WHERE i.purchase_stage IN ('Pre-purchase', 'Browsing', 'Checkout')
        GROUP BY c.cluster_id, c.cluster_name, c.intent_relevance, c.severity, c.opportunity_score
        ORDER BY c.opportunity_score DESC
    """)
    clusters = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return clusters

@app.get("/api/insights/{cluster_id}")
def get_insights(cluster_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, topic, problem_statement, intent, purchase_stage, source_review_id 
        FROM insights 
        WHERE cluster_id = ? AND purchase_stage IN ('Pre-purchase', 'Browsing', 'Checkout')
    """, (cluster_id,))
    
    insights = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not insights:
        raise HTTPException(status_code=404, detail="Cluster not found or has no insights.")
        
    return insights

class QueryRequest(BaseModel):
    query: str

# Global caches for RAG
vector_db_client = None
embedding_model = None
llm = None

def get_rag_components():
    global vector_db_client, embedding_model, llm
    if vector_db_client is None:
        # pyrefly: ignore [missing-import]
        import chromadb
        # pyrefly: ignore [missing-import]
        from sentence_transformers import SentenceTransformer
        # pyrefly: ignore [missing-import]
        from langchain_groq import ChatGroq
        # pyrefly: ignore [missing-import]
        from dotenv import load_dotenv
        
        load_dotenv()
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "vector_db")
        vector_db_client = chromadb.PersistentClient(path=db_path)
        # Using a very fast local embedding model
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY is missing for semantic search.")
        
        llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=api_key)
        
    return vector_db_client, embedding_model, llm

@app.post("/api/query")
def query_insights(req: QueryRequest):
    try:
        client, encoder, chat_model = get_rag_components()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # 1. Embed the user's query
    query_vector = encoder.encode([req.query])[0].tolist()
    
    # 2. Search ChromaDB
    collection = client.get_collection("ajio_insights")
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=15,
        where={"purchase_stage": {"$in": ["Pre-purchase", "Browsing", "Checkout"]}}
    )
    
    if not results['documents'] or len(results['documents'][0]) == 0:
        return {"answer": "No relevant reviews found for your query.", "sources": []}
        
    # Extract the top results
    docs = results['documents'][0]
    metas = results['metadatas'][0]
    
    sources = []
    context_text = ""
    for idx, (doc, meta) in enumerate(zip(docs, metas)):
        sources.append({
            "problem_statement": doc,
            "topic": meta.get("topic", ""),
            "intent": meta.get("intent", "")
        })
        context_text += f"- {doc}\n"
        
    # 3. Generate Answer using the LLM
    prompt = f"""You are an elite Product Management AI for AJIO.
Analyze the following exact user complaints and synthesize a highly concise, actionable summary of user behavior.

Format your response strictly as 2-3 insights using this exact structure for each insight. You MUST include line breaks exactly as shown:

**[Insight Title]**

[Brief explanation of WHY users behave this way and the severe friction points, directly below the title]


Do not use bullet points (-). You MUST place a line break between the bold title and the explanation. Separate each insight with a blank line. Do not write introductory or concluding paragraphs.
Respond DIRECTLY with the final insights. Do NOT include a <think> block. Do NOT include your reasoning process.

USER QUERY: {req.query}

RAW COMPLAINTS FOUND:
{context_text}
"""
    
    try:
        response = chat_model.invoke(prompt)
        answer = response.content
        
        # Robustly filter out reasoning blocks
        if "</think>" in answer:
            answer = answer.split("</think>")[-1].strip()
        elif "<think>" in answer:
            answer = answer.split("<think>")[0].strip()
            if not answer:
                answer = "The AI model encountered an error while synthesizing. Please click 'Ask AI' again to retry."
        
    except Exception as e:
        answer = f"Error generating AI synthesis: {str(e)}"
        
    return {
        "answer": answer,
        "sources": sources
    }

if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import uvicorn
    # This block is used when running locally: `python src/api/server.py`
    uvicorn.run(app, host="127.0.0.1", port=8000)
