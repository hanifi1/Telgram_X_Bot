"""
Test X API search with English hashtag.
"""
from x_client import XClient
from config import Config

def test_api_search():
    print("🔍 Testing X API Search...")
    Config.validate()
    
    client = XClient()
    
    # Test with an English hashtag
    hashtag = "python"
    print(f"\n📡 Searching for #{hashtag}...")
    
    try:
        posts = client.get_top_posts(hashtag, limit=5)
        
        if posts:
            print(f"\n✅ SUCCESS! Found {len(posts)} posts:\n")
            for i, post in enumerate(posts, 1):
                print(f"{i}. @{post.author}")
                print(f"   {post.text[:100]}...")
                print(f"   ❤️ {post.likes} 🔄 {post.retweets} 💬 {post.replies}")
                print(f"   Engagement: {post.engagement_score}")
                print("-" * 60)
        else:
            print("\n❌ No posts found.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nThis is expected if you're on the Free Tier.")
        print("Free Tier does NOT support search_recent_tweets.")

if __name__ == "__main__":
    test_api_search()
