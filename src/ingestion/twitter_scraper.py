import os
import json
from datetime import datetime
# pyrefly: ignore [missing-import]
from apify_client import ApifyClient
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

def scrape_twitter(query='AJIO', limit=50):
    """
    Scrapes recent tweets matching a specific query using Apify.
    """
    apify_token = os.getenv('APIFY_API_TOKEN')

    if not apify_token or apify_token == 'your_apify_api_token_here':
        print("Error: Apify API token not found or invalid in .env file. Please add it to scrape real data.")
        return []

    print(f"Scraping Twitter (via Apify) for query '{query}'...")
    try:
        client = ApifyClient(apify_token)

        # Prepare the Actor input for apify/twitter-scraper or similar free/freemium actor
        run_input = {
            "searchTerms": [query],
            "maxItems": limit,
            "sort": "Latest"
        }

        # Run the Actor (apify/twitter-scraper) and wait for it to finish
        # Alternatively, we could use microworlds/twitter-scraper which is highly reliable
        run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)

        scraped_data = []
        default_dataset_id = getattr(run, 'defaultDatasetId', None) or getattr(run, 'default_dataset_id', None)
        if default_dataset_id:
            for item in client.dataset(default_dataset_id).iterate_items():
                scraped_data.append({
                    "source": "twitter",
                    "timestamp": item.get("createdAt", datetime.now().isoformat()),
                    "text": item.get("full_text") or item.get("text", ""),
                    "author": item.get("user", {}).get("screen_name", "unknown_user"),
                    "metadata": {
                        "tweet_id": item.get("id_str"),
                        "retweet_count": item.get("retweet_count", 0),
                        "like_count": item.get("favorite_count", 0)
                    }
                })

        print(f"Successfully scraped {len(scraped_data)} tweets via Apify.")
        return scraped_data

    except Exception as e:
        print(f"Error scraping Twitter via Apify: {e}")
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
    data = scrape_twitter(limit=10)
    save_to_raw_storage(data, "twitter")
