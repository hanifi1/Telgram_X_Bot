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
    
    def search_tweets_by_hashtag(self, hashtag: str, count: int = 100) -> List[dict]:
        """
        Search for recent tweets containing the specified hashtag.
        
        Args:
            hashtag: Hashtag to search for (with or without #)
            count: Maximum number of tweets to retrieve (default: 100)
        
        Returns:
            List of tweet dictionaries
        """
        # Ensure hashtag starts with #
        if not hashtag.startswith('#'):
            hashtag = f'#{hashtag}'
        
        try:
            # Search for tweets with the hashtag
            # Using tweet_fields to get engagement metrics
            response = self.client.search_recent_tweets(
                query=hashtag,
                max_results=min(count, 100),  # API limit is 100 per request
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )
            
            if not response.data:
                return []
            
            # Create a mapping of author IDs to usernames
            users = {}
            if response.includes and 'users' in response.includes:
                users = {user.id: user.username for user in response.includes['users']}
            
            tweets = []
            for tweet in response.data:
                author_username = users.get(tweet.author_id, 'unknown')
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'author': author_username,
                    'author_id': tweet.author_id,
                    'created_at': tweet.created_at,
                    'metrics': tweet.public_metrics
                })
            
            return tweets
        
        except tweepy.TweepyException as e:
            print(f"❌ Error searching tweets: {e}")
            raise
    
    def get_top_posts(self, hashtag: str, limit: int = 10) -> List[Post]:
        """
        Get top posts for a hashtag ranked by engagement.
        
        Args:
            hashtag: Hashtag to search for
            limit: Number of top posts to return (default: 10)
        
        Returns:
            List of Post objects sorted by engagement score
        """
        tweets = self.search_tweets_by_hashtag(hashtag, count=100)
        
        if not tweets:
            return []
        
        # Convert to Post objects
        posts = []
        for tweet in tweets:
            metrics = tweet['metrics']
            post = Post(
                id=str(tweet['id']),
                text=tweet['text'],
                author=tweet['author'],
                likes=metrics.get('like_count', 0),
                retweets=metrics.get('retweet_count', 0),
                replies=metrics.get('reply_count', 0),
                url=f"https://twitter.com/{tweet['author']}/status/{tweet['id']}",
                created_at=tweet['created_at'].strftime('%Y-%m-%d %H:%M') if isinstance(tweet['created_at'], datetime) else str(tweet['created_at'])
            )
            posts.append(post)
        
        # Sort by engagement score (likes + retweets + replies)
        posts.sort(key=lambda p: p.engagement_score, reverse=True)
        
        return posts[:limit]
    
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
