import os
import collections
# pyrefly: ignore [missing-import]
from chromadb import PersistentClient
from sklearn.cluster import HDBSCAN
# pyrefly: ignore [missing-import]
import numpy as np

def extract_keywords(insights):
    """Use AI to intelligently name a cluster based on its most prominent emergent theme."""
    import os
    # pyrefly: ignore [missing-import]
    from langchain_groq import ChatGroq
    # pyrefly: ignore [missing-import]
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Emergent Opportunity"
        
    # Sample up to 10 insights to avoid max token limits
    sample_texts = [ins['observed_problem_summary'] for ins in insights[:10]]
    combined_text = "\n- ".join(sample_texts)
    
    prompt = f"""You are a senior Product Manager. Review the following friction points collected from users and provide a SINGLE, very short (2 to 4 words max) precise name for this specific cluster of problems. Do not provide any explanation, just the exact name.
    
Frictions:
- {combined_text}

Name:"""

    try:
        model = ChatGroq(model_name="qwen/qwen3.8-27b", groq_api_key=api_key, temperature=0.1)
        response = model.invoke(prompt)
        name = response.content.strip().replace('"', '').replace('**', '')
        return name
    except Exception as e:
        print(f"Error naming cluster: {e}")
        return "Emergent Opportunity"

def run_clustering():
    vector_db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "vector_db")
    if not os.path.exists(vector_db_dir):
        print("Error: Vector DB not found.")
        return None
        
    print("Connecting to ChromaDB...")
    client = PersistentClient(path=vector_db_dir)
    collection = client.get_collection(name="ajio_insights")
    
    # Fetch all data
    data = collection.get(include=['embeddings', 'metadatas', 'documents'])
    
    if not len(data['embeddings']):
        print("No embeddings found in ChromaDB.")
        return None
        
    filtered_embeddings = []
    filtered_metadatas = []
    filtered_documents = []
    
    for emb, meta, doc in zip(data['embeddings'], data['metadatas'], data['documents']):
        if meta.get('relevance_status') in ['RELEVANT', 'POSSIBLY_RELEVANT']:
            filtered_embeddings.append(emb)
            filtered_metadatas.append(meta)
            filtered_documents.append(doc)
            
    if not filtered_embeddings:
        print("No RELEVANT embeddings found for clustering.")
        return None
        
    embeddings = np.array(filtered_embeddings)
    documents = filtered_documents
    metadatas = filtered_metadatas
    
    print(f"Loaded {len(embeddings)} RELEVANT vectors for clustering.")
    
    if len(embeddings) < 6:
        print("Not enough data to form 6 clusters.")
        return None
        
    print("Running KMeans clustering engine to discover exactly 6 emergent themes...")
    from sklearn.cluster import KMeans
    clusterer = KMeans(n_clusters=6, random_state=42)
    labels = clusterer.fit_predict(embeddings)
    
    print(f"Discovered 6 unique problem clusters.")
    
    # Group insights by cluster
    clustered_data = collections.defaultdict(list)
    for i, label in enumerate(labels):
        if label == -1:
            continue # Skip noise points (outliers)
            
        meta = metadatas[i]
        
        insight = {
            'observed_problem_summary': documents[i],
            'source': meta.get('source', ''),
            'source_type': meta.get('source_type', ''),
            'source_url': meta.get('source_url', ''),
            'source_id': meta.get('source_id', ''),
            'timestamp': meta.get('timestamp', ''),
            'original_text': meta.get('original_text', ''),
            'relevance_status': meta.get('relevance_status', ''),
            'relevance_reason': meta.get('relevance_reason', ''),
            'relevance_confidence': meta.get('relevance_confidence', 0),
            'theme': meta.get('theme') or meta.get('topic', 'Unknown Theme'),
            'user_segment_clue': meta.get('user_segment_clue', ''),
            'wishlist_intent': meta.get('wishlist_intent') or meta.get('intent', 'UNKNOWN'),
            'why_saved': meta.get('why_saved', ''),
            'conversion_blocker': meta.get('conversion_blocker') or meta.get('topic', 'UNKNOWN'),
            'uncertainty': meta.get('uncertainty', ''),
            'workaround': meta.get('workaround', ''),
            'external_platform_used': meta.get('external_platform_used', ''),
            'purchase_status': meta.get('purchase_status', ''),
            'evidence_strength': meta.get('evidence_strength', ''),
            'theme_support': meta.get('theme_support', ''),
            'user_segment_clue_support': meta.get('user_segment_clue_support', ''),
            'wishlist_intent_support': meta.get('wishlist_intent_support', ''),
            'why_saved_support': meta.get('why_saved_support', ''),
            'conversion_blocker_support': meta.get('conversion_blocker_support', ''),
            'uncertainty_support': meta.get('uncertainty_support', ''),
            'workaround_support': meta.get('workaround_support', ''),
            'external_platform_used_support': meta.get('external_platform_used_support', ''),
            'purchase_status_support': meta.get('purchase_status_support', '')
        }
        clustered_data[label].append(insight)
        
    # Format into a final list of clusters
    final_clusters = []
    for cluster_id, insights in clustered_data.items():
        cluster_name = extract_keywords(insights)
        final_clusters.append({
            'cluster_id': int(cluster_id),
            'cluster_name': cluster_name,
            'insights': insights
        })
        
    return final_clusters

if __name__ == "__main__":
    clusters = run_clustering()
    if clusters:
        for c in clusters[:3]:
            print(f"Cluster {c['cluster_id']} ({c['cluster_name']}) - {len(c['insights'])} insights")
