"""
Main Telegram bot application.
Handles user commands and orchestrates X API and content generation.
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode

from config import Config
from models import BotState
from x_client import XClient
from content_generator import ContentGenerator

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot state
bot_state = BotState()

# Initialize clients
x_client = XClient()
content_gen = ContentGenerator()


def is_authorized_user(user_id: int) -> bool:
    """Check if user is authorized to use the bot."""
    authorized_id = int(Config.TELEGRAM_USER_ID)
    return user_id == authorized_id


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user_id = update.effective_user.id
    
    if not is_authorized_user(user_id):
        await update.message.reply_text(
            "❌ Unauthorized. This bot is for private use only."
        )
        return
    
    welcome_message = """
🤖 **Welcome to Telegram X Bot!**

This bot helps you analyze trending Farsi hashtags on X (Twitter) and generate AI-powered post proposals.

**Available Commands:**

📊 `/search #hashtag` - Search for a Farsi hashtag and view top 10 posts
   Example: `/search #ایران`

🤖 `/propose` - Generate AI post proposal based on last search

✅ `/approve` - Post the proposed content to X

❌ `/cancel` - Cancel current operation

**How it works:**
1. Search for a hashtag to see top posts
2. Generate a proposal based on those posts
3. Review and approve to post to X

Let's get started! 🚀
"""
    
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command."""
    user_id = update.effective_user.id
    
    if not is_authorized_user(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    # Get hashtag from command arguments
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a hashtag.\n"
            "Usage: `/search #hashtag`\n"
            "Example: `/search #ایران`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    hashtag = context.args[0]
    
    # Send "searching" message
    status_msg = await update.message.reply_text(
        f"🔍 Searching for top posts with {hashtag}...\n"
        "This may take a moment..."
    )
    
    try:
        # Search for top posts
        posts = x_client.get_top_posts(hashtag, limit=10)
        
        if not posts:
            await status_msg.edit_text(
                f"❌ No posts found for {hashtag}\n"
                "Try a different hashtag or check if it's spelled correctly."
            )
            return
        
        # Store results in bot state
        bot_state.set_search_results(hashtag, posts)
        
        # Format results for display
        results_message = f"📊 **Top 10 Posts for {hashtag}**\n\n"
        
        for i, post in enumerate(posts, 1):
            # Truncate long posts
            text = post.text[:150] + "..." if len(post.text) > 150 else post.text
            results_message += (
                f"**{i}. @{post.author}**\n"
                f"{text}\n"
                f"❤️ {post.likes} | 🔄 {post.retweets} | 💬 {post.replies}\n"
                f"[View Post]({post.url})\n\n"
            )
        
        results_message += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Found {len(posts)} posts\n\n"
            "💡 Use `/propose` to generate an AI post based on these results!"
        )
        
        # Delete status message and send results
        await status_msg.delete()
        await update.message.reply_text(
            results_message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error in search_command: {e}")
        await status_msg.edit_text(
            f"❌ Error searching for posts: {str(e)}\n\n"
            "Please check:\n"
            "• X API credentials are correct\n"
            "• You haven't exceeded rate limits\n"
            "• The hashtag is valid"
        )


async def propose_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /propose command."""
    user_id = update.effective_user.id
    
    if not is_authorized_user(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    # Check if there are search results
    if not bot_state.has_search_results():
        await update.message.reply_text(
            "❌ No search results available.\n"
            "Please use `/search #hashtag` first!",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Send "generating" message
    status_msg = await update.message.reply_text(
        "🤖 Generating AI-powered post proposal...\n"
        "This may take a moment..."
    )
    
    try:
        # Check Ollama connection
        if not content_gen.test_connection():
            await status_msg.edit_text(
                "❌ Cannot connect to Ollama.\n\n"
                "Please make sure Ollama is running:\n"
                "1. Install from https://ollama.ai\n"
                f"2. Run: `ollama pull {Config.OLLAMA_MODEL}`\n"
                "3. Ollama should be running in the background",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Generate proposal
        proposal = content_gen.generate_post_proposal(
            bot_state.last_search_results,
            bot_state.last_search_hashtag
        )
        
        # Store proposal
        bot_state.set_proposal(proposal)
        
        # Format proposal message
        proposal_message = (
            "🤖 **AI-Generated Post Proposal**\n\n"
            f"📝 {proposal.content}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Based on: {proposal.hashtag}\n"
            f"📈 Analyzed {len(proposal.based_on_posts)} top posts\n"
            f"📏 Length: {len(proposal.content)} characters\n\n"
            "✅ Use `/approve` to post this to X\n"
            "❌ Use `/cancel` to discard"
        )
        
        # Delete status message and send proposal
        await status_msg.delete()
        await update.message.reply_text(
            proposal_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in propose_command: {e}")
        await status_msg.edit_text(
            f"❌ Error generating proposal: {str(e)}\n\n"
            "Please check:\n"
            "• Ollama is running\n"
            f"• Model '{Config.OLLAMA_MODEL}' is installed\n"
            "• Try running: `ollama pull {Config.OLLAMA_MODEL}`",
            parse_mode=ParseMode.MARKDOWN
        )


async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /approve command."""
    user_id = update.effective_user.id
    
    if not is_authorized_user(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    # Check if there's a proposal
    if not bot_state.has_proposal():
        await update.message.reply_text(
            "❌ No proposal to approve.\n"
            "Please use `/propose` first!",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Send "posting" message
    status_msg = await update.message.reply_text(
        "📤 Posting to X...\n"
        "Please wait..."
    )
    
    try:
        # Post to X
        tweet_id = x_client.post_tweet(bot_state.current_proposal.content)
        
        # Clear proposal
        bot_state.clear_proposal()
        
        # Success message
        tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
        success_message = (
            "✅ **Successfully posted to X!**\n\n"
            f"📝 {bot_state.current_proposal.content if bot_state.current_proposal else 'Posted'}\n\n"
            f"🔗 [View on X]({tweet_url})\n\n"
            "🎉 Great job! Use `/search` to find more trends."
        )
        
        await status_msg.edit_text(
            success_message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error in approve_command: {e}")
        await status_msg.edit_text(
            f"❌ Error posting to X: {str(e)}\n\n"
            "Please check:\n"
            "• X API credentials have write permissions\n"
            "• You haven't exceeded posting limits (500/month)\n"
            "• The content meets X's guidelines"
        )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /cancel command."""
    user_id = update.effective_user.id
    
    if not is_authorized_user(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    if bot_state.has_proposal():
        bot_state.clear_proposal()
        await update.message.reply_text(
            "❌ Proposal discarded.\n\n"
            "Use `/search` to start over or `/propose` to generate a new proposal."
        )
    else:
        await update.message.reply_text(
            "ℹ️ Nothing to cancel.\n\n"
            "Use `/search #hashtag` to get started!"
        )


def main():
    """Start the bot."""
    # Validate configuration
    Config.validate()
    
    print("🤖 Starting Telegram X Bot...")
    print(f"👤 Authorized User ID: {Config.TELEGRAM_USER_ID}")
    print(f"🐦 X API configured")
    print(f"🧠 Ollama Model: {Config.OLLAMA_MODEL}")
    print(f"🌐 Ollama Host: {Config.OLLAMA_HOST}")
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("propose", propose_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Start the bot
    print("\n✅ Bot is running! Press Ctrl+C to stop.\n")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
