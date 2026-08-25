import os
import json
import requests
from datetime import datetime
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

def scrape_youtube_comments(video_ids=None):
    """
    Scrapes comments from a list of YouTube video IDs (e.g., fashion haul videos).
    """
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key or api_key == 'your_youtube_api_key_here':
        print("Error: YouTube API credentials not found or invalid in .env file.")
        return []

    if video_ids is None:
        print("No video IDs provided. Searching for 'AJIO fashion haul review'...")
        search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=AJIO+fashion+haul+review&type=video&maxResults=20&key={api_key}"
        try:
            search_res = requests.get(search_url)
            search_data = search_res.json()
            video_ids = [item['id']['videoId'] for item in search_data.get('items', [])]
            print(f"Found videos: {video_ids}")
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            video_ids = []
        


    scraped_data = []
    
    for video_id in video_ids:
        print(f"Scraping YouTube comments for video {video_id}...")
        url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults=100&key={api_key}"
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Error from YouTube API: {response.text}")
                continue
                
            data = response.json()
            items = data.get('items', [])
            
            for item in items:
                comment = item['snippet']['topLevelComment']['snippet']
                scraped_data.append({
                    "source": "youtube",
                    "timestamp": comment.get('publishedAt'),
                    "text": comment.get('textOriginal'),
                    "author": comment.get('authorDisplayName'),
                    "metadata": {
                        "videoId": video_id,
                        "likeCount": comment.get('likeCount')
                    }
                })
                
        except Exception as e:
            print(f"Error scraping YouTube: {e}")

    print(f"Successfully scraped {len(scraped_data)} YouTube comments.")
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
    # Test run
    data = scrape_youtube_comments()
    save_to_raw_storage(data, "youtube")
