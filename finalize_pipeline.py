import os
import sys
import sqlite3
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

def finalize_pipeline():
    backup_path = os.path.join("data", "reports", "ai_insights_canonical.json")
    if not os.path.exists(backup_path):
        print("No canonical JSON found.")
        return
        
    with open(backup_path, 'r', encoding='utf-8') as f:
        all_extracted_insights = json.load(f)
        
    print(f"Loaded {len(all_extracted_insights)} fully extracted insights. Persisting to SQLite...")
    
    db_path = os.path.join("data", "warehouse", "ajio_warehouse.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
    
    print(f"Inserted {synced} records to DB.")
    
    # pyrefly: ignore [missing-import]
    import ai_engine.vector_store as vector_store
    # pyrefly: ignore [missing-import]
    import processing.clustering as clustering
    # pyrefly: ignore [missing-import]
    import processing.quantification as quantification
    
    print("Vectorizing...")
    vector_store.build_vector_db()
    
    print("Clustering (KMeans=6)...")
    clusters = clustering.run_clustering()
    print(f"Formed {len(clusters) if clusters else 0} clusters.")
    
    print("Quantifying and exporting...")
    quantification.score_and_export_clusters()
    
    print("SUCCESS!")

if __name__ == "__main__":
    finalize_pipeline()
