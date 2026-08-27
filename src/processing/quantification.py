import os
import sqlite3
import collections

from clustering import run_clustering

def calc_relevance_norm(insights):
    score = 0
    valid = 0
    high_intent = ['SELF_PURCHASE', 'DEFERRED_PURCHASE', 'COMPARISON']
    med_intent = ['BOOKMARKING', 'EXPLORATION', 'GIFTING', 'SHARING', 'RECOMMENDATION_DRIVEN']
    for ins in insights:
        intent = ins.get('wishlist_intent', '').upper()
        if intent in high_intent:
            score += 100
        elif intent in med_intent:
            score += 50
        else:
            score += 10
        valid += 1
    return score / valid if valid > 0 else 0

def calc_evidence_strength_norm(insights):
    total_score = 0
    valid = 0
    for ins in insights:
        ev_strength = ins.get('evidence_strength', '').upper()
        if ev_strength == 'HIGH':
            total_score += 100
        elif ev_strength == 'MEDIUM':
            total_score += 60
        else:
            total_score += 20
        valid += 1
    return total_score / valid if valid > 0 else 0

def calc_severity_norm(insights):
    # Evidence-grounded severity based on observable consequences
    # e.g., ABANDONED, DELAYED purchase status implies higher severity
    # or severe conversion blockers
    score = 0
    valid = 0
    for ins in insights:
        status = ins.get('purchase_status', '').upper()
        if status in ['ABANDONED', 'REMOVED']:
            score += 100
        elif status == 'DELAYED':
            score += 70
        else:
            # Fallback to blocker if status isn't severe
            blocker = ins.get('conversion_blocker', '').upper()
            high_sev = ['PRICE_VALUE', 'FIT_SIZE', 'QUALITY', 'TRUST', 'AVAILABILITY', 'BUDGET_TIMING']
            if blocker in high_sev:
                score += 80
            else:
                score += 40
        valid += 1
    return score / valid if valid > 0 else 0

def calc_cross_source_norm(insights):
    # Unique source categories (e.g., Reddit vs Google Play)
    sources = set()
    for ins in insights:
        src = ins.get('source', '').lower()
        if src:
            sources.add(src)
    count = len(sources)
    if count >= 3:
        return 100
    elif count == 2:
        return 66
    elif count == 1:
        return 33
    return 0

def calc_segment_concentration_norm(insights):
    segments = [ins.get('user_segment_clue', '').strip() for ins in insights]
    segments = [s for s in segments if s and s.lower() not in ['unknown', 'none', 'n/a', '']]
    
    # If there is insufficient segment evidence, return a neutral score
    if len(segments) < max(2, len(insights) * 0.1): 
        return 30
        
    most_common = collections.Counter(segments).most_common(1)
    if not most_common:
        return 30
    
    ratio = most_common[0][1] / len(segments)
    if ratio > 0.5:
        return 100
    if ratio > 0.3:
        return 60
    return 30

def score_and_export_clusters():
    print("Initiating Quantification Engine...")
    
    clusters = run_clustering()
    if not clusters:
        print("No clusters to quantify.")
        return
        
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "warehouse", "ajio_warehouse.db")
    if not os.path.exists(db_path):
        print("Error: Database not initialized. Please run sync_to_sqlite.py first.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Calculate global max prevalence for normalization
    # The denominator is total unique relevant user observations
    cursor.execute("SELECT count(*) FROM insights WHERE duplicate_status = 'UNIQUE' AND relevance_status = 'RELEVANT' AND source_type = 'USER_GENERATED'")
    total_relevant_user_obs = cursor.fetchone()[0]
    
    if total_relevant_user_obs == 0:
        total_relevant_user_obs = 1 # fallback to avoid div by zero
        
    print(f"Calculating Weighted Opportunity Scores based on {total_relevant_user_obs} total relevant user observations...")
    
    cursor.execute('DELETE FROM clusters')
    
    total_insights_synced = 0
    
    for cluster in clusters:
        insights = cluster['insights']
        
        # 1. Prevalence (25%) - Only unique, relevant, user-generated observations
        user_gen_insights = [ins for ins in insights if ins.get('source_type') == 'USER_GENERATED']
        prevalence = len(user_gen_insights)
        prev_norm = (prevalence / total_relevant_user_obs) * 100
        
        # 2. Wishlist-Conversion Relevance (25%)
        rel_norm = calc_relevance_norm(insights)
        
        # 3. Evidence Strength (15%)
        ev_norm = calc_evidence_strength_norm(insights)
        
        # 4. Severity (15%)
        sev_norm = calc_severity_norm(insights)
        
        # 5. Cross-Source Consistency (10%)
        cross_norm = calc_cross_source_norm(insights)
        
        # 6. Segment Concentration (10%)
        seg_norm = calc_segment_concentration_norm(insights)
        
        # Total Weighted Score
        score = (prev_norm * 0.25) + (rel_norm * 0.25) + (ev_norm * 0.15) + (sev_norm * 0.15) + (cross_norm * 0.10) + (seg_norm * 0.10)
        
        cursor.execute('''
            INSERT INTO clusters (
                cluster_id, cluster_name, prevalence, prevalence_norm, intent_relevance_norm, 
                severity_norm, cross_source_norm, segment_concentration_norm, evidence_strength_norm, opportunity_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cluster['cluster_id'], cluster['cluster_name'], prevalence, prev_norm, rel_norm, 
            sev_norm, cross_norm, seg_norm, ev_norm, score
        ))
        
        # Update canonical database with cluster assignments
        for ins in insights:
            cursor.execute('''
                UPDATE insights 
                SET cluster_id = ? 
                WHERE source_id = ?
            ''', (cluster['cluster_id'], ins.get('source_id')))
            total_insights_synced += 1
            
    conn.commit()
    conn.close()
    
    print(f"\n--- Quantification Complete ---")
    print(f"Successfully processed {len(clusters)} clusters and updated {total_insights_synced} canonical records in the warehouse.")

if __name__ == "__main__":
    score_and_export_clusters()
