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

def normalize_text(text):
    return re.sub(r'\\s+', ' ', str(text).lower().strip())

def get_fingerprint(source, text, date_str, author=None):
    # Deterministic deduplication fingerprint if source_id is missing
    norm_text = normalize_text(text)
    raw_str = f"{source}_{norm_text}_{date_str}_{author}".encode('utf-8')
    return hashlib.sha256(raw_str).hexdigest()

def classify_source_type(source_platform, text, author):
    # Basic heuristic for source and author type classification
    source_platform = str(source_platform).lower()
    author = str(author).lower()
    
    if "ajio" in author or "support" in author or "official" in author:
        return "BRAND_GENERATED", "BRAND"
        
    if source_platform in ["google_play", "app_store", "twitter", "reddit", "facebook", "instagram", "youtube"]:
        return "USER_GENERATED", "USER"
        
    if source_platform in ["news", "blog", "article"]:
        return "SECONDARY_CONTEXT", "UNKNOWN"
        
    return "USER_GENERATED", "USER"

def deduplicate_records(raw_records):
    unique_map = {}
    processed = []
    
    raw_count = len(raw_records)
    unique_count = 0
    duplicate_count = 0
    
    for r in raw_records:
        source = r.get('source', 'unknown')
        source_id = r.get('id')
        author = r.get('author', '')
        text = r.get('text', '')
        date = r.get('date', '')
        
        # Primary identity
        if source_id:
            identity = f"{source}_{source_id}"
        else:
            # Fallback identity
            identity = get_fingerprint(source, text, date, author)
            
        r['_internal_id'] = identity
        
        if identity in unique_map:
            r['duplicate_status'] = "EXACT_DUPLICATE"
            r['duplicate_of'] = identity
            r['duplicate_confidence'] = 1.0
            duplicate_count += 1
        else:
            r['duplicate_status'] = "UNIQUE"
            r['duplicate_of'] = None
            r['duplicate_confidence'] = 0.0
            unique_map[identity] = True
            unique_count += 1
            
        processed.append(r)
        
    print(f"Deduplication Complete: {raw_count} Raw -> {unique_count} Unique, {duplicate_count} Exact Duplicates")
    return processed, unique_count, duplicate_count

def analyze_dataset(max_records=None, start_index=0, batch_size=5, resume=True):
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
        
    print(f"Loaded {len(data)} total records from dataset.")
    
    # Run Explicit Deduplication
    deduped_data, unique_count, duplicate_count = deduplicate_records(data)
    
    # Filter short reviews
    valid_records = [r for r in deduped_data if len(str(r.get('text', ''))) > 30]
    print(f"Selected {len(valid_records)} records with sufficient length.")
    
    if max_records:
        valid_records = valid_records[start_index:start_index+max_records]
    else:
        valid_records = valid_records[start_index:]
        
    print(f"Records Selected for Analysis: {len(valid_records)}")

    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # Resume functionality
    all_insights = []
    already_processed_ids = set()
    output_file = os.path.join(reports_dir, "ai_insights_canonical.json")
    
    if resume and os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                all_insights = json.load(f)
                already_processed_ids = {ins.get('source_id') for ins in all_insights if ins.get('source_id')}
            print(f"Resuming: Loaded {len(all_insights)} previously processed records.")
        except Exception as e:
            print(f"Failed to load resume file: {e}")
            
    # Filter out already processed unique IDs to prevent re-processing
    records_to_process = [r for r in valid_records if r['_internal_id'] not in already_processed_ids]
    
    print(f"Records Already Processed: {len(valid_records) - len(records_to_process)}")
    print(f"Records Newly Queued for Processing: {len(records_to_process)}")
    
def analyze_batch(chunk, meta_map, fallback_models, groq_api_key):
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
For every extracted field, output a paired `_support` field containing "SUPPORTED", "UNSUPPORTED", or "UNKNOWN" relative to the original evidence.

