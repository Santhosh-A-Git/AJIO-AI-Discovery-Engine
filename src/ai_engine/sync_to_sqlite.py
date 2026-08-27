import os
import json
import sqlite3
import glob

def sync():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "warehouse", "ajio_warehouse.db")
    if not os.path.exists(db_path):
        print("Database not found. Run db_setup.py first.")
        return
        
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "reports")
    files = glob.glob(os.path.join(reports_dir, "ai_insights_canonical.json"))
    
    if not files:
        print("No ai_insights_canonical.json found.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # We will use source_id or internal id for unique constraint.
    # To avoid complex upsert, we check if it exists based on source_id or duplicate_of.
    # Actually, we will just sync based on source_id.
    
    with open(files[0], 'r', encoding='utf-8') as file:
        all_insights = json.load(file)
        
    print(f"Loaded {len(all_insights)} insights from canonical JSON.")
    
    synced = 0
    for ins in all_insights:
        source_id = ins.get('source_id')
        
        # Check if exists
        cursor.execute('SELECT id FROM insights WHERE source_id = ?', (source_id,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute('''
                INSERT INTO insights (
                    source, source_type, author_type, source_url, source_id, timestamp, 
                    original_text, relevance_status, relevance_reason, relevance_confidence, 
                    observed_problem_summary, theme, user_segment_clue, wishlist_intent, 
                    why_saved, conversion_blocker, uncertainty, workaround, external_platform_used, 
                    purchase_status, evidence_strength, evidence_strength_reason, theme_support, user_segment_clue_support, 
                    wishlist_intent_support, why_saved_support, conversion_blocker_support, 
                    uncertainty_support, workaround_support, external_platform_used_support, purchase_status_support,
                    duplicate_status, duplicate_of, duplicate_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ins.get('source'), ins.get('source_type'), ins.get('author_type'), ins.get('source_url'),
                source_id, ins.get('timestamp'), ins.get('original_text'), ins.get('relevance_status'),
                ins.get('relevance_reason'), ins.get('relevance_confidence'), ins.get('observed_problem_summary'),
                ins.get('theme'), ins.get('user_segment_clue'), ins.get('wishlist_intent'), ins.get('why_saved'),
                ins.get('conversion_blocker'), ins.get('uncertainty'), ins.get('workaround'), ins.get('external_platform_used'),
                ins.get('purchase_status'), ins.get('evidence_strength'), ins.get('evidence_strength_reason'), ins.get('theme_support'),
                ins.get('user_segment_clue_support'), ins.get('wishlist_intent_support'), ins.get('why_saved_support'),
                ins.get('conversion_blocker_support'), ins.get('uncertainty_support'), ins.get('workaround_support'),
                ins.get('external_platform_used_support'), ins.get('purchase_status_support'),
                ins.get('duplicate_status'), ins.get('duplicate_of'), ins.get('duplicate_confidence')
            ))
            synced += 1
            
    conn.commit()
    conn.close()
    
    print(f"Successfully synced {synced} NEW records to SQLite canonical evidence database.")

if __name__ == "__main__":
    sync()
