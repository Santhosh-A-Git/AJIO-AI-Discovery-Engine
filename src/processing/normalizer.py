import os
import json
import hashlib
from datetime import datetime
from cleaner import process_text

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw')
CLEANSED_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'cleansed')

def generate_id(source, text):
    """Generates a unique hash based on source and text to deduplicate."""
    hash_input = f"{source}_{text}".encode('utf-8')
    return hashlib.md5(hash_input).hexdigest()

def normalize_and_clean_data():
    """
    Reads all raw JSON files, normalizes schemas, scrubs PII, removes duplicates,
    and writes to a single cleansed dataset.
    """
    os.makedirs(CLEANSED_DATA_DIR, exist_ok=True)
    
    if not os.path.exists(RAW_DATA_DIR):
        print(f"No raw data directory found at {RAW_DATA_DIR}")
        return

    seen_hashes = set()
    normalized_records = []
    
    # Iterate over all JSON files in the raw directory
    for filename in os.listdir(RAW_DATA_DIR):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(RAW_DATA_DIR, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in data:
                # Basic validation
                text = item.get('text', '')
                source = item.get('source', 'unknown')
                
                if not text:
                    continue
                    
                # 1. Clean and Scrub Text
                safe_text = process_text(text)
                if not safe_text:
                    continue # Skip if text is empty after cleaning
                
                # 2. Deduplication
                record_hash = generate_id(source, safe_text)
                if record_hash in seen_hashes:
                    continue
                seen_hashes.add(record_hash)
                
                # 3. Normalize Schema
                normalized_record = {
                    "id": record_hash,
                    "source": source,
                    "timestamp": item.get('timestamp', datetime.now().isoformat()),
                    "text": safe_text,
                    "author": item.get('author', 'anonymous'),
                    "metadata": item.get('metadata', {})
                }
                
                normalized_records.append(normalized_record)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    # Write normalized data to cleansed directory
    output_file = os.path.join(CLEANSED_DATA_DIR, 'clean_dataset.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalized_records, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully processed and normalized {len(normalized_records)} unique records.")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    normalize_and_clean_data()
