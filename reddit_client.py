"""
Reddit client for fetching trending posts as content source.
Uses Reddit's public JSON API (no authentication required).
"""

import requests
from typing import List, Dict
from datetime import datetime
from models import Post


class RedditClient:
    """Client for fetching top posts from Reddit using public JSON API."""
    
    # Map topics to relevant subreddits
    TOPIC_SUBREDDITS = {
        'python': ['python', 'learnpython', 'pythontips'],
        'javascript': ['javascript', 'learnjavascript', 'webdev'],
        'ai': ['artificial', 'MachineLearning', 'deeplearning'],
        'ml': ['MachineLearning', 'learnmachinelearning', 'datascience'],
        'crypto': ['cryptocurrency', 'CryptoMarkets', 'bitcoin'],
        'tech': ['technology', 'tech', 'gadgets'],
        'programming': ['programming', 'learnprogramming', 'coding'],
        'web': ['webdev', 'web_design', 'Frontend'],
        'data': ['datascience', 'datasets', 'dataengineering'],
        'startup': ['startups', 'Entrepreneur', 'SideProject'],
    }
    
    def __init__(self):
        """Initialize Reddit client."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TelegramXBot/1.0'
        })
    
    def _get_subreddits_for_topic(self, topic: str) -> List[str]:
        """
        Get relevant subreddits for a topic.
        
        Args:
            topic: Topic to search for (e.g., 'python', 'ai')
        
        Returns:
            List of subreddit names
        """
        topic_lower = topic.lower().replace('#', '').strip()
        
        # Check if we have a predefined mapping
        if topic_lower in self.TOPIC_SUBREDDITS:
            return self.TOPIC_SUBREDDITS[topic_lower]
        
        # Default: use the topic as subreddit name
        return [topic_lower]
    
    def get_top_posts(self, topic: str, limit: int = 10) -> List[Post]:
        """
        Get top posts from Reddit for a given topic.
        
        Args:
            topic: Topic to search for
            limit: Number of top posts to return
        
        Returns:
            List of Post objects sorted by score (upvotes - downvotes)
        """
        subreddits = self._get_subreddits_for_topic(topic)
        posts = []
        
        print(f"🔍 Fetching top posts from Reddit for topic: {topic}")
        print(f"📂 Searching subreddits: {', '.join(subreddits)}")
        
        for subreddit_name in subreddits:
            try:
                # Use Reddit's public JSON API (no auth needed)
                url = f"https://www.reddit.com/r/{subreddit_name}/top.json?t=week&limit={limit}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' not in data or 'children' not in data['data']:
                    continue
                
                for item in data['data']['children']:
                    post_data = item['data']
                    
                    # Extract text (title + selftext if available)
                    title = post_data.get('title', '')
                    selftext = post_data.get('selftext', '')
                    text = f"{title}\n\n{selftext[:200]}" if selftext else title
                    
                    post = Post(
                        id=post_data.get('id', ''),
                        text=text,
                        author=post_data.get('author', 'deleted'),
                        likes=post_data.get('score', 0),
                        retweets=0,  # Reddit doesn't have retweets
                        replies=post_data.get('num_comments', 0),
                        url=f"https://reddit.com{post_data.get('permalink', '')}",
                        created_at=datetime.fromtimestamp(post_data.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M')
                    )
                    posts.append(post)
                    
            except Exception as e:
                print(f"⚠️ Error fetching from r/{subreddit_name}: {e}")
                continue
        
        if not posts:
            print(f"❌ No posts found for topic: {topic}")
            return []
        
        # Sort by engagement score (score + comments)
        posts.sort(key=lambda p: p.engagement_score, reverse=True)
        
        print(f"✅ Found {len(posts)} posts, returning top {limit}")
        return posts
    
    def get_trending_topics(self, limit: int = 10) -> List[Dict]:
        """
        Get trending topics from Reddit's r/all.
        
        Args:
            limit: Number of trending topics to return
        
        Returns:
            List of trending topics with title, subreddit, and engagement
        """
        try:
            print(f"🔥 Fetching top {limit} trending topics from Reddit...")
            
            # Fetch from r/all hot posts
            url = f"https://www.reddit.com/r/all/hot.json?limit={limit * 2}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'data' not in data or 'children' not in data['data']:
                return []
            
            topics = []
            for item in data['data']['children']:
                post_data = item['data']
                
                # Skip stickied posts and ads
                if post_data.get('stickied') or post_data.get('promoted'):
                    continue
                
                topic = {
                    'title': post_data.get('title', ''),
                    'subreddit': post_data.get('subreddit', ''),
                    'score': post_data.get('score', 0),
                    'comments': post_data.get('num_comments', 0),
                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                    'id': post_data.get('id', '')
                }
                topics.append(topic)
                
                if len(topics) >= limit:
                    break
            
            print(f"✅ Found {len(topics)} trending topics")
            return topics
            
        except Exception as e:
            print(f"❌ Failed to fetch trending topics: {e}")
            return [][:limit]


if __name__ == '__main__':
    # Test the Reddit client
    client = RedditClient()
    
    print("🧪 Testing Reddit client...\n")
    
    # Test with 'python' topic
    posts = client.get_top_posts('python', limit=5)
    
    print(f"\n📊 Top {len(posts)} posts:\n")
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post.author}")
        print(f"   {post.text[:100]}...")
        print(f"   👍 {post.likes} | 💬 {post.replies}")
        print(f"   Engagement: {post.engagement_score}")
        print("-" * 60)

