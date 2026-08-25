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
        intent_relevance REAL,
        severity REAL,
        opportunity_score REAL
    )
    ''')
    
    # Create Insights Table (Linked to Clusters)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cluster_id INTEGER,
        topic TEXT,
        problem_statement TEXT,
        intent TEXT,
        purchase_stage TEXT,
        source_review_id TEXT,
        FOREIGN KEY (cluster_id) REFERENCES clusters (cluster_id)
    )
    ''')
    
    # We clear the tables if they exist so we can run the pipeline fresh
    cursor.execute('DELETE FROM clusters')
    cursor.execute('DELETE FROM insights')
    
    conn.commit()
    conn.close()
    print("Database tables initialized successfully.")
    
    return db_path

if __name__ == "__main__":
    setup_database()
