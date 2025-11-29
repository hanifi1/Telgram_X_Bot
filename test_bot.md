# Testing Your Telegram Bot

## ✅ Your Bot is Running!

The logs show your bot is successfully connected to Telegram:
```
✅ Bot is running! Press Ctrl+C to stop.
Application started
```

## How to Find and Test Your Bot

### 1. Find Your Bot in Telegram

**Option A: Search by Username**
- Open Telegram app
- Click the search icon (🔍)
- Type your bot's username (the one you created with @BotFather)
- Click on your bot from the search results

**Option B: Use Direct Link**
- If you remember your bot username, go to: `https://t.me/YOUR_BOT_USERNAME`
- Replace `YOUR_BOT_USERNAME` with your actual bot username

### 2. Start the Conversation

Once you find your bot:
1. Click **"Start"** button at the bottom
2. Or type `/start` and press send

You should see this welcome message:
```
🤖 Welcome to Telegram X Bot!

This bot helps you analyze trending Farsi hashtags on X (Twitter)...
```

### 3. Test the Bot

Try these commands:

```
/start
```
Should show welcome message

```
/search #ایران
```
Should search for top posts with #ایران hashtag

## Troubleshooting

### "I can't find my bot"

1. **Check your bot username:**
   - Go back to your chat with @BotFather
   - Look for the message where it gave you the bot token
   - Your bot username should be there (ends with "bot")

2. **Make sure you're using the correct Telegram account:**
   - Your bot only responds to user ID: `1479431077`
   - Make sure you're logged into the Telegram account with this user ID
   - To verify: message @userinfobot and check your ID

### "Bot doesn't respond to my messages"

1. **Check if you're the authorized user:**
   - Send `/start` to @userinfobot
   - Verify your user ID is `1479431077`
   - If not, update the `TELEGRAM_USER_ID` in your `.env` file

2. **Restart the bot:**
   ```bash
   # Stop the bot (Ctrl+C if running)
   # Then start again:
   source venv/bin/activate
   python bot.py
   ```

### "How do I know my bot username?"

Check your conversation with @BotFather. When you created the bot, it sent you a message like:

```
Done! Congratulations on your new bot. You will find it at t.me/YOUR_BOT_NAME.
```

## Quick Test Commands

Once you find your bot, test these in order:

1. `/start` - Should show welcome message
2. `/search #test` - Should search for posts (may not find many)
3. `/search #ایران` - Should find Farsi posts
4. `/propose` - Should generate AI proposal (requires Ollama running)
5. `/cancel` - Should cancel operation

## Your Bot Details

- **Authorized User ID:** 1479431077
- **Bot Token:** 8558056654:AAEdTc_Wb9I8D3j1OgVZb4AAwXTKbd4a-h4
- **Ollama Model:** mistral
- **Status:** ✅ Running and connected to Telegram

## Next Steps

1. Find your bot in Telegram
2. Send `/start`
3. Try `/search #ایران` to test X API integration
4. Make sure Ollama is running: `ollama serve`
5. Try `/propose` to test AI generation

Need help? Check the README.md for more details!
