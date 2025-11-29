"""
Configuration management for the Telegram X Bot.
Loads and validates environment variables.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration loaded from environment variables."""
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')
    
    # X (Twitter) API Configuration
    X_API_KEY = os.getenv('X_API_KEY')
    X_API_SECRET = os.getenv('X_API_SECRET')
    X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
    X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')
    
    # Ollama Configuration
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        required_vars = [
            ('TELEGRAM_BOT_TOKEN', cls.TELEGRAM_BOT_TOKEN),
            ('TELEGRAM_USER_ID', cls.TELEGRAM_USER_ID),
            ('X_API_KEY', cls.X_API_KEY),
            ('X_API_SECRET', cls.X_API_SECRET),
            ('X_ACCESS_TOKEN', cls.X_ACCESS_TOKEN),
            ('X_ACCESS_TOKEN_SECRET', cls.X_ACCESS_TOKEN_SECRET),
        ]
        
        missing = [name for name, value in required_vars if not value]
        
        if missing:
            print("❌ Missing required environment variables:")
            for var in missing:
                print(f"   - {var}")
            print("\n💡 Please create a .env file based on .env.example")
            sys.exit(1)
        
        print("✅ Configuration validated successfully!")
        return True

if __name__ == '__main__':
    # Test configuration when run directly
    Config.validate()
    print(f"\n📱 Telegram Bot Token: {Config.TELEGRAM_BOT_TOKEN[:10]}...")
    print(f"👤 Telegram User ID: {Config.TELEGRAM_USER_ID}")
    print(f"🐦 X API Key: {Config.X_API_KEY[:10]}...")
    print(f"🤖 Ollama Host: {Config.OLLAMA_HOST}")
    print(f"🧠 Ollama Model: {Config.OLLAMA_MODEL}")
