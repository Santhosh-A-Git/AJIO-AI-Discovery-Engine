import json
import os
import time
from datetime import datetime
# pyrefly: ignore [missing-import]
from google_play_scraper import Sort, reviews

def scrape_playstore(app_package='com.ril.ajio', count=1000):
    """
    Scrape reviews from the Google Play Store for the AJIO app.
    """
    print(f"Scraping {count} recent reviews for {app_package}...")
    try:
        result, continuation_token = reviews(
            app_package,
            lang='en', # Language
            country='in', # Country (India)
            sort=Sort.NEWEST, # Get newest reviews
            count=count
        )
        
        scraped_data = []
        for review in result:
            scraped_data.append({
                "source": "google_play_store",
                "timestamp": review.get('at').isoformat() if review.get('at') else datetime.now().isoformat(),
                "text": review.get('content'),
                "author": review.get('userName'),
                "rating": review.get('score'),
                "metadata": {
                    "thumbsUpCount": review.get('thumbsUpCount'),
                    "reviewId": review.get('reviewId')
                }
            })
            
        print(f"Successfully scraped {len(scraped_data)} reviews.")
        return scraped_data
        
    except Exception as e:
        print(f"Error scraping Play Store: {e}")
        return []

def save_to_raw_storage(data, source_name):
    if not data:
        return
        
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(raw_dir, f"{source_name}_{timestamp}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} items to {filename}")

if __name__ == "__main__":
    # Test run
    data = scrape_playstore (count=1000)
    save_to_raw_storage(data, "playstore")
