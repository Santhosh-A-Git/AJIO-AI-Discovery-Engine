import os
import collections
# pyrefly: ignore [missing-import]
from chromadb import PersistentClient
from sklearn.cluster import HDBSCAN
# pyrefly: ignore [missing-import]
import numpy as np

def extract_keywords(insights):
    """Simple heuristic to name a cluster based on the most common topic in the cluster."""
    topics = [insight['topic'] for insight in insights if 'topic' in insight]
    if topics:
        most_common = collections.Counter(topics).most_common(1)[0][0]
        return most_common
    return "Unknown Problem"

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
    
    embeddings = np.array(data['embeddings'])
    documents = data['documents']
    metadatas = data['metadatas']
    
    print(f"Loaded {len(embeddings)} vectors for clustering.")
    
    if len(embeddings) < 10:
        print("Not enough data to cluster.")
        return None
        
    print("Running HDBSCAN clustering engine...")
    # HDBSCAN parameters optimized for ~800 dense vectors
    clusterer = HDBSCAN(min_cluster_size=5, min_samples=2, metric='euclidean')
    labels = clusterer.fit_predict(embeddings)
    
    print(f"Discovered {len(set(labels)) - (1 if -1 in labels else 0)} unique problem clusters.")
    
    # Group insights by cluster
    clustered_data = collections.defaultdict(list)
    for i, label in enumerate(labels):
        if label == -1:
            continue # Skip noise points (outliers)
            
        insight = {
            'problem_statement': documents[i],
            'topic': metadatas[i].get('topic', ''),
            'intent': metadatas[i].get('intent', ''),
            'purchase_stage': metadatas[i].get('purchase_stage', ''),
            'source_review_id': metadatas[i].get('source_review_id', '')
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
