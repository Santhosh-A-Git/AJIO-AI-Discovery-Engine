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
        
    # Setup Vector DB directory
    vector_db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "vector_db")
    os.makedirs(vector_db_dir, exist_ok=True)
    
    print(f"Initializing ChromaDB at {vector_db_dir}...")
    client = PersistentClient(path=vector_db_dir)
    
    # We use a custom embedding function so we can use sentence-transformers locally
    print("Loading HuggingFace embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Create or get collection
    collection = client.get_or_create_collection(name="ajio_insights")
    
    print(f"Embedding and storing {len(insights)} insights into ChromaDB...")
    
    # Batch add to Chroma
    documents = []
    metadatas = []
    ids = []
    embeddings = []
    
    seen_hashes = set()
    
    for i, insight in enumerate(insights):
        # We embed the problem statement directly as it holds the most semantic meaning for clustering
        text_to_embed = insight.get('problem_statement', '')
        
        import hashlib
        unique_hash = hashlib.md5(text_to_embed.encode('utf-8')).hexdigest()
        
        if unique_hash in seen_hashes:
            continue
        seen_hashes.add(unique_hash)
        
        # We store the rest as metadata
        metadata = {
            "topic": insight.get('topic', ''),
            "intent": insight.get('intent', ''),
            "purchase_stage": insight.get('purchase_stage', ''),
            "source_review_id": str(insight.get('source_review_id', ''))
        }
        
        documents.append(text_to_embed)
        metadatas.append(metadata)
        import hashlib
        unique_hash = hashlib.md5(text_to_embed.encode('utf-8')).hexdigest()
        ids.append(f"insight_{unique_hash}")
        
    # Generate embeddings natively
    embeddings_list = model.encode(documents, show_progress_bar=True)
    embeddings = embeddings_list.tolist()
    
    # Upsert to ChromaDB
    collection.upsert(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"Successfully vectorized and stored {len(insights)} insights in ChromaDB!")
    print(f"Vector Database ready at: {vector_db_dir}")

if __name__ == "__main__":
    build_vector_db()
