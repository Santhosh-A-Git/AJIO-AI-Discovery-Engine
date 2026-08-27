import sqlite3
import os

def setup_database():
    db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "warehouse")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "ajio_warehouse.db")
    
    print(f"Initializing SQLite Database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Clusters Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clusters (
        cluster_id INTEGER PRIMARY KEY,
        cluster_name TEXT,
        prevalence INTEGER,
        prevalence_norm REAL,
        intent_relevance_norm REAL,
        severity_norm REAL,
        cross_source_norm REAL,
        segment_concentration_norm REAL,
        evidence_strength_norm REAL,
        opportunity_score REAL
    )
    ''')
    
    # Create Insights Table (Canonical Evidence Record)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cluster_id INTEGER,
        source TEXT,
        source_type TEXT,
        source_url TEXT,
        source_id TEXT,
        timestamp TEXT,
        original_text TEXT,
        relevance_status TEXT,
        relevance_reason TEXT,
        relevance_confidence REAL,
        observed_problem_summary TEXT,
        theme TEXT,
        user_segment_clue TEXT,
        wishlist_intent TEXT,
        why_saved TEXT,
        conversion_blocker TEXT,
        uncertainty TEXT,
        workaround TEXT,
        external_platform_used TEXT,
        purchase_status TEXT,
        evidence_strength TEXT,
        theme_support TEXT,
        user_segment_clue_support TEXT,
        wishlist_intent_support TEXT,
        why_saved_support TEXT,
        conversion_blocker_support TEXT,
        uncertainty_support TEXT,
        workaround_support TEXT,
        external_platform_used_support TEXT,
        purchase_status_support TEXT,
        FOREIGN KEY (cluster_id) REFERENCES clusters (cluster_id)
    )
    ''')
    
    # We clear the tables if they exist so we can run the pipeline fresh
    cursor.execute('DROP TABLE IF EXISTS clusters')
    cursor.execute('DROP TABLE IF EXISTS insights')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clusters (
        cluster_id INTEGER PRIMARY KEY,
        cluster_name TEXT,
        prevalence INTEGER,
        prevalence_norm REAL,
        intent_relevance_norm REAL,
        severity_norm REAL,
        cross_source_norm REAL,
        segment_concentration_norm REAL,
        evidence_strength_norm REAL,
        opportunity_score REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cluster_id INTEGER,
        source TEXT,
        source_type TEXT,
        source_url TEXT,
        source_id TEXT,
        timestamp TEXT,
        original_text TEXT,
        relevance_status TEXT,
        relevance_reason TEXT,
        relevance_confidence REAL,
        observed_problem_summary TEXT,
        theme TEXT,
        user_segment_clue TEXT,
        wishlist_intent TEXT,
        why_saved TEXT,
        conversion_blocker TEXT,
        uncertainty TEXT,
        workaround TEXT,
        external_platform_used TEXT,
        purchase_status TEXT,
        evidence_strength TEXT,
        theme_support TEXT,
        user_segment_clue_support TEXT,
        wishlist_intent_support TEXT,
        why_saved_support TEXT,
        conversion_blocker_support TEXT,
        uncertainty_support TEXT,
        workaround_support TEXT,
        external_platform_used_support TEXT,
        purchase_status_support TEXT,
        FOREIGN KEY (cluster_id) REFERENCES clusters (cluster_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")
    
    return db_path

if __name__ == "__main__":
    setup_database()
