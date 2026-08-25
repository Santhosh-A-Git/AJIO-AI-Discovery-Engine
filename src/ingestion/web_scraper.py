import os
import json
import requests
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_generic_web_reviews(url):
    """
    A generic scraper utilizing BeautifulSoup to parse standard review sites.
    This example specifically targets a mock structure representing Mouthshut or Trustpilot.
    """
    print(f"Scraping generic web reviews from {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} from {url}")
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # NOTE: This parsing logic is generic and would need to be tuned for specific sites (e.g., Trustpilot structure).
        # We look for common review wrapper classes.
        review_elements = soup.find_all('div', class_=['review', 'review-card', 'customer-review', 'review-article'])
        
        if not review_elements:
            print("Error: No review elements found with standard CSS classes.")
            return []

        scraped_data = []
        for element in review_elements:
            text_el = element.find(['p', 'div'], class_=['review-text', 'content', 'more', 'reviewdata'])
            author_el = element.find(['span', 'h4', 'div', 'a'], class_=['author', 'name', 'user-ms-name'])
            
            scraped_data.append({
                "source": "web_reviews",
                "timestamp": datetime.now().isoformat(),
                "text": text_el.get_text(strip=True) if text_el else "No text found",
                "author": author_el.get_text(strip=True) if author_el else "Anonymous",
                "metadata": {
                    "source_url": url
                }
            })
            
        print(f"Successfully scraped {len(scraped_data)} web reviews.")
        return scraped_data

    except Exception as e:
        print(f"Error scraping web url {url}: {e}")
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
    data = scrape_generic_web_reviews("https://www.mouthshut.com/product-reviews/Ajio-com-reviews-925893043")
    save_to_raw_storage(data, "web_reviews")
