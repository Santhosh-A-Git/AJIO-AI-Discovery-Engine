import os
import json
import time
import requests
import re
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

def chunk_data(data, chunk_size=10):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

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
    # Batch size 10 to keep tokens low. Skip the first 40 batches (already processed).
    chunks = list(chunk_data(detailed_reviews, chunk_size=10))[40:]
    
    print(f"Processing {len(chunks)} batches through Groq API...")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    prompt_template = """You are an expert Product Manager analyzing a batch of raw user reviews for the AJIO app.
Your goal is to extract deep, actionable insights and identify user friction points.

Extract up to 1-2 key insights per review if they mention a clear problem or feature request. 
If a review is generic (e.g. "nice app"), skip it.

Output strictly in JSON format matching this schema:
{{
  "insights": [
    {{
      "topic": "Main category (e.g., Size, Fit, Quality, Delivery, App UX)",
      "problem_statement": "Exact user friction described",
      "intent": "e.g., High Purchase Intent, Frustration, General Feedback",
      "purchase_stage": "e.g., Pre-purchase, Checkout, Post-purchase",
      "source_review_id": "The first 5 words of the review text"
    }}
  ]
}}

Batch of Reviews:
{reviews_batch}
"""

    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    output_file = os.path.join(reports_dir, f"ai_insights_FULL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    for i, chunk in enumerate(chunks):
        print(f"Processing Batch {i+1}/{len(chunks)}...")
        reviews_str = ""
        for idx, r in enumerate(chunk):
            reviews_str += f"Review {idx+1} [Source: {r['source']}]: {r['text']}\n"
            
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "system", "content": "You are a product manager. Always output valid JSON."},
                {"role": "user", "content": prompt_template.format(reviews_batch=reviews_str)}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }
            
        success = False
        retries = 0
        while not success and retries < 3:
            try:
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    result_json = json.loads(response.json()['choices'][0]['message']['content'])
                    insights = result_json.get('insights', [])
                    all_insights.extend(insights)
                    print(f" -> Extracted {len(insights)} insights.")
                    success = True
                else:
                    error_text = response.text
                    print(f" -> Error {response.status_code}: {error_text}")
                    if response.status_code == 429:
                        # Try to extract the sleep time from the error message, default 60s
                        sleep_time = 60
                        match = re.search(r'try again in (\d+\.?\d*)s', error_text)
                        if match:
                            sleep_time = float(match.group(1)) + 5 # Add 5s buffer
                        print(f" -> Rate limit hit! Sleeping for {sleep_time} seconds...")
                        time.sleep(sleep_time)
                        retries += 1
                    elif response.status_code == 400:
                        print(" -> Bad Request. Skipping batch.")
                        break # Skip this batch
                    else:
                        time.sleep(10)
                        retries += 1
            except Exception as e:
                print(f" -> Request failed: {e}")
                time.sleep(10)
                retries += 1
                
        # Save incrementally
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_insights, f, indent=2, ensure_ascii=False)
            
        # Base sleep between requests to respect 8000 TPM limit
        time.sleep(45)
        
    print(f"\n--- AI Analysis Complete ---")
    print(f"Successfully generated {len(all_insights)} structured insights.")
    print(f"Final data saved to: {output_file}")

if __name__ == "__main__":
    analyze_dataset()
