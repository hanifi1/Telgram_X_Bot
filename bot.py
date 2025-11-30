"""
Main Telegram bot application - Trending Topics Workflow.
Handles user commands and orchestrates Reddit trending, web research, and X posting.
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
from reddit_client import RedditClient
from research_client import ResearchClient
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
reddit_client = RedditClient()  # For trending topics
research_client = ResearchClient()  # For web research
x_client = XClient()  # For posting tweets
content_gen = ContentGenerator()


def is_authorized_user(user_id: int) -> bool:
    """Check if user is authorized to use the bot."""
    authorized_id = int(Config.TELEGRAM_USER_ID)
    return user_id == authorized_id


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    # Log all incoming requests for debugging
    logger.info(f"📱 /start command from user_id={user_id}, username=@{username}")
    print(f"📱 /start command from user_id={user_id}, username=@{username}")
    
    if not is_authorized_user(user_id):
        logger.warning(f"❌ Unauthorized access attempt from user_id={user_id}")
        print(f"❌ Unauthorized access attempt from user_id={user_id}")
        print(f"💡 Expected user_id={Config.TELEGRAM_USER_ID}")
        await update.message.reply_text(
            f"❌ Unauthorized. This bot is for private use only.\\n\\n"
            f"Your user ID: {user_id}\\n"
            f"Expected user ID: {Config.TELEGRAM_USER_ID}\\n\\n"
            f"💡 Update TELEGRAM_USER_ID in your .env file to {user_id} to authorize yourself."
        )
        return
    
    welcome_message = """
🤖 **Welcome to Telegram X Bot!**

This bot helps you discover trending topics, research them, and create AI-powered X posts.

**Workflow:**

1️⃣ `/trending python` - Find top 10 trending posts about Python on Reddit

2️⃣ `/research 3` - Research topic #3 on the web (LLM does deep research)

3️⃣ `/propose` - LLM writes an X post based on research

4️⃣ `/approve` - Post to X

**Other Commands:**
❌ `/cancel` - Cancel current operation

