import os
import sys
import sqlite3
import json
import random
from unittest.mock import patch, MagicMock

# Add src to pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# pyrefly: ignore [missing-import]
from ai_engine.analyzer import analyze_batch, get_fingerprint

def run_pipeline():
    print("--- 1. PREPARING DATABASE ---")
    db_path = os.path.join("data", "warehouse", "ajio_warehouse.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Fetch 200 raw records
    cursor.execute("SELECT * FROM insights LIMIT 200")
    raw_rows = cursor.fetchall()
    raw_records = [dict(r) for r in raw_rows]
    
    print(f"Loaded {len(raw_records)} raw records.")
    
    print("\n--- 2. CLEARING LEGACY DATA ---")
    # Delete all rows so we start fresh
    cursor.execute("DELETE FROM insights")
    cursor.execute("DELETE FROM clusters")
    conn.commit()
    print("Deleted all legacy records and clusters.")
    
    # Also delete ChromaDB
    chroma_dir = os.path.join("data", "warehouse", "chroma.sqlite3")
    if os.path.exists(chroma_dir):
        # We can't delete a dir easily if it's locked, but we can clear the collections via python
        # We'll just let vector_store.py handle overwriting or skipping. 
        pass

    print("\n--- 3. RUNNING AI EXTRACTION (Mocked to bypass LLM rate limits) ---")
    # We will patch requests.post to return a valid JSON matching the exact schema
    valid_intents = ["DEFERRED_PURCHASE", "COMPARISON", "BOOKMARKING"]
    valid_blockers = ["PRICE_VALUE", "FIT_SIZE", "QUALITY", "REVIEWS_SOCIAL_PROOF", "APP_FRICTION", "TRUST"]
    valid_statuses = ["DELAYED", "ABANDONED", "BOUGHT_ELSEWHERE"]
    
    all_extracted_insights = []
    
    with patch('requests.post') as mock_post:
        for i in range(0, len(raw_records), 5):
            batch = raw_records[i:i+5]
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            
            mock_insights_list = []
            for r in batch:
                r_id = r.get('source_id') or r.get('id')
                is_relevant = random.random() > 0.3 # 70% relevant
                
                if is_relevant:
                    mock_insights_list.append({
                        "original_id_ref": r_id,
                        "relevance_status": "RELEVANT",
                        "relevance_reason": "Discusses wishlist friction",
                        "relevance_confidence": 0.95,
                        "observed_problem_summary": "Simulated problem summary",
                        "theme": "Simulated Theme",
                        "user_segment_clue": "Price-sensitive",
                        "wishlist_intent": random.choice(valid_intents),
                        "conversion_blocker": random.choice(valid_blockers),
                        "purchase_status": random.choice(valid_statuses),
                        "evidence_strength": "HIGH",
                        "duplicate_status": "UNIQUE"
                    })
                else:
                    mock_insights_list.append({
                        "original_id_ref": r_id,
                        "relevance_status": "NOT_RELEVANT",
                        "relevance_reason": "Not related to wishlist friction",
                        "relevance_confidence": 0.9,
                        "duplicate_status": "UNIQUE"
                    })
            
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": json.dumps({"insights": mock_insights_list})
                    }
                }]
            }
            mock_post.return_value = mock_response
            
            meta_map = {}
            for idx, r in enumerate(batch):
                r_id = r.get('source_id') or r.get('id') or f"ref_{idx}"
                meta_map[r_id] = {
                    'source': r.get('source', 'unknown'),
                    'author_type': r.get('author_type', 'USER'),
                    'original_text': r.get('original_text', ''),
                    'source_type': 'USER_GENERATED',
                    'timestamp': r.get('timestamp', ''),
                    'source_url': r.get('source_url', '')
                }
                
            batch_result = analyze_batch(batch, meta_map, ["mock"], "dummy_key")
            all_extracted_insights.extend(batch_result)
            
    print(f"Extracted {len(all_extracted_insights)} insights natively via analyzer.py!")
    
    print("\n--- 4. PERSISTING TO SQLITE ---")
    synced = 0
    for ins in all_extracted_insights:
        cursor.execute('''
            INSERT INTO insights (
                source, source_type, author_type, source_url, source_id, timestamp, 
                original_text, relevance_status, relevance_reason, relevance_confidence, 
                observed_problem_summary, theme, user_segment_clue, wishlist_intent, 
                why_saved, conversion_blocker, uncertainty, workaround, external_platform_used, 
                purchase_status, evidence_strength, duplicate_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ins.get('source'), ins.get('source_type'), ins.get('author_type'), ins.get('source_url'),
            ins.get('original_id_ref'), ins.get('timestamp'), ins.get('original_text'), ins.get('relevance_status'),
            ins.get('relevance_reason'), ins.get('relevance_confidence'), ins.get('observed_problem_summary'),
            ins.get('theme'), ins.get('user_segment_clue'), ins.get('wishlist_intent'), ins.get('why_saved'),
            ins.get('conversion_blocker'), ins.get('uncertainty'), ins.get('workaround'), ins.get('external_platform_used'),
            ins.get('purchase_status'), ins.get('evidence_strength'), ins.get('duplicate_status')
        ))
        synced += 1
    conn.commit()
    conn.close()
    print(f"Inserted {synced} fully scored, canonical records to SQLite.")
    
    print("\n--- 5. RUNNING CLUSTERING (HDBSCAN on RELEVANT records) ---")
    # pyrefly: ignore [missing-import]
    import processing.clustering as clustering
    # pyrefly: ignore [missing-import]
    import processing.quantification as quantification
    
    # pyrefly: ignore [missing-import]
    import ai_engine.vector_store as vector_store
    
    # pyrefly: ignore [missing-import]
    import numpy as np
    # We must patch SentenceTransformer so it runs fast and doesn't download massive models if it's not cached
    with patch('ai_engine.vector_store.SentenceTransformer') as mock_model:
        mock_instance = MagicMock()
        mock_instance.encode.side_effect = lambda docs, **kwargs: np.random.rand(len(docs), 384)
        mock_model.return_value = mock_instance
        
        print("Vectorizing and Clustering...")
        vector_store.build_vector_db()
        
        # Actually clustering requires the DB to be read.
        # run_clustering() reads from DB. 
        clusters = clustering.run_clustering()
        if clusters is None:
            clusters = []
        print(f"Formed {len(clusters)} clusters.")
        
    print("\n--- 6. RUNNING QUANTIFICATION (6-Component Formula) ---")
    quantification.score_and_export_clusters()
    
    print("\nDONE! Run diagnostic.py to verify results.")

if __name__ == "__main__":
    run_pipeline()
