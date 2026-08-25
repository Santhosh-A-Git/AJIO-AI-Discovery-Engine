import os
import json
import requests
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

def scrape_search(query="AJIO customer complaints and reviews"):
    """
    Scrapes Google Search snippets via SerpApi for generalized web sentiment and reviews.
    """
    print(f"Scraping Google Search via SerpApi for '{query}'...")
    
    api_key = os.getenv('SERPAPI_API_KEY')
    if not api_key or api_key == 'your_serpapi_key_here':
        print("Error: SerpApi credentials missing from .env file.")
        return []

    url = f"https://serpapi.com/search.json?engine=google&q={query}&num=100&api_key={api_key}"
    scraped_data = []
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get('organic_results', [])
            
            for result in results:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                source = result.get('source', 'Web Site')
                link = result.get('link', '')
                
                if title or snippet:
                    scraped_data.append({
                        "source": "web_search",
                        "timestamp": datetime.now().isoformat(),
                        "text": f"{title}\n{snippet}".strip(),
                        "author": source,
                        "metadata": {
                            "url": link,
                            "position": result.get('position', 0)
                        }
                    })
        else:
            print(f"SerpApi Google Search returned status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error scraping Google Search via SerpApi: {e}")
        
    print(f"Successfully scraped {len(scraped_data)} web snippets.")
    return scraped_data

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
    data = scrape_search()
    save_to_raw_storage(data, "web_search")
