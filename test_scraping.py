"""
Test script for ntscraper (Nitter Scraper).
"""
from ntscraper import Nitter
import json

def test_scraping():
    print("🔍 Initializing Nitter scraper...")
    scraper = Nitter()
    
    hashtag = "ایران"
    print(f"📡 Searching for #{hashtag}...")
    
    try:
        # Scrape tweets
        tweets = scraper.get_tweets(hashtag, mode='hashtag', number=5)
        
        if 'tweets' in tweets and tweets['tweets']:
            print(f"\n✅ Success! Found {len(tweets['tweets'])} tweets:\n")
            for i, tweet in enumerate(tweets['tweets'], 1):
                print(f"{i}. @{tweet['user']['username']}")
                print(f"   {tweet['text'][:100]}...")
                print(f"   ❤️ {tweet['stats']['likes']} 🔄 {tweet['stats']['retweets']} 💬 {tweet['stats']['comments']}")
                print("-" * 40)
        else:
            print("\n❌ No tweets found or empty response.")
            print(f"Response: {tweets}")
            
    except Exception as e:
        print(f"\n❌ Error scraping: {e}")

if __name__ == "__main__":
    test_scraping()