Let's discover what's trending! 🚀
"""
    
    await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)


async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trending command to show trending topics for a specific subject."""
    user_id = update.effective_user.id
    
    if not is_authorized_user(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    # Get topic from command arguments
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a topic.\\n"
            "Usage: `/trending python`\\n"
            "Example: `/trending ai`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    topic = ' '.join(context.args)
    
    # Send "fetching" message
    status_msg = await update.message.reply_text(
        f"🔥 Finding top 10 trending posts about '{topic}' on Reddit...\\n"
        "This may take a moment..."
    )
    
    try:
        # Fetch top posts for the topic
        posts = reddit_client.get_top_posts(topic, limit=10)
        
        if not posts:
            await status_msg.edit_text(
                f"❌ No trending posts found for '{topic}'.\\n"
                "Try a different topic or check spelling."
            )
            return
        
        # Convert posts to topic format for consistency
        topics = []
        for post in posts[:10]:  # Limit to exactly 10 posts
            topics.append({
                'title': post.text,
                'subreddit': 'various',
                'score': post.likes,
                'comments': post.replies,
                'url': post.url,
                'id': post.id
            })
        
        # Store topics in bot state
        bot_state.set_trending_topics(topics)
        
        # Delete status message
        await status_msg.delete()
        
        # Send header message
        header_msg = f"🔥 **Top 10 Trending Posts: {topic}**\n\n"
        await update.message.reply_text(header_msg, parse_mode=ParseMode.MARKDOWN)
        
        # Send each post as a separate message
        for i, topic_item in enumerate(topics, 1):
            # Escape special Markdown characters to avoid parsing errors
            text = topic_item['title']
            # Escape Markdown special characters
            for char in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
                text = text.replace(char, f'\\{char}')
            
            post_message = (
                f"**━━━ Post #{i} ━━━**\n"
                f"{text}\n\n"
                f"👍 {topic_item['score']:,} upvotes | 💬 {topic_item['comments']} comments"
            )
            await update.message.reply_text(
                post_message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
        
        # Send footer message
        footer_msg = (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Found {len(topics)} trending posts\n\n"
            "💡 Use `/research 3` to research post #3!"
        )
        await update.message.reply_text(footer_msg, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Error in trending_command: {e}")
        await status_msg.edit_text(
            f"❌ Error fetching trending posts: {str(e)}\\n\\n"
            "Please try again with a different topic."
        )


async def research_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /research command for web research on selected topic."""
    user_id = update.effective_user.id
    
    if not is_authorized_user(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    # Check if there are trending topics
    if not bot_state.has_trending_topics():
        await update.message.reply_text(
            "❌ No trending topics available.\\n"
            "Please use `/trending` first!",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Get topic number from command arguments
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "❌ Please provide a topic number.\\n"
            "Usage: `/research 3`\\n"
            "Example: `/research 1`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    topic_num = int(context.args[0])
    
    # Select the topic
    selected_topic = bot_state.select_topic(topic_num)
    
    if not selected_topic:
        await update.message.reply_text(
            f"❌ Invalid topic number. Please choose between 1 and {len(bot_state.trending_topics)}."
        )
        return
    
    # Send "researching" message
    status_msg = await update.message.reply_text(
        f"🔬 Researching topic #{topic_num}: '{selected_topic['title'][:50]}...'\\n"
        "LLM is gathering information from the web..."
    )
    
    try:
        # Perform web research
        results = research_client.search_topic(selected_topic['title'], max_results=5)
        
        if not results:
            await status_msg.edit_text(
                f"❌ No research results found for this topic.\\n"
                "Try a different topic."
            )
            return
        
        # Store research results
        bot_state.set_research_results(results)
        
        # Format research summary
        summary = f"🔬 **Research: {selected_topic['title'][:80]}**\\n\\n"
        
        for i, result in enumerate(results, 1):
            title = result['title'][:80]
            snippet = result['snippet'][:120] + "..." if len(result['snippet']) > 120 else result['snippet']
            summary += (
                f"**{i}. {title}**\\n"
                f"{snippet}\\n"
                f"🔗 [Read more]({result['url']})\\n\\n"
            )
        
        summary += (
            "━━━━━━━━━━━━━━━━━━━━\\n"
            f"✅ Found {len(results)} research sources\\n\\n"
            "💡 Use `/propose` to generate an X post from this research!"
        )
        
        # Delete status message and send results
        await status_msg.delete()
        await update.message.reply_text(
            summary,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error in research_command: {e}")
        await status_msg.edit_text(
            f"❌ Error performing research: {str(e)}\\n\\n"
            "Please try again."
        )


async def propose_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /propose command to generate X post from research."""
    user_id = update.effective_user.id
    
    if not is_authorized_user(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    # Check if there are research results
    if not bot_state.has_research_results():
        await update.message.reply_text(
            "❌ No research results available.\\n"
            "Please use `/research [number]` first!",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Send "generating" message
    status_msg = await update.message.reply_text(
        "🤖 LLM is writing an X post based on research...\\n"
        "This may take a moment..."
    )
    
    try:
        # Check Ollama connection
        if not content_gen.test_connection():
            await status_msg.edit_text(
                "❌ Cannot connect to Ollama.\\n\\n"
                "Please make sure Ollama is running:\\n"
                "1. Install from https://ollama.ai\\n"
                f"2. Run: `ollama pull {Config.OLLAMA_MODEL}`\\n"
                "3. Ollama should be running in the background",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Generate proposal from research
        proposal = content_gen.generate_from_research(
            bot_state.selected_topic['title'],
            bot_state.research_results
        )
        
        # Store proposal
        bot_state.set_proposal(proposal)
        
        # Format proposal message
        proposal_message = (
            "🤖 **AI-Generated X Post**\\n\\n"
            f"📝 {proposal.content}\\n\\n"
            "━━━━━━━━━━━━━━━━━━━━\\n"
            f"📊 Based on: {bot_state.selected_topic['title'][:60]}...\\n"
            f"📏 Length: {len(proposal.content)} characters\\n\\n"
            "✅ Use `/approve` to post this to X\\n"
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
            f"❌ Error generating proposal: {str(e)}\\n\\n"
            "Please check:\\n"
            "• Ollama is running\\n"
            f"• Model '{Config.OLLAMA_MODEL}' is installed\\n"
            "• Try running: `ollama pull {Config.OLLAMA_MODEL}`",
            parse_mode=ParseMode.MARKDOWN
        )


async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /approve command to post to X."""
    user_id = update.effective_user.id
    
    if not is_authorized_user(user_id):
        await update.message.reply_text("❌ Unauthorized.")
        return
    
    # Check if there's a proposal
    if not bot_state.has_proposal():
        await update.message.reply_text(
            "❌ No proposal to approve.\\n"
            "Please use `/propose` first!",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # Send "posting" message
    status_msg = await update.message.reply_text(
        "📤 Posting to X...\\n"
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
            "✅ **Successfully posted to X!**\\n\\n"
            f"📝 {bot_state.current_proposal.content if bot_state.current_proposal else 'Posted'}\\n\\n"
            f"🔗 [View on X]({tweet_url})\\n\\n"
            "🎉 Great job! Use `/trending` to discover more topics."
        )
        
        await status_msg.edit_text(
            success_message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error in approve_command: {e}")
        await status_msg.edit_text(
            f"❌ Error posting to X: {str(e)}\\n\\n"
            "Please check:\\n"
            "• X API credentials have write permissions\\n"
            "• You haven't exceeded posting limits (500/month)\\n"
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
            "❌ Proposal discarded.\\n\\n"
            "Use `/trending` to start over or `/propose` to generate a new proposal."
        )
    else:
        await update.message.reply_text(
            "ℹ️ Nothing to cancel.\\n\\n"
            "Use `/trending` to get started!"
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
    application.add_handler(CommandHandler("trending", trending_command))
    application.add_handler(CommandHandler("research", research_command))
    application.add_handler(CommandHandler("propose", propose_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Start the bot
    print("\\n✅ Bot is running! Press Ctrl+C to stop.\\n")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