Output strictly in JSON format matching this schema:
{{
  "insights": [
    {{
      "original_id_ref": "The ID of the review provided in the input prompt",
      "relevance_status": "RELEVANT | POSSIBLY_RELEVANT | NOT_RELEVANT",
      "relevance_reason": "Why is this relevant or not?",
      "relevance_confidence": 0.9,
      
      "observed_problem_summary": "Traceable summary/justification of the exact friction",
      "theme": "Emergent semantic cluster label (e.g. Price Volatility, Fit Uncertainty, Delivery)",
      "theme_support": "Traceability justification for derived theme",
      
      "user_segment_clue": "e.g. Price-sensitive, High intent, Trend-seeker",
      "user_segment_clue_support": "SUPPORTED|UNSUPPORTED|UNKNOWN",
      
      "wishlist_intent": "SELF_PURCHASE | DEFERRED_PURCHASE | COMPARISON | BOOKMARKING | EXPLORATION | GIFTING | SHARING | RECOMMENDATION_DRIVEN | UNKNOWN | OTHER",
      "wishlist_intent_support": "SUPPORTED|UNSUPPORTED|UNKNOWN",
      
      "why_saved": "Why did the user save this?",
      "why_saved_support": "SUPPORTED|UNSUPPORTED|UNKNOWN",
      
      "conversion_blocker": "PRICE_VALUE | FIT_SIZE | QUALITY | REVIEWS_SOCIAL_PROOF | STYLING | OCCASION | COMPARISON | AVAILABILITY | DELIVERY | RETURNS_EXCHANGE | BUDGET_TIMING | DECISION_OVERLOAD | TRUST | LACK_OF_URGENCY | APP_FRICTION | UNKNOWN | OTHER",
      "conversion_blocker_support": "SUPPORTED|UNSUPPORTED|UNKNOWN",
      
      "uncertainty": "What is the user unsure about? (e.g. size accuracy, value)",
      "uncertainty_support": "SUPPORTED|UNSUPPORTED|UNKNOWN",
      
      "workaround": "What did they do instead? (e.g. abandon, external check)",
      "workaround_support": "SUPPORTED|UNSUPPORTED|UNKNOWN",
      
      "external_platform_used": "Any competitors/platforms mentioned (e.g. YouTube, Myntra, Amazon, None)",
      "external_platform_used_support": "SUPPORTED|UNSUPPORTED|UNKNOWN",
      
      "purchase_status": "PURCHASED | NOT_PURCHASED | DELAYED | ABANDONED | REMOVED | BOUGHT_ELSEWHERE | UNKNOWN",
      "purchase_status_support": "SUPPORTED|UNSUPPORTED|UNKNOWN",
      
      "evidence_strength": "HIGH | MEDIUM | LOW (High=Direct statement, Low=AI inference)",
      "evidence_strength_reason": "Reasoning for the evidence strength score"
    }}
  ]
}}

