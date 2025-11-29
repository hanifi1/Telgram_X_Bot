"""
Web research client for gathering information about topics.
Uses DuckDuckGo search (free, no API key needed).
"""

from duckduckgo_search import DDGS
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


class ResearchClient:
    """Client for performing web research on topics."""
    
    def __init__(self):
        """Initialize research client."""
        self.ddgs = DDGS()
    
    def search_topic(self, topic: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web for information about a topic.
        
        Args:
            topic: Topic to research
            max_results: Maximum number of results to return
        
        Returns:
            List of search results with title, snippet, and URL
        """
        try:
            print(f"🔍 Researching: {topic}")
            
            # Perform search using DuckDuckGo
            results = []
            search_results = self.ddgs.text(topic, max_results=max_results)
            
            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'url': result.get('href', '')
                })
            
            print(f"✅ Found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def summarize_research(self, topic: str, results: List[Dict]) -> str:
        """
        Create a summary of research results.
        
        Args:
            topic: Topic being researched
            results: List of search results
        
        Returns:
            Formatted summary string
        """
        if not results:
            return f"No information found about '{topic}'"
        
        summary = f"📚 **Research Summary: {topic}**\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"**{i}. {result['title']}**\n"
            summary += f"{result['snippet'][:200]}...\n"
            summary += f"🔗 [Read more]({result['url']})\n\n"
        
        return summary


if __name__ == '__main__':
    # Test the research client
    client = ResearchClient()
    
    print("🧪 Testing research client...\n")
    
    # Test with 'python machine learning' topic
    results = client.search_topic('python machine learning', max_results=3)
    
    if results:
        summary = client.summarize_research('python machine learning', results)
        print(summary)
    else:
        print("❌ No results found")
