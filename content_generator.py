"""
AI-powered content generation using Ollama (local LLM).
"""

import requests
import json
from typing import List
from config import Config
from models import Post, ProposedPost


class ContentGenerator:
    """Generate post proposals using Ollama local LLM."""
    
    def __init__(self):
        """Initialize content generator with Ollama configuration."""
        self.ollama_host = Config.OLLAMA_HOST
        self.model = Config.OLLAMA_MODEL
        self.api_url = f"{self.ollama_host}/api/generate"
    
    def analyze_trends(self, posts: List[Post]) -> str:
        """
        Analyze top posts to identify themes and topics.
        
        Args:
            posts: List of top posts to analyze
        
        Returns:
            Summary of trends and themes
        """
        if not posts:
            return "No posts to analyze"
        
        # Extract text from posts
        post_texts = [f"- {post.text}" for post in posts[:5]]  # Use top 5 for analysis
        combined_text = "\n".join(post_texts)
        
        return combined_text
    
    def generate_post_proposal(self, posts: List[Post], hashtag: str) -> ProposedPost:
        """
        Generate an engaging Farsi post based on trending posts.
        
        Args:
            posts: List of top posts to base the proposal on
            hashtag: The hashtag being analyzed
        
        Returns:
            ProposedPost object with generated content
        """
        if not posts:
            raise ValueError("No posts provided for content generation")
        
        # Analyze trends
        trends_summary = self.analyze_trends(posts)
        
        # Create prompt for Ollama
        prompt = f"""You are a social media expert creating engaging Persian/Farsi tweets.

Based on these top trending posts about {hashtag}:

{trends_summary}

Create ONE engaging Persian/Farsi tweet that:
1. Reflects the main themes and topics from these posts
2. Is culturally relevant and engaging for Persian speakers
3. Is MAXIMUM 280 characters (very important!)
4. Includes the hashtag {hashtag}
5. Is original and creative, not a copy

IMPORTANT: Respond ONLY with the tweet text in Persian/Farsi. No explanations, no English, just the tweet.
"""
        
        # Call Ollama API
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get('response', '').strip()
            
            # Ensure it's within character limit
            if len(generated_text) > 280:
                # Truncate and add ellipsis
                generated_text = generated_text[:277] + "..."
            
            # Create ProposedPost
            proposal = ProposedPost(
                content=generated_text,
                hashtag=hashtag,
                based_on_posts=posts
            )
            
            return proposal
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error calling Ollama API: {e}")
            raise Exception(f"Failed to generate content. Is Ollama running? Error: {e}")
    
    def test_connection(self) -> bool:
        """
        Test connection to Ollama.
        
        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False


if __name__ == '__main__':
    # Test the content generator
    from config import Config
    Config.validate()
    
    generator = ContentGenerator()
    
    # Test Ollama connection
    print("🔍 Testing Ollama connection...")
    if generator.test_connection():
        print("✅ Ollama is running!")
    else:
        print("❌ Cannot connect to Ollama. Make sure it's running.")
        exit(1)
    
    # Create sample posts for testing
    sample_posts = [
        Post(
            id="1",
            text="تست پست اول درباره ایران و فرهنگ غنی آن",
            author="user1",
            likes=100,
            retweets=50,
            replies=20,
            url="https://twitter.com/user1/status/1",
            created_at="2024-01-01 12:00"
        ),
        Post(
            id="2",
            text="ایران زیباست و مردمش مهربان",
            author="user2",
            likes=80,
            retweets=30,
            replies=15,
            url="https://twitter.com/user2/status/2",
            created_at="2024-01-01 13:00"
        )
    ]
    
    print("\n🤖 Generating post proposal...")
    try:
        proposal = generator.generate_post_proposal(sample_posts, "#ایران")
        print(f"\n✅ Generated proposal:")
        print(f"📝 {proposal.content}")
        print(f"📏 Length: {len(proposal.content)} characters")
    except Exception as e:
        print(f"❌ Error: {e}")
