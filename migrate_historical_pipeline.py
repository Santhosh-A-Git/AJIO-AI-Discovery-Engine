import os
import json
import sqlite3

def migrate_old_insights():
    db_path = os.path.join("data", "warehouse", "ajio_warehouse.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM insights")
    cursor.execute("DELETE FROM clusters")
    conn.commit()
    print("Database cleared.")

    paths = [
        "data/reports/ai_insights_FULL_20260826_091754.json",
        "data/reports/ai_insights_FULL_20260824_224713.json"
    ]
    
    migrated_insights = []
    
    for path in paths:
        if not os.path.exists(path):
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            
        for idx, row in enumerate(old_data):
            insight = {
                'source': 'historical_migration',
                'source_type': 'USER_GENERATED',
                'author_type': 'USER',
                'source_url': '',
                'source_id': f"{row.get('source_review_id', 'unknown_id')}_{idx}_{len(migrated_insights)}",
                'timestamp': '',
                'original_text': row.get('problem_statement', ''),
                'relevance_status': 'RELEVANT',
                'relevance_reason': 'Migrated from historical insights',
                'relevance_confidence': 1.0,
                'observed_problem_summary': row.get('problem_statement', ''),
                'theme': row.get('topic', 'Unknown Theme'),
                'user_segment_clue': '',
                'wishlist_intent': row.get('intent', 'UNKNOWN'),
                'why_saved': '',
                'conversion_blocker': row.get('topic', 'UNKNOWN'),
                'uncertainty': '',
                'workaround': '',
                'external_platform_used': '',
                'purchase_status': row.get('purchase_stage', 'UNKNOWN'),
                'evidence_strength': 'HIGH',
                'duplicate_status': 'UNIQUE'
            }
            migrated_insights.append(insight)
            
    print(f"Migrated {len(migrated_insights)} records.")
    
    # Insert to DB
    for ins in migrated_insights:
        cursor.execute('''
            INSERT INTO insights (
                source, source_type, author_type, source_url, source_id, timestamp, 
                original_text, relevance_status, relevance_reason, relevance_confidence, 
                observed_problem_summary, theme, user_segment_clue, wishlist_intent, 
                why_saved, conversion_blocker, uncertainty, workaround, external_platform_used, 
                purchase_status, evidence_strength, duplicate_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ins['source'], ins['source_type'], ins['author_type'], ins['source_url'],
            ins['source_id'], ins['timestamp'], ins['original_text'], ins['relevance_status'],
            ins['relevance_reason'], ins['relevance_confidence'], ins['observed_problem_summary'],
            ins['theme'], ins['user_segment_clue'], ins['wishlist_intent'], ins['why_saved'],
            ins['conversion_blocker'], ins['uncertainty'], ins['workaround'], ins['external_platform_used'],
            ins['purchase_status'], ins['evidence_strength'], ins['duplicate_status']
        ))
        
    conn.commit()
    conn.close()
    
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    # pyrefly: ignore [missing-import]
    import ai_engine.vector_store as vector_store
    # pyrefly: ignore [missing-import]
    import processing.clustering as clustering
    # pyrefly: ignore [missing-import]
    import processing.quantification as quantification
    
    vector_store.build_vector_db()
    clusters = clustering.run_clustering()
    if clusters is None:
        clusters = []
    print(f"Formed {len(clusters)} clusters.")
    quantification.score_and_export_clusters()
    print("Done!")

if __name__ == "__main__":
    migrate_old_insights()
