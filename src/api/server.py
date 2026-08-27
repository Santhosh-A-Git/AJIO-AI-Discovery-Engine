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
from dotenv import load_dotenv

load_dotenv()

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
def get_feedback(relevance: Optional[str] = None, source_type: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM insights WHERE duplicate_status = 'UNIQUE'"
    params = []
    
    if relevance and relevance != "All":
        query += " AND relevance_status = ?"
        if relevance == 'Relevant Only':
            params.append('RELEVANT')
        else:
            params.append(relevance.upper())
            
    if source_type and source_type != "All Sources":
        query += " AND source = ?"
        params.append(source_type)
        
    query += " ORDER BY timestamp DESC LIMIT 100"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Map to frontend expected format
    feedbacks = []
    for r in rows:
        feedbacks.append({
            "id": r["source_id"],
            "source": r["source"],
            "date": r["timestamp"],
            "text": r["original_text"],
            "url": r["source_url"],
            "relevance_status": r["relevance_status"]
        })
        
    return feedbacks

@app.get("/api/stats")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(DISTINCT cluster_id) as total_clusters FROM insights")
    total_clusters = cursor.fetchone()['total_clusters']
    
    # We can get raw total from DB if we inserted everything. Yes, we did.
    cursor.execute("SELECT COUNT(*) as raw_records FROM insights")
    raw_records = cursor.fetchone()['raw_records']
    
    cursor.execute("SELECT COUNT(*) as unique_records FROM insights WHERE duplicate_status = 'UNIQUE'")
    unique_records = cursor.fetchone()['unique_records']
    
    cursor.execute("SELECT COUNT(*) as relevant FROM insights WHERE duplicate_status = 'UNIQUE' AND relevance_status = 'RELEVANT'")
    relevant = cursor.fetchone()['relevant']
    
    cursor.execute("SELECT COUNT(*) as possibly_relevant FROM insights WHERE duplicate_status = 'UNIQUE' AND relevance_status = 'POSSIBLY_RELEVANT'")
    possibly_relevant = cursor.fetchone()['possibly_relevant']
    
    cursor.execute("SELECT COUNT(*) as not_relevant FROM insights WHERE duplicate_status = 'UNIQUE' AND relevance_status = 'NOT_RELEVANT'")
    not_relevant = cursor.fetchone()['not_relevant']
    
    conn.close()
    
    return {
        "raw_records_collected": raw_records,
        "unique_records": unique_records,
        "ai_analyzed_records": raw_records,
        "relevant_observations": relevant,
        "possibly_relevant_observations": possibly_relevant,
        "not_relevant_observations": not_relevant,
        "opportunity_clusters": total_clusters
    }

@app.get("/api/clusters")
def get_clusters():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cluster_id, cluster_name, prevalence, prevalence_norm, intent_relevance_norm, 
        severity_norm, cross_source_norm, segment_concentration_norm, evidence_strength_norm, 
        ROUND(opportunity_score, 2) as opportunity_score 
        FROM clusters
        ORDER BY opportunity_score DESC
    """)
    clusters = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return clusters

@app.get("/api/insights/{cluster_id}")
def get_insights(cluster_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * 
        FROM insights 
        WHERE cluster_id = ?
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
        from dotenv import load_dotenv
        
        load_dotenv()
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "vector_db")
        vector_db_client = chromadb.PersistentClient(path=db_path)
        # Using a very fast local embedding model
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY is missing for semantic search.")
        
        llm = None
        
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
        n_results=15
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
            "original_text": meta.get("original_text", ""),
            "source": meta.get("source", ""),
            "source_type": meta.get("source_type", ""),
            "source_url": meta.get("source_url", ""),
            "source_id": meta.get("source_id", ""),
            "relevance_status": meta.get("relevance_status", ""),
            "wishlist_intent": meta.get("wishlist_intent", ""),
            "conversion_blocker": meta.get("conversion_blocker", ""),
            "uncertainty": meta.get("uncertainty", ""),
            "workaround": meta.get("workaround", ""),
            "purchase_status": meta.get("purchase_status", ""),
            "evidence_strength": meta.get("evidence_strength", ""),
            "theme": meta.get("theme", ""),
            "user_segment_clue": meta.get("user_segment_clue", "")
        })
        context_text += f"- Document: {doc}\n  Context: Source={meta.get('source')}, Intent={meta.get('wishlist_intent')}, Blocker={meta.get('conversion_blocker')}, Uncertainty={meta.get('uncertainty')}, Workaround={meta.get('workaround')}, Purchase Status={meta.get('purchase_status')}\n\n"
        
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
        api_key = os.getenv("GROQ_API_KEY")
        # pyrefly: ignore [missing-import]
        from langchain_groq import ChatGroq
        
        fallback_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "allam-2-7b"]
        answer = None
        
        for model_name in fallback_models:
            try:
                temp_model = ChatGroq(model_name=model_name, groq_api_key=api_key, model_kwargs={"response_format": {"type": "json_object"}})
                response = temp_model.invoke(prompt)
                answer = response.content
                break # Success!
            except Exception as model_err:
                print(f"Model {model_name} failed: {model_err}")
                continue
                
        if not answer:
            raise Exception("All fallback LLM models failed or were rate limited.")
        
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