Batch of Reviews:
{reviews_batch}
"""
    reviews_str = ""
    for r_id in meta_map:
        source_platform = meta_map[r_id]['source']
        author = meta_map[r_id]['author_type']
        text = meta_map[r_id]['original_text']
        reviews_str += f"[{r_id}] Source: {source_platform}\nAuthor: {author}\nText: {text}\n\n"
        
    # Loop infinitely until one model succeeds or we hard-fail on something non-retryable
    # We will iterate through fallback models, and if all hit rate limits, we sleep and try again.
    while True:
        for model_name in fallback_models:
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
                # Use a very generous timeout of 60 seconds to ensure models finish generation
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                if response.status_code == 200:
                    result_json = json.loads(response.json()['choices'][0]['message']['content'])
                    insights = result_json.get('insights', [])
                    
                    # Re-attach original provenance metadata
                    for ins in insights:
                        r_id = ins.get('original_id_ref')
                        if r_id in meta_map:
                            ins.update(meta_map[r_id])
                    print(f" -> {model_name} extracted {len(insights)} insights.")
                    return insights
                elif response.status_code == 429:
                    print(f" -> {model_name} rate limited (429). Trying next model...")
                else:
                    print(f" -> {model_name} failed ({response.status_code}): {response.text}")
            except requests.exceptions.Timeout:
                print(f" -> {model_name} request timed out. Generating this batch might be slow. Trying next model...")
            except Exception as e:
                print(f" -> {model_name} request failed: {e}")
                
        # If we exhausted all fallback models (usually due to a global Groq rate limit)
        # We MUST NOT use mock data. We MUST wait and try again.
        print(f" -> ALL MODELS EXHAUSTED for this batch. Sleeping 65 seconds to clear Groq rate limits, then retrying same batch...")
        time.sleep(65)

def analyze_dataset(max_records=None, start_index=0, batch_size=5, resume=True):
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
        
    print(f"Loaded {len(data)} total records from dataset.")
    
    # Run Explicit Deduplication
    deduped_data, unique_count, duplicate_count = deduplicate_records(data)
    
    # Filter short reviews
    valid_records = [r for r in deduped_data if len(str(r.get('text', ''))) > 30]
    print(f"Selected {len(valid_records)} records with sufficient length.")
    
    if max_records:
        valid_records = valid_records[start_index:start_index+max_records]
    else:
        valid_records = valid_records[start_index:]
        
    print(f"Records Selected for Analysis: {len(valid_records)}")

    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # Resume functionality
    all_insights = []
    already_processed_ids = set()
    output_file = os.path.join(reports_dir, "ai_insights_canonical.json")
    
    if resume and os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                all_insights = json.load(f)
                already_processed_ids = {ins.get('source_id') for ins in all_insights if ins.get('source_id')}
            print(f"Resuming: Loaded {len(all_insights)} previously processed records.")
        except Exception as e:
            print(f"Failed to load resume file: {e}")
            
    # Filter out already processed unique IDs to prevent re-processing
    records_to_process = [r for r in valid_records if r['_internal_id'] not in already_processed_ids]
    
    print(f"Records Already Processed: {len(valid_records) - len(records_to_process)}")
    print(f"Records Newly Queued for Processing: {len(records_to_process)}")
    
    chunks = list(chunk_data(records_to_process, chunk_size=batch_size))
    fallback_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "allam-2-7b"]
    records_failed = 0
    records_processed = 0

    for i, chunk in enumerate(chunks):
        print(f"Processing Batch {i+1}/{len(chunks)}...")
        meta_map = {}
        for idx, r in enumerate(chunk):
            r_id = f"REV_{idx}"
            source_platform = r.get('source', 'unknown')
            source_type, author_type = classify_source_type(source_platform, r.get('text', ''), r.get('author', ''))
            
            meta_map[r_id] = {
                "source": source_platform,
                "source_type": source_type,
                "author_type": author_type,
                "source_url": r.get('url', ''),
                "source_id": r['_internal_id'],
                "timestamp": r.get('date', ''),
                "original_text": r.get('text', ''),
                "duplicate_status": r.get('duplicate_status'),
                "duplicate_of": r.get('duplicate_of'),
                "duplicate_confidence": r.get('duplicate_confidence')
            }
            
        insights = analyze_batch(chunk, meta_map, fallback_models, groq_api_key)
        
        if insights:
            all_insights.extend(insights)
            records_processed += len(insights)
        else:
            print(f" -> ALL FALLBACK MODELS FAILED for batch {i+1}. Sleeping 60s...")
            records_failed += len(chunk)
            time.sleep(60)
            
        # Save incrementally
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_insights, f, indent=2, ensure_ascii=False)
            
        time.sleep(1) # Minor delay to avoid hammering API
        
    print(f"\n--- AI Analysis Complete ---")
    print(f"Raw Records: {len(data)}")
    print(f"Records Selected for Analysis: {len(valid_records)}")
    print(f"Records Already Processed: {len(valid_records) - len(records_to_process)}")
    print(f"Records Newly Processed: {records_processed}")
    print(f"Records Failed: {records_failed}")
    print(f"Final data saved to: {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AJIO Discovery Engine - AI Analyzer")
    parser.add_argument("--max_records", type=int, default=None, help="Max records to process")
    parser.add_argument("--start_index", type=int, default=0, help="Start index")
    parser.add_argument("--batch_size", type=int, default=5, help="Batch size for LLM")
    parser.add_argument("--no_resume", action="store_true", help="Disable resume from existing output")
    args = parser.parse_args()
    
    analyze_dataset(
        max_records=args.max_records, 
        start_index=args.start_index, 
        batch_size=args.batch_size, 
        resume=not args.no_resume
    )
