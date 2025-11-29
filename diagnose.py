"""
Diagnostic script to test bot connection and identify issues.
"""

import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from config import Config

# Configure detailed logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

async def debug_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log ALL incoming messages for debugging."""
    user = update.effective_user
    message = update.message
    
    print("\n" + "="*60)
    print("📨 INCOMING MESSAGE DETECTED!")
    print("="*60)
    print(f"👤 User ID: {user.id}")
    print(f"👤 Username: @{user.username if user.username else 'No username'}")
    print(f"👤 First Name: {user.first_name}")
    print(f"📝 Message Text: {message.text if message.text else 'No text'}")
    print(f"🕐 Timestamp: {message.date}")
    print("="*60)
    print(f"\n💡 Your TELEGRAM_USER_ID in .env: {Config.TELEGRAM_USER_ID}")
    print(f"💡 Match: {'✅ YES' if str(user.id) == str(Config.TELEGRAM_USER_ID) else '❌ NO'}")
    print("="*60 + "\n")
    
    # Send a response
    await message.reply_text(
        f"🔍 **Debug Info**\n\n"
        f"Your User ID: `{user.id}`\n"
        f"Expected User ID: `{Config.TELEGRAM_USER_ID}`\n"
        f"Match: {'✅ Authorized' if str(user.id) == str(Config.TELEGRAM_USER_ID) else '❌ Not Authorized'}\n\n"
        f"Message received: {message.text}"
    )

def main():
    """Run diagnostic bot."""
    print("\n🔍 Starting Diagnostic Bot...")
    print(f"📱 Bot Token: {Config.TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"👤 Expected User ID: {Config.TELEGRAM_USER_ID}")
    print("\n✅ Bot is listening for ALL messages...\n")
    print("💡 Send ANY message to the bot to see debug info!\n")
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Add handler for ALL messages (both commands and regular text)
    application.add_handler(MessageHandler(filters.ALL, debug_all_messages))
    
    # Start polling
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
