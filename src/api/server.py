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
    
    cursor.execute("SELECT COUNT(*) as total_clusters FROM clusters")
    total_clusters = cursor.fetchone()['total_clusters']
    
    cursor.execute("SELECT COUNT(*) as total_insights FROM insights")
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
        SELECT cluster_id, cluster_name, prevalence, intent_relevance, severity, ROUND(opportunity_score, 2) as opportunity_score 
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
        SELECT id, topic, problem_statement, intent, purchase_stage, source_review_id 
        FROM insights 
        WHERE cluster_id = ?
    """, (cluster_id,))
    
    insights = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not insights:
        raise HTTPException(status_code=404, detail="Cluster not found or has no insights.")
        
    return insights

if __name__ == "__main__":
    # pyrefly: ignore [missing-import]
    import uvicorn
    # This block is used when running locally: `python src/api/server.py`
    uvicorn.run(app, host="127.0.0.1", port=8000)
