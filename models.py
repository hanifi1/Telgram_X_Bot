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
    """Manages bot state for a single user session."""
    
    def __init__(self):
        self.last_search_hashtag: Optional[str] = None
        self.last_search_results: list[Post] = []
        self.current_proposal: Optional[ProposedPost] = None
    
    def set_search_results(self, hashtag: str, posts: list[Post]):
        """Store search results."""
        self.last_search_hashtag = hashtag
        self.last_search_results = posts
    
    def set_proposal(self, proposal: ProposedPost):
        """Store current proposal."""
        self.current_proposal = proposal
    
    def clear_proposal(self):
        """Clear current proposal."""
        self.current_proposal = None
    
    def has_search_results(self) -> bool:
        """Check if there are search results available."""
        return bool(self.last_search_results)
    
    def has_proposal(self) -> bool:
        """Check if there is a proposal awaiting approval."""
        return self.current_proposal is not None
