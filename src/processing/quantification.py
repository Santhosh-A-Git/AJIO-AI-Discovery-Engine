import os
import sqlite3

from clustering import run_clustering

# High-friction keywords mapped to a Severity Multiplier
SEVERITY_KEYWORDS = {
    'high': ['uninstall', 'fraud', 'scam', 'refund', 'worst', 'hate', 'terrible', 'never buy', 'pathetic', 'stuck', 'money lost', 'fake'],
    'medium': ['slow', 'bug', 'crash', 'annoying', 'bad', 'fix', 'error', 'late', 'delay', 'issue', 'not working']
}

def calculate_severity(text):
    text_lower = text.lower()
    for kw in SEVERITY_KEYWORDS['high']:
        if kw in text_lower:
            return 1.5
    for kw in SEVERITY_KEYWORDS['medium']:
        if kw in text_lower:
            return 1.0
    return 0.5

def is_high_intent(intent_text):
    text_lower = intent_text.lower()
    # If the user is trying to checkout, purchase, or expects a refund, they are high intent
    intent_keywords = ['purchase', 'buy', 'checkout', 'cart', 'order', 'refund', 'money']
    return any(kw in text_lower for kw in intent_keywords)

def score_and_export_clusters():
    print("Initiating Quantification Engine...")
    
    clusters = run_clustering()
    if not clusters:
        print("No clusters to quantify.")
        return
        
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "warehouse", "ajio_warehouse.db")
    if not os.path.exists(db_path):
        print("Error: Database not initialized. Please run db_setup.py first.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Calculating Opportunity Scores and syncing to SQLite Warehouse...")
    
    # Clear existing data so we don't hit UNIQUE constraint errors on re-runs
    cursor.execute('DELETE FROM insights')
    cursor.execute('DELETE FROM clusters')
    
    total_insights_synced = 0
    
    for cluster in clusters:
        insights = cluster['insights']
        
        # 1. Prevalence (Volume)
        prevalence = len(insights)
        
        # 2. Intent Relevance (Ratio of high intent vs total)
        high_intent_count = sum(1 for ins in insights if is_high_intent(ins['intent']))
        intent_ratio = (high_intent_count / prevalence) if prevalence > 0 else 0
        # Prevent the score from being wiped out by setting a minimum baseline of 0.2
        intent_relevance = max(0.2, intent_ratio)
        
        # 3. Severity (Average severity of problems in the cluster)
        total_severity = sum(calculate_severity(ins['problem_statement']) for ins in insights)
        avg_severity = (total_severity / prevalence) if prevalence > 0 else 0.5
        
        # 4. Opportunity Score Calculation
        opportunity_score = prevalence * intent_relevance * avg_severity
        
        # Insert Cluster
        cursor.execute('''
            INSERT INTO clusters (cluster_id, cluster_name, prevalence, intent_relevance, severity, opportunity_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (cluster['cluster_id'], cluster['cluster_name'], prevalence, intent_relevance, avg_severity, opportunity_score))
        
        # Insert Linked Insights
        for ins in insights:
            cursor.execute('''
                INSERT INTO insights (cluster_id, topic, problem_statement, intent, purchase_stage, source_review_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                cluster['cluster_id'], 
                ins['topic'], 
                ins['problem_statement'], 
                ins['intent'], 
                ins['purchase_stage'], 
                ins['source_review_id']
            ))
            total_insights_synced += 1
            
    conn.commit()
    conn.close()
    
    print(f"\n--- Quantification Complete ---")
    print(f"Successfully processed {len(clusters)} clusters and synced {total_insights_synced} insights to the warehouse.")
    print("Run verification to see top ranked problems!")

if __name__ == "__main__":
    score_and_export_clusters()
