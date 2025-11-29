"""
X (Twitter) API client for searching hashtags and posting tweets.
"""

import tweepy
from typing import List, Optional
from datetime import datetime
from config import Config
from models import Post


class XClient:
    """Client for interacting with X (Twitter) API."""
    
    def __init__(self):
        """Initialize X API client with credentials from config."""
        # Authenticate with X API v2
        self.client = tweepy.Client(
            consumer_key=Config.X_API_KEY,
            consumer_secret=Config.X_API_SECRET,
            access_token=Config.X_ACCESS_TOKEN,
            access_token_secret=Config.X_ACCESS_TOKEN_SECRET
        )
    
    def get_top_posts(self, hashtag: str, limit: int = 10) -> List[Post]:
        """
        Get top posts for a hashtag using scraping (Free Tier).
        
        Args:
            hashtag: Hashtag to search for
            limit: Number of top posts to return (default: 10)
        
        Returns:
            List of Post objects sorted by engagement score
        """
        # Ensure hashtag starts with #
        if not hashtag.startswith('#'):
            hashtag = f'#{hashtag}'
        
        posts = []
        
        try:
            print(f"🔍 Scraping top posts for {hashtag}...")
            from ntscraper import Nitter
            scraper = Nitter(log_level=1, skip_instance_check=False)
            
            # Scrape more tweets to ensure we get enough results
            scraped_data = scraper.get_tweets(hashtag, mode='hashtag', number=limit * 3)
            
            if scraped_data and 'tweets' in scraped_data and scraped_data['tweets']:
                print(f"✅ Scraped {len(scraped_data['tweets'])} tweets")
                
                for tweet in scraped_data['tweets']:
                    # Parse stats safely
                    stats = tweet.get('stats', {})
                    likes = stats.get('likes', 0)
                    retweets = stats.get('retweets', 0)
                    comments = stats.get('comments', 0)
                    
                    post = Post(
                        id=str(tweet.get('link', '').split('/')[-1] or '0'),
                        text=tweet.get('text', ''),
                        author=tweet.get('user', {}).get('username', 'unknown'),
                        likes=likes,
                        retweets=retweets,
                        replies=comments,
                        url=tweet.get('link', ''),
                        created_at=tweet.get('date', '')
                    )
                    posts.append(post)
                
                # Sort by engagement score (likes + retweets + replies)
                posts.sort(key=lambda p: p.engagement_score, reverse=True)
                posts = posts[:limit]
                
                print(f"✅ Returning top {len(posts)} posts")
                
            else:
                print("⚠️ Scraping returned no tweets (Nitter might be down)")
                
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            
        return posts
    
    def post_tweet(self, content: str) -> Optional[str]:
        """
        Post a tweet to X.
        
        Args:
            content: Tweet content (max 280 characters)
        
        Returns:
            Tweet ID if successful, None otherwise
        """
        if len(content) > 280:
            raise ValueError(f"Tweet too long: {len(content)} characters (max 280)")
        
        try:
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            print(f"✅ Tweet posted successfully! ID: {tweet_id}")
            return tweet_id
        
        except tweepy.TweepyException as e:
            print(f"❌ Error posting tweet: {e}")
            raise


if __name__ == '__main__':
    # Test the X client
    from config import Config
    Config.validate()
    
    client = XClient()
    print("🔍 Testing hashtag search...")
    
    # Test with a Farsi hashtag
    posts = client.get_top_posts('#ایران', limit=5)
    print(f"\n📊 Found {len(posts)} top posts:")
    
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. {post.author}")
        print(f"   {post.text[:100]}...")
        print(f"   Engagement: {post.engagement_score} (❤️{post.likes} 🔄{post.retweets} 💬{post.replies})")
