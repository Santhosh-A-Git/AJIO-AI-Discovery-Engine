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
    support_keys = [
        "theme_support", "user_segment_clue_support", "wishlist_intent_support", 
        "why_saved_support", "conversion_blocker_support", "uncertainty_support",
        "workaround_support", "external_platform_used_support", "purchase_status_support"
    ]
    total_score = 0
    valid = 0
    for ins in insights:
        sup_count = 0
        total_eval = 0
        for k in support_keys:
            val = ins.get(k, 'unknown').lower()
            if val == 'supported':
                sup_count += 1
                total_eval += 1
            elif val == 'unsupported':
                total_eval += 1
        
        # Base it off explicit evidence_strength field too
        ev_strength = ins.get('evidence_strength', '').upper()
        base = 50
        if ev_strength == 'HIGH':
            base = 100
        elif ev_strength == 'LOW':
            base = 20
            
        field_acc = (sup_count / total_eval * 100) if total_eval > 0 else 50
        total_score += (base * 0.5) + (field_acc * 0.5)
        valid += 1
    return total_score / valid if valid > 0 else 0

def calc_severity_norm(insights):
    high_sev = ['PRICE_VALUE', 'FIT_SIZE', 'QUALITY', 'TRUST', 'AVAILABILITY', 'BUDGET_TIMING']
    med_sev = ['DELIVERY', 'RETURNS_EXCHANGE', 'DECISION_OVERLOAD']
    score = 0
    valid = 0
    for ins in insights:
        blocker = ins.get('conversion_blocker', '').upper()
        if blocker in high_sev:
            score += 100
        elif blocker in med_sev:
            score += 70
        else:
            score += 40
        valid += 1
    return score / valid if valid > 0 else 0

def calc_cross_source_norm(insights):
    sources = set()
    for ins in insights:
        src = ins.get('source', '')
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
    segments = [s for s in segments if s and s.lower() not in ['unknown', 'none', 'n/a']]
    if not segments:
        return 30 # Uniform / Unknown
    
    most_common = collections.Counter(segments).most_common(1)
    if not most_common:
        return 30
    
    ratio = most_common[0][1] / len(insights)
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
        print("Error: Database not initialized. Please run db_setup.py first.")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Calculating Weighted Opportunity Scores and syncing to SQLite Warehouse...")
    
    cursor.execute('DELETE FROM insights')
    cursor.execute('DELETE FROM clusters')
    
    total_insights_synced = 0
    
    # Calculate global max prevalence for normalization
    max_prevalence = max([len(c['insights']) for c in clusters]) if clusters else 1
    
    for cluster in clusters:
        insights = cluster['insights']
        
        # 1. Prevalence (25%)
        prevalence = len(insights)
        prev_norm = (prevalence / max_prevalence) * 100
        
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
        
        for ins in insights:
            cursor.execute('''
                INSERT INTO insights (
                    cluster_id, source, source_type, source_url, source_id, timestamp, 
                    original_text, relevance_status, relevance_reason, relevance_confidence, 
                    observed_problem_summary, theme, user_segment_clue, wishlist_intent, 
                    why_saved, conversion_blocker, uncertainty, workaround, external_platform_used, 
                    purchase_status, evidence_strength, theme_support, user_segment_clue_support, 
                    wishlist_intent_support, why_saved_support, conversion_blocker_support, 
                    uncertainty_support, workaround_support, external_platform_used_support, purchase_status_support
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cluster['cluster_id'], ins.get('source'), ins.get('source_type'), ins.get('source_url'),
                ins.get('source_id'), ins.get('timestamp'), ins.get('original_text'), ins.get('relevance_status'),
                ins.get('relevance_reason'), ins.get('relevance_confidence'), ins.get('observed_problem_summary'),
                ins.get('theme'), ins.get('user_segment_clue'), ins.get('wishlist_intent'), ins.get('why_saved'),
                ins.get('conversion_blocker'), ins.get('uncertainty'), ins.get('workaround'), ins.get('external_platform_used'),
                ins.get('purchase_status'), ins.get('evidence_strength'), ins.get('theme_support'),
                ins.get('user_segment_clue_support'), ins.get('wishlist_intent_support'), ins.get('why_saved_support'),
                ins.get('conversion_blocker_support'), ins.get('uncertainty_support'), ins.get('workaround_support'),
                ins.get('external_platform_used_support'), ins.get('purchase_status_support')
            ))
            total_insights_synced += 1
            
    conn.commit()
    conn.close()
    
    print(f"\n--- Quantification Complete ---")
    print(f"Successfully processed {len(clusters)} clusters and synced {total_insights_synced} canonical records to the warehouse.")

if __name__ == "__main__":
    score_and_export_clusters()
