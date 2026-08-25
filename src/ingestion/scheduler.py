import time
from datetime import datetime   
# pyrefly: ignore [missing-import]
import schedule
# pyrefly: ignore [missing-import]
from playstore_scraper import scrape_playstore, save_to_raw_storage as save_playstore
# pyrefly: ignore [missing-import]
from youtube_scraper import scrape_youtube_comments, save_to_raw_storage as save_youtube
# pyrefly: ignore [missing-import]
from twitter_scraper import scrape_twitter, save_to_raw_storage as save_twitter
# pyrefly: ignore [missing-import]
from web_scraper import scrape_generic_web_reviews, save_to_raw_storage as save_web
# pyrefly: ignore [missing-import]
from news_scraper import scrape_news, save_to_raw_storage as save_news
# pyrefly: ignore [missing-import]
from search_scraper import scrape_search, save_to_raw_storage as save_search
# pyrefly: ignore [missing-import]
from queue_manager import QueueManager

def run_all_jobs():
    print(f"[{datetime.now()}] Starting full ingestion cycle...")
    qm = QueueManager()
    
    # 1. Google Play Store
    print("-> Triggering Play Store Scraper")
    playstore_data = scrape_playstore()
    save_playstore(playstore_data, "google_play_store")
    
    # 2. YouTube
    print("-> Triggering YouTube Scraper")
    youtube_data = scrape_youtube_comments()
    save_youtube(youtube_data, "youtube")
    
    # 3. Twitter
    print("-> Triggering Twitter Scraper")
    twitter_data = scrape_twitter()
    save_twitter(twitter_data, "twitter")
    
    # 4. Google News
    print("-> Triggering Google News Scraper")
    news_data = scrape_news()
    save_news(news_data, "google_news")
    
    # 5. Google Search Snippets
    print("-> Triggering Google Search Scraper")
    search_data = scrape_search()
    save_search(search_data, "web_search")
    qm.publish_batch(search_data)
    
    print("--- Ingestion Pipeline Finished ---")

if __name__ == "__main__":
    print("Running initial ingestion immediately...")
    run_all_jobs()
    
    print("Scheduling ingestion pipeline to run every 6 hours...")
    schedule.every(6).hours.do(run_all_jobs)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
