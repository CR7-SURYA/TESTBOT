import os
import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from flask import Flask

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables")

# Conversation states
GET_NAME = 1

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a welcome message and ask for the user's name."""
    welcome_message = (
        "👋 Welcome to the Name Styler Bot!\n\n"
        "I can display your name in different cool styles. "
        "Please send me your name:"
    )
    
    await update.message.reply_text(welcome_message)
    return GET_NAME

# Handle name input
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the user's name and display it in different styles."""
    user_name = update.message.text.strip()
    
    if not user_name:
        await update.message.reply_text("Please send me a valid name!")
        return GET_NAME
    
    # Create different styles
    styles = create_name_styles(user_name)
    
    # Send the styled names
    response = f"✨ Here's your name in different styles, {user_name}!\n\n"
    response += styles
    
    await update.message.reply_text(response)
    
    # Ask if they want to try another name
    keyboard = [['/start', '/help']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Want to try another name? Use /start to begin again!",
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END

def create_name_styles(name: str) -> str:
    """Generate different text styles for the given name."""
    styles = []
    
    # 1. Normal style
    styles.append(f"🔹 Normal: {name}")
    
    # 2. Uppercase
    styles.append(f"🔸 UPPERCASE: {name.upper()}")
    
    # 3. Lowercase
    styles.append(f"🔹 lowercase: {name.lower()}")
    
    # 4. Title Case
    styles.append(f"🔸 Title Case: {name.title()}")
    
    # 5. Alternating case
    alternating = ''.join(
        char.upper() if i % 2 == 0 else char.lower() 
        for i, char in enumerate(name)
    )
    styles.append(f"🔹 AlTeRnAtInG: {alternating}")
    
    # 6. Reverse
    styles.append(f"🔸 Reverse: {name[::-1]}")
    
    # 7. With emojis
    emoji_name = ' '.join(f"{char}✨" for char in name)
    styles.append(f"🔹 With Emojis: {emoji_name}")
    
    # 8. Spaced out
    spaced = ' '.join(name)
    styles.append(f"🔸 Spaced Out: {spaced}")
    
    return '\n'.join(styles)

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with instructions."""
    help_text = (
        "🤖 Name Styler Bot Help\n\n"
        "• Use /start to begin and enter your name\n"
        "• I'll show your name in different cool styles\n"
        "• You can try as many names as you want!\n\n"
        "Just type /start to begin the fun!"
    )
    await update.message.reply_text(help_text)

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "Operation cancelled. Use /start to begin again!",
        reply_markup=ReplyKeyboardMarkup([['/start']], resize_keyboard=True)
    )
    return ConversationHandler.END

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Exception while handling an update: {context.error}")

# Initialize Flask app for Render web service
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Name Styler Bot is running!"

def run_bot():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    # Start the bot in a separate thread
    import threading
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
