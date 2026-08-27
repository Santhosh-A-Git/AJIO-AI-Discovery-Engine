import os
import sys
import sqlite3
import json
import time
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
# pyrefly: ignore [missing-import]
from ai_engine.analyzer import analyze_batch

def run_real_pipeline():
    print("--- 1. PREPARING DATABASE ---")
    db_path = os.path.join("data", "warehouse", "ajio_warehouse.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    dataset_path = os.path.join("data", "cleansed", "clean_dataset.json")
    if not os.path.exists(dataset_path):
        print("Cleansed dataset not found.")
        return
        
    with open(dataset_path, 'r', encoding='utf-8') as f:
        raw_records = json.load(f)
        
    print(f"Loaded {len(raw_records)} raw records from dataset.")
    
    print("\n--- 2. (SKIPPED) DATABASE CLEARING DEFERRED UNTIL AI EXTRACTION COMPLETES ---")
    
    print("\n--- 3. RUNNING REAL AI EXTRACTION (Handling rate limits robustly) ---")
    all_extracted_insights = []
    batch_size = 5
    total_batches = (len(raw_records) + batch_size - 1) // batch_size
    
    i = 0
    batch_num = 1
    while i < len(raw_records):
        batch = raw_records[i:i+batch_size]
        
        meta_map = {}
        for idx, r in enumerate(batch):
            r_id = r.get('source_id') or r.get('id') or f"ref_{i+idx}"
            meta_map[r_id] = {
                'source': r.get('source', 'unknown'),
                'author_type': r.get('author_type', 'USER'),
                'original_text': r.get('text', ''),
                'source_type': 'USER_GENERATED',
                'timestamp': r.get('timestamp', ''),
                'source_url': r.get('source_url', '')
            }
            
        print(f"Processing batch {batch_num}/{total_batches}...")
        try:
            groq_key = os.getenv("GROQ_API_KEY")
            
            # Use GPT-OSS 120b and 20b as primary models, Qwen as a backup.
            batch_result = analyze_batch(batch, meta_map, ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"], groq_key)
            
            if batch_result:
                all_extracted_insights.extend(batch_result)
                
                # (Deferred SQLite insertion until end of script to keep UI populated)
                # Incrementally save to JSON to prevent data loss
                backup_path = os.path.join("data", "reports", "ai_insights_canonical.json")
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(all_extracted_insights, f, indent=2)
                
                i += batch_size
                batch_num += 1
            else:
                print(" -> Unknown failure (empty batch_result). Retrying...")
                time.sleep(30)
                # i is NOT incremented, loop retries same batch
        except Exception as e:
            print(f" -> Critical Error on batch: {e}. Sleeping 60s and retrying...")
            time.sleep(60)
            # i is NOT incremented, loop retries same batch
            
    print(f"Successfully extracted {len(all_extracted_insights)} canonical insights natively via AI.")
    
    backup_path = os.path.join("data", "reports", "ai_insights_canonical.json")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(all_extracted_insights, f, indent=2)
    
    print("\n--- 4. PERSISTING TO SQLITE ---")
    print("Clearing old records from database...")
    cursor.execute("DELETE FROM insights")
    cursor.execute("DELETE FROM clusters")
    conn.commit()
    
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
            ins.get('original_id_ref') or ins.get('source_id'), ins.get('timestamp'), ins.get('original_text'), ins.get('relevance_status'),
            ins.get('relevance_reason'), ins.get('relevance_confidence'), ins.get('observed_problem_summary'),
            ins.get('theme'), ins.get('user_segment_clue'), ins.get('wishlist_intent'), ins.get('why_saved'),
            ins.get('conversion_blocker'), ins.get('uncertainty'), ins.get('workaround'), ins.get('external_platform_used'),
            ins.get('purchase_status'), ins.get('evidence_strength'), ins.get('duplicate_status', 'UNIQUE')
        ))
        synced += 1
    conn.commit()
    conn.close()
    print(f"Inserted {synced} fully scored, canonical records to SQLite.")
    
    print("\n--- 5. RUNNING CLUSTERING (HDBSCAN on RELEVANT records) ---")
    # pyrefly: ignore [missing-import]
    import ai_engine.vector_store as vector_store
    # pyrefly: ignore [missing-import]
    import processing.clustering as clustering
    # pyrefly: ignore [missing-import]
    import processing.quantification as quantification
    
    print("Vectorizing...")
    vector_store.build_vector_db()
    
    print("Clustering...")
    clusters = clustering.run_clustering()
    if clusters is None:
        clusters = []
    print(f"Formed {len(clusters)} clusters.")
        
    print("\n--- 6. RUNNING QUANTIFICATION (6-Component Formula) ---")
    quantification.score_and_export_clusters()
    
    print("\nDONE! Pipeline successfully executed on real data.")

if __name__ == "__main__":
    run_real_pipeline()
