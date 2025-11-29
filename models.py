"""
Data models for the Telegram X Bot.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Post:
    """Represents an X (Twitter) post with engagement metrics."""
    id: str
    text: str
    author: str
    likes: int
    retweets: int
    replies: int
    url: str
    created_at: str
    
    @property
    def engagement_score(self) -> int:
        """Calculate total engagement score."""
        return self.likes + self.retweets + self.replies
    
    def format_for_telegram(self) -> str:
        """Format post for display in Telegram."""
        return (
            f"👤 **{self.author}**\n"
            f"📝 {self.text}\n\n"
            f"❤️ {self.likes} | 🔄 {self.retweets} | 💬 {self.replies}\n"
            f"🔗 {self.url}\n"
            f"📅 {self.created_at}"
        )


@dataclass
class ProposedPost:
    """Represents a proposed post awaiting user approval."""
    content: str
    hashtag: str
    based_on_posts: list
    
    def format_for_telegram(self) -> str:
        """Format proposed post for display in Telegram."""
        return (
            f"🤖 **AI-Generated Post Proposal**\n\n"
            f"📝 {self.content}\n\n"
            f"📊 Based on: {self.hashtag}\n"
            f"📈 Analyzed {len(self.based_on_posts)} top posts\n\n"
            f"✅ Use /approve to post to X\n"
            f"❌ Use /cancel to discard"
        )




class BotState:
    """Manages bot state for trending topics workflow."""
    
    def __init__(self):
        self.trending_topics: list = []  # List of trending topics from Reddit
        self.selected_topic: Optional[dict] = None  # Currently selected topic
        self.research_results: list = []  # Web research results
        self.current_proposal: Optional[ProposedPost] = None
    
    def set_trending_topics(self, topics: list):
        """Store trending topics."""
        self.trending_topics = topics
    
    def select_topic(self, topic_number: int) -> Optional[dict]:
        """Select a topic by number (1-indexed)."""
        if 1 <= topic_number <= len(self.trending_topics):
            self.selected_topic = self.trending_topics[topic_number - 1]
            return self.selected_topic
        return None
    
    def set_research_results(self, results: list):
        """Store research results."""
        self.research_results = results
    
    def set_proposal(self, proposal: ProposedPost):
        """Store current proposal."""
        self.current_proposal = proposal
    
    def clear_proposal(self):
        """Clear current proposal."""
        self.current_proposal = None
    
    def has_trending_topics(self) -> bool:
        """Check if there are trending topics available."""
        return bool(self.trending_topics)
    
    def has_selected_topic(self) -> bool:
        """Check if a topic has been selected."""
        return self.selected_topic is not None
    
    def has_research_results(self) -> bool:
        """Check if there are research results available."""
        return bool(self.research_results)
    
    def has_proposal(self) -> bool:
        """Check if there is a proposal awaiting approval."""
        return self.current_proposal is not None
