import os
import json
import glob
# pyrefly: ignore [missing-import]
from chromadb import PersistentClient
# pyrefly: ignore [missing-import]
from sentence_transformers import SentenceTransformer

def get_all_insights():
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "reports")
    files = glob.glob(os.path.join(reports_dir, "ai_insights_FULL_*.json"))
    all_insights = []
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            all_insights.extend(json.load(file))
    return all_insights

def build_vector_db():
    print("Finding all AI insights reports...")
    insights = get_all_insights()
        
    if not insights:
        print("Error: Insights file is empty.")
        return
        
    vector_db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "vector_db")
    os.makedirs(vector_db_dir, exist_ok=True)
    
    print(f"Initializing ChromaDB at {vector_db_dir}...")
    client = PersistentClient(path=vector_db_dir)
    
    print("Loading HuggingFace embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    collection = client.get_or_create_collection(name="ajio_insights")
    
    # We clear it to avoid mixing old and new schema
    try:
        client.delete_collection("ajio_insights")
        collection = client.create_collection(name="ajio_insights")
    except Exception:
        pass
    
    documents = []
    metadatas = []
    ids = []
    
    seen_hashes = set()
    
    # Pre-filter irrelevant records from the core clustering engine
    relevant_insights = [ins for ins in insights if ins.get('relevance_status') in ['RELEVANT', 'POSSIBLY_RELEVANT']]
    print(f"Embedding {len(relevant_insights)} relevant insights out of {len(insights)} total records...")
    
    for i, insight in enumerate(relevant_insights):
        # Embed the core observable problem for semantic clustering
        text_to_embed = insight.get('observed_problem_summary') or insight.get('original_text') or "Unknown problem"
        
        # Deduplication via source + source_id fingerprint
        fingerprint_key = f"{insight.get('source', '')}_{insight.get('source_id', '')}"
        if not insight.get('source_id'):
            import hashlib
            fingerprint_key = hashlib.sha256(text_to_embed.encode('utf-8')).hexdigest()
            
        if fingerprint_key in seen_hashes:
            continue
        seen_hashes.add(fingerprint_key)
        
        # Safely convert metadata to strings for ChromaDB compatibility
        metadata = {}
        for key in ["source", "source_type", "source_url", "source_id", "timestamp", "original_text", 
                    "relevance_status", "relevance_reason", "relevance_confidence",
                    "observed_problem_summary", "theme", "user_segment_clue", "wishlist_intent",
                    "why_saved", "conversion_blocker", "uncertainty", "workaround", 
                    "external_platform_used", "purchase_status", "evidence_strength"]:
            val = insight.get(key)
            if val is None:
                metadata[key] = ""
            elif isinstance(val, (int, float, bool, str)):
                metadata[key] = val
            else:
                metadata[key] = str(val)
                
        # Support fields
        for key in ["theme_support", "user_segment_clue_support", "wishlist_intent_support", 
                    "why_saved_support", "conversion_blocker_support", "uncertainty_support",
                    "workaround_support", "external_platform_used_support", "purchase_status_support"]:
            metadata[key] = str(insight.get(key, 'unknown'))
            
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
