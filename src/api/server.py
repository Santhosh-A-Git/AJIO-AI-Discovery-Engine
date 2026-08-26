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

@app.get("/api/feedback")
def get_feedback():
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "cleansed", "clean_dataset.json")
    if not os.path.exists(dataset_path):
        return []
    import json
    import random
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    valid_reviews = [r for r in data if len(r.get('text', '')) > 20]
    
    by_source = {}
    for r in valid_reviews:
        src = r.get("source", "UNKNOWN")
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(r)
        
    final_list = []
    if not by_source:
        return []
        
    per_source = 100 // len(by_source)
    for src, items in by_source.items():
        random.shuffle(items)
        final_list.extend(items[:per_source])
        
    remaining = 100 - len(final_list)
    if remaining > 0:
        all_remaining = [item for src_items in by_source.values() for item in src_items[per_source:]]
        random.shuffle(all_remaining)
        final_list.extend(all_remaining[:remaining])
        
    random.shuffle(final_list)
    return final_list

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
        
        llm = ChatGroq(model_name="qwen/qwen3.8-27b", groq_api_key=api_key, model_kwargs={"response_format": {"type": "json_object"}})
        
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
Analyze the following exact user complaints and synthesize a highly actionable summary of user behavior regarding wishlist to purchase friction.

Extract exactly 1 to 2 distinct insights.
You must respond STRICTLY in JSON format matching this exact schema:
{{
  "insights": [
    {{
      "headline": "A short, punchy 3-5 word title for the insight",
      "explanation": "A concise, single-sentence explanation of WHY users behave this way and the severe friction points",
      "evidence": {{
        "source": "The origin of the friction (e.g., App Store, Google News, etc.) based on the context",
        "user_segment_clue": "e.g., Price-sensitive, High intent, Trend-seeker",
        "wishlist_intent": "e.g., Price tracking, Bookmarking, Waiting for review",
        "why_saved": "Why did the user save this item to their wishlist?",
        "conversion_blocker": "What is the exact friction stopping them from purchasing?",
        "uncertainty": "What is the user unsure about? (e.g., Size, Quality, Delivery)",
        "workaround": "What did the user do instead? (e.g., Bought elsewhere, abandoned)",
        "external_platform_used": "Any competitors or platforms mentioned (e.g., Myntra, Instagram, none)",
        "purchase_status": "e.g., Abandoned, Delayed, Bought Elsewhere",
        "evidence_strength": "High/Medium/Low based on the number of complaints",
        "theme": "A 2-3 word high-level theme"
      }}
    }}
  ]
}}

USER QUERY: {req.query}

RAW COMPLAINTS FOUND:
{context_text}
"""
    
    try:
        response = chat_model.invoke(prompt)
        answer = response.content
        
        # Robustly filter out reasoning blocks if model didn't obey json strictness fully
        if "</think>" in answer:
            answer = answer.split("</think>")[-1].strip()
        elif "<think>" in answer:
            answer = answer.split("<think>")[0].strip()
            if not answer:
                # the content is inside the think block or empty
                pass

        # Ensure we return valid JSON to frontend
        import json
        import re
        
        # Try to parse the JSON
        try:
            # Strip markdown json blocks if present
            clean_json = re.sub(r'```json\n|\n```|```', '', answer).strip()
            answer_json = json.loads(clean_json)
            return {"structured_insights": answer_json.get("insights", []), "sources": sources}
        except json.JSONDecodeError:
            # Fallback if parsing completely fails
            return {"answer": answer, "sources": sources}
            
    except Exception as e:
        return {"answer": f"Error generating AI synthesis: {str(e)}", "sources": []}

if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import uvicorn
    # This block is used when running locally: `python src/api/server.py`
    uvicorn.run(app, host="127.0.0.1", port=8000)
