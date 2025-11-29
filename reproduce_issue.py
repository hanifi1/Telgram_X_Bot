from x_client import XClient
from config import Config

# Mock config to avoid needing real env vars if possible, but x_client uses Config directly
# We assume env vars are set or Config handles it.
# Actually Config.validate() is called in main, but x_client imports Config.
# Let's just run it, assuming .env is there.

def test_search():
    client = XClient()
    term = "ایران" # User said "I will put a word"
    print(f"Testing search with term: '{term}'")
    
    posts = client.get_top_posts(term, limit=5)
    
    print(f"Result count: {len(posts)}")
    if not posts:
        print("❌ returned empty list!")
    else:
        print("✅ returned posts:")
        for p in posts:
            print(f" - {p.id}: {p.text[:50]}...")

if __name__ == "__main__":
    test_search()
