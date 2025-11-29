"""
Script to test X (Twitter) API credentials.
"""
import tweepy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_x_connection():
    print("\n🔍 Testing X API Connection...")
    
    # Get credentials
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    access_token = os.getenv('X_ACCESS_TOKEN')
    access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')
    
    # Check if credentials exist
    print(f"🔑 API Key: {'✅ Found' if api_key else '❌ Missing'}")
    print(f"🔑 API Secret: {'✅ Found' if api_secret else '❌ Missing'}")
    print(f"🔑 Access Token: {'✅ Found' if access_token else '❌ Missing'}")
    print(f"🔑 Access Secret: {'✅ Found' if access_token_secret else '❌ Missing'}")
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("\n❌ Missing one or more required credentials in .env file.")
        return
    
    try:
        # Initialize Client
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Test connection by getting current user
        print("\n📡 Connecting to X API...")
        me = client.get_me()
        
        if me.data:
            print(f"\n✅ SUCCESS! Connected as: @{me.data.username} (ID: {me.data.id})")
            
            # Test Search Permission
            print("\n🔍 Testing Search Permissions...")
            try:
                client.search_recent_tweets(query="#test", max_results=10)
                print("✅ Search Permission: GRANTED")
            except tweepy.TweepyException as e:
                print(f"❌ Search Permission: DENIED (Likely Free Tier limitation)")
                print(f"   Error: {e}")

            # Test Write Permission (Dry Run check if possible, or just print info)
            print("\n📝 Note: Write permissions are required to post tweets.")
            print("   If you are on the Free Tier, you CAN post but CANNOT search.")
            
        else:
            print("\n❌ Connection failed: Could not retrieve user data.")
            
    except tweepy.TweepyException as e:
        print(f"\n❌ Connection Error: {e}")
        print("\n💡 Troubleshooting Tips:")
        print("1. Check if your API Key and Secret are correct.")
        print("2. Check if your Access Token and Secret are correct.")
        print("3. Ensure your App has 'Read and Write' permissions in the X Developer Portal.")
        print("4. Regenerate your Access Token/Secret AFTER changing app permissions.")

if __name__ == "__main__":
    test_x_connection()
