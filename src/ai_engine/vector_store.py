import os
import sqlite3
# pyrefly: ignore [missing-import]
from chromadb import PersistentClient
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer

def build_vector_db():
    print("Finding all AI insights from Canonical SQLite Database...")
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "warehouse", "ajio_warehouse.db")
    if not os.path.exists(db_path):
        print("Database not found. Run sync_to_sqlite.py first.")
        return
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # We only embed records that are UNIQUE (no exact duplicates) 
    # and that are RELEVANT or POSSIBLY_RELEVANT. NOT_RELEVANT is excluded from semantic search.
    cursor.execute('''
        SELECT * FROM insights 
        WHERE duplicate_status = 'UNIQUE' 
        AND relevance_status IN ('RELEVANT', 'POSSIBLY_RELEVANT')
    ''')
    
    insights = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not insights:
        print("Error: No unique relevant insights found in database.")
        return
        
    vector_db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "vector_db")
    os.makedirs(vector_db_dir, exist_ok=True)
    
    print(f"Initializing ChromaDB at {vector_db_dir}...")
    client = PersistentClient(path=vector_db_dir)
    
    print("Loading HuggingFace embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # We clear the collection to ensure we only have the strictly valid, unique subset.
    try:
        client.delete_collection("ajio_insights")
    except Exception:
        pass
        
    collection = client.create_collection(name="ajio_insights")
    
    documents = []
    metadatas = []
    ids = []
    
    print(f"Embedding {len(insights)} verified canonical insights...")
    
    for i, insight in enumerate(insights):
        # Embed the core observable problem for semantic clustering
        text_to_embed = insight.get('observed_problem_summary') or insight.get('original_text') or "Unknown problem"
        
        fingerprint_key = insight.get('source_id')
        
        # Safely convert metadata to strings for ChromaDB compatibility
        metadata = {}
        for key, val in insight.items():
            if val is None:
                metadata[key] = ""
            elif isinstance(val, (int, float, bool, str)):
                metadata[key] = val
            else:
                metadata[key] = str(val)
                
        documents.append(text_to_embed)
        metadatas.append(metadata)
        ids.append(f"insight_{fingerprint_key}")
        
    if not documents:
        print("No valid documents to embed.")
        return
        
    embeddings_list = model.encode(documents, show_progress_bar=True)
    embeddings = embeddings_list.tolist()
    
    collection.upsert(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Successfully vectorized and stored {len(documents)} relevant insights in ChromaDB!")

if __name__ == "__main__":
    build_vector_db()
