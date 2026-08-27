import os
import json
import time
import requests
import re
import hashlib
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

def chunk_data(data, chunk_size=5):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def get_fingerprint(source, text, date_str):
    # Deterministic deduplication fingerprint if source_id is missing
    raw_str = f"{source}_{text}_{date_str}".encode('utf-8')
    return hashlib.sha256(raw_str).hexdigest()

def analyze_dataset():
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY not found in .env")
        return
        
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "cleansed", "clean_dataset.json")
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}")
        return
        
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} total records. Filtering out very short reviews (< 30 chars)...")
    detailed_reviews = [r for r in data if len(r.get('text', '')) > 30]
    print(f"Selected {len(detailed_reviews)} reviews for deep AI analysis.")

    all_insights = []
    # Batch size 5 to keep tokens low, allowing room for massive JSON outputs
    chunks = list(chunk_data(detailed_reviews, chunk_size=5))[40:42] # Testing a small chunk first
    
    print(f"Processing {len(chunks)} batches through Groq API Cascade...")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    prompt_template = """You are an elite Product Manager analyzing raw user feedback for AJIO.
Your goal is to extract evidence specifically concerning why users who save/wishlist fashion products fail to convert that interest into a purchase.

First, determine if the review is RELEVANT, POSSIBLY_RELEVANT, or NOT_RELEVANT to the Wishlist-to-Purchase journey.
If it is NOT_RELEVANT, you still output the object but leave the analytical fields blank.
If RELEVANT or POSSIBLY_RELEVANT, extract the exact canonical evidence. Do NOT hallucinate. 
For every extracted field, output a paired `_support` field containing "supported", "unsupported", or "unknown" relative to the original evidence.

Output strictly in JSON format matching this schema:
{{
  "insights": [
    {{
      "original_id_ref": "The ID of the review provided in the input prompt",
      "relevance_status": "RELEVANT | POSSIBLY_RELEVANT | NOT_RELEVANT",
      "relevance_reason": "Why is this relevant or not?",
      "relevance_confidence": 0.9,
      "observed_problem_summary": "Traceable summary/justification of the exact friction",
      "theme": "Emergent semantic cluster label (e.g. Price, Fit, Delivery, Capacity)",
      "theme_support": "supported|unsupported|unknown",
      "user_segment_clue": "e.g. Price-sensitive, High intent, Trend-seeker",
      "user_segment_clue_support": "supported|unsupported|unknown",
      "wishlist_intent": "SELF_PURCHASE | DEFERRED_PURCHASE | COMPARISON | BOOKMARKING | EXPLORATION | GIFTING | SHARING | RECOMMENDATION_DRIVEN | UNKNOWN | OTHER",
      "wishlist_intent_support": "supported|unsupported|unknown",
      "why_saved": "Why did the user save this?",
      "why_saved_support": "supported|unsupported|unknown",
      "conversion_blocker": "PRICE_VALUE | FIT_SIZE | QUALITY | REVIEWS_SOCIAL_PROOF | STYLING | OCCASION | COMPARISON | AVAILABILITY | DELIVERY | RETURNS_EXCHANGE | BUDGET_TIMING | DECISION_OVERLOAD | TRUST | LACK_OF_URGENCY | UNKNOWN | OTHER",
      "conversion_blocker_support": "supported|unsupported|unknown",
      "uncertainty": "What is the user unsure about?",
      "uncertainty_support": "supported|unsupported|unknown",
      "workaround": "What did they do instead? (e.g. abandon, external check)",
      "workaround_support": "supported|unsupported|unknown",
      "external_platform_used": "Any competitors/platforms mentioned",
      "external_platform_used_support": "supported|unsupported|unknown",
      "purchase_status": "PURCHASED | NOT_PURCHASED | DELAYED | ABANDONED | REMOVED | UNKNOWN",
      "purchase_status_support": "supported|unsupported|unknown",
      "evidence_strength": "HIGH | MEDIUM | LOW (High=Direct statement, Low=AI inference)"
    }}
  ]
}}

Batch of Reviews:
{reviews_batch}
"""

    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    output_file = os.path.join(reports_dir, f"ai_insights_FULL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    fallback_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "allam-2-7b"]

    for i, chunk in enumerate(chunks):
        print(f"Processing Batch {i+1}/{len(chunks)}...")
        reviews_str = ""
        # Store metadata mapping to rejoin after LLM output
        meta_map = {}
        for idx, r in enumerate(chunk):
            r_id = f"REV_{idx}"
            source_id = r.get('id') or get_fingerprint(r.get('source', 'unknown'), r.get('text', ''), r.get('date', ''))
            meta_map[r_id] = {
                "source": r.get('source'),
                "source_type": "USER_GENERATED" if r.get('source') in ['google_play', 'twitter'] else "SECONDARY_CONTEXT",
                "source_url": r.get('url', ''),
                "source_id": source_id,
                "timestamp": r.get('date', ''),
                "original_text": r.get('text', '')
            }
            reviews_str += f"[{r_id}] Source: {r.get('source')}\nText: {r.get('text')}\n\n"
            
        success = False
        
        for model_name in fallback_models:
            if success:
                break
                
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a product manager. Always output valid JSON."},
                    {"role": "user", "content": prompt_template.format(reviews_batch=reviews_str)}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    result_json = json.loads(response.json()['choices'][0]['message']['content'])
                    insights = result_json.get('insights', [])
                    
                    # Re-attach original provenance metadata
                    for ins in insights:
                        r_id = ins.get('original_id_ref')
                        if r_id in meta_map:
                            ins.update(meta_map[r_id])
                            all_insights.append(ins)
                            
                    print(f" -> {model_name} extracted {len(insights)} insights.")
                    success = True
                elif response.status_code == 429:
                    print(f" -> {model_name} rate limited. Falling back...")
                else:
                    print(f" -> {model_name} failed ({response.status_code}): {response.text}")
            except Exception as e:
                print(f" -> {model_name} request failed: {e}")
                
        if not success:
            print(f" -> ALL FALLBACK MODELS FAILED for batch {i+1}. Sleeping 60s...")
            time.sleep(60)
            
        # Save incrementally
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_insights, f, indent=2, ensure_ascii=False)
            
        time.sleep(2) # Minor delay to avoid hammering API
        
    print(f"\n--- AI Analysis Complete ---")
    print(f"Successfully generated {len(all_insights)} structured insights.")
    print(f"Final data saved to: {output_file}")

if __name__ == "__main__":
    analyze_dataset()
