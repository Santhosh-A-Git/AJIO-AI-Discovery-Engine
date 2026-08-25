import os
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup

def scrape_news(query="AJIO reviews"):
    """
    Scrapes Google News RSS for press mentions and articles about AJIO.
    """
    print(f"Scraping Google News RSS for '{query}'...")
    
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    scraped_data = []
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            for item in root.findall('.//item'):
                title = item.findtext('title')
                link = item.findtext('link')
                pub_date = item.findtext('pubDate')
                description = item.findtext('description')
                source = item.find('source').text if item.find('source') is not None else "News Source"
                
                # Parse HTML description to get clean text snippet
                clean_desc = ""
                if description:
                    soup = BeautifulSoup(description, 'html.parser')
                    clean_desc = soup.get_text(strip=True)
                
                scraped_data.append({
                    "source": "google_news",
                    "timestamp": pub_date or datetime.now().isoformat(),
                    "text": f"{title}\n{clean_desc}".strip(),
                    "author": source,
                    "metadata": {
                        "url": link
                    }
                })
        else:
            print(f"Google News RSS returned status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error scraping Google News RSS: {e}")
        
    print(f"Successfully scraped {len(scraped_data)} news articles.")
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
    data = scrape_news()
    save_to_raw_storage(data, "google_news")
