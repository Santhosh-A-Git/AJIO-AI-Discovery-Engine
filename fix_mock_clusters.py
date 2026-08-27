import sqlite3
import random
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
# pyrefly: ignore [missing-import]
from src.ai_engine import vector_store
# pyrefly: ignore [missing-import]
from src.processing import clustering
# pyrefly: ignore [missing-import]
from src.processing import quantification

def fix_clusters():
    dataset_path = os.path.join("data", "cleansed", "clean_dataset.json")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        raw_records = json.load(f)
        
    text_map = {}
    for r in raw_records:
        r_id = r.get('source_id') or r.get('id')
        if r_id:
            text_map[r_id] = r.get('text', '')
            
    db_path = os.path.join("data", "warehouse", "ajio_warehouse.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, source_id, original_text FROM insights")
    rows = cursor.fetchall()
    
    themes = ["Fit Issues", "Price Volatility", "Delivery Delay", "Quality Concerns", "Trust & Validation", "App Friction"]
    blockers = ["FIT_SIZE", "PRICE_VALUE", "DELIVERY", "QUALITY", "REVIEWS_SOCIAL_PROOF", "APP_FRICTION"]
    
    print(f"Fixing {len(rows)} mock insights...")
    for row_id, source_id, db_text in rows:
        theme = random.choice(themes)
        idx = themes.index(theme)
        blocker = blockers[idx]
        
        actual_text = text_map.get(source_id, db_text)
        
        snippet = (actual_text[:100] + "...") if actual_text and len(actual_text) > 100 else (actual_text or "General problem")
        
        cursor.execute("""
            UPDATE insights 
            SET observed_problem_summary = ?, theme = ?, conversion_blocker = ?, original_text = ?
            WHERE id = ?
        """, (snippet, theme, blocker, actual_text, row_id))
        
    conn.commit()
    print("Fixed SQLite.")
    
    print("Running Vectorizer...")
    vector_store.build_vector_db()
    
    print("Running Clustering...")
    clusters = clustering.run_clustering()
    print(f"Formed {len(clusters) if clusters else 0} clusters.")
    
    print("Running Quantification...")
    quantification.score_and_export_clusters()
    
    print("DONE!")

if __name__ == "__main__":
    fix_clusters()
