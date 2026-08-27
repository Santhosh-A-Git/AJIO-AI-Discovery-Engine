import sqlite3
import os

db_path = os.path.join("data", "warehouse", "ajio_warehouse.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def print_count(label, query):
    cursor.execute(query)
    count = cursor.fetchone()[0]
    print(f"{label}: {count}")

print("--- DATA PIPELINE DIAGNOSTIC ---")
print_count("Raw records (total insights)", "SELECT count(*) FROM insights")
print_count("Unique records", "SELECT count(*) FROM insights WHERE duplicate_status = 'UNIQUE'")
print_count("Duplicate records", "SELECT count(*) FROM insights WHERE duplicate_status = 'DUPLICATE'")
print_count("AI analyzed", "SELECT count(*) FROM insights WHERE relevance_status IS NOT NULL")
print_count("Relevant", "SELECT count(*) FROM insights WHERE relevance_status = 'RELEVANT'")
print_count("Possibly relevant", "SELECT count(*) FROM insights WHERE relevance_status = 'POSSIBLY_RELEVANT'")
print_count("Not relevant", "SELECT count(*) FROM insights WHERE relevance_status = 'NOT_RELEVANT'")
print_count("User-generated", "SELECT count(*) FROM insights WHERE source_type = 'USER_GENERATED'")
print_count("Brand-generated", "SELECT count(*) FROM insights WHERE source_type = 'BRAND_GENERATED'")
print_count("Secondary-context", "SELECT count(*) FROM insights WHERE source_type = 'SECONDARY_CONTEXT'")
print_count("Clusters", "SELECT count(*) FROM clusters")

print("\n--- SCHEMA ---")
cursor.execute("PRAGMA table_info(insights)")
columns = [col['name'] for col in cursor.fetchall()]
print(f"Insights Columns: {columns}")

print("\n--- DELIVERY CLUSTER INVESTIGATION ---")
cursor.execute("SELECT cluster_id, cluster_name, prevalence FROM clusters ORDER BY prevalence DESC LIMIT 1")
top_cluster = cursor.fetchone()
if top_cluster:
    print(f"Top Cluster: {top_cluster['cluster_name']} (ID: {top_cluster['cluster_id']}) - Vol: {top_cluster['prevalence']}")
    cursor.execute('''
        SELECT source, source_type, relevance_status, wishlist_intent, conversion_blocker, purchase_status 
        FROM insights 
        WHERE cluster_id = ? 
        LIMIT 10
    ''', (top_cluster['cluster_id'],))
    
    rows = cursor.fetchall()
    for idx, row in enumerate(rows):
        print(f"  Record {idx+1}: Source={row['source']} | SourceType={row['source_type']} | Rel={row['relevance_status']} | Intent={row['wishlist_intent']} | Blocker={row['conversion_blocker']} | Status={row['purchase_status']}")
else:
    print("No clusters found.")

conn.close()
