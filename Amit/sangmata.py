import logging
import random
import json
from datetime import datetime, timedelta
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
import os

# Get required environment variables
PORT = int(os.environ.get('PORT', '8080'))
TOKEN = os.environ.get('BOT_TOKEN', None)
owner = os.environ.get('OWNER', None)

# Ensure chats.json exists
if not os.path.exists("chats.json"):
    with open("chats.json", "w") as f:
        json.dump([], f)

# Function to log user activity
def logg(m):
    m.forward(owner)
    chat_id = m.chat.id
    with open("chats.json", "r+") as f:
        data = json.load(f)
        f.seek(0)
        if chat_id not in data:
            data.append(chat_id)
        json.dump(data, f)
        f.truncate()

# Function to generate a random date within the past 300 days
def ran_date():
    start = datetime.now()
    end = start + timedelta(days=-300)
    random_date = start + (end - start) * random.random()
    return random_date.strftime("%d/%m/%Y %I:%M:%S")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Setting up the Telegram bot
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

############################# Functions #############################

def helping(update, context):
    logg(update.message)
    help_text = """
**Available Commands:**

1️⃣ `/search_id <user_id>` - Search user details by their ID.  
2️⃣ `/check_name` - Get the name history of a user.  
3️⃣ `/check_username` - Get the username history of a user.  
4️⃣ `/check_brain` - Check if a user has a brain (for fun).  
5️⃣ Forward a message to get user history.
    """
    update.message.reply_text(help_text)

def Forwarded(update, context):
    logg(update.message)
    message = update.message
    if "forward_from" in message.to_dict():
        user = message.forward_from
        message.reply_text(f"""
Name History
👤 {user.id}

1. [{ran_date()}] {user.full_name}
""")

def search_id(update, context):
    logg(update.message)
    message = update.message
    text = message.text
    try:
        id_search = int(text.split(" ")[1])
        user = context.bot.getChat(id_search)
        message.reply_text(f"""
Name History
👤 {user.id}

1. [{ran_date()}] {user.full_name}
""")
    except Exception as e:
        print(e)
        message.reply_text("No records found")

def check_name(update, context):
    logg(update.message)
    message = update.message
    if "reply_to_message" in message.to_dict():
        user = message.reply_to_message.from_user
        mesg = message.reply_to_message
    else:
        user = message.from_user
        mesg = message
    text = f"""
Name History
👤 {user.id}

1. [{ran_date()}] {user.full_name}
    """
    mesg.reply_text(text)

def check_brain(update, context):
    logg(update.message)
    message = update.message
    if "reply_to_message" in message.to_dict():
        message.reply_to_message.reply_text(f"No Brain Found")
    else:
        message.reply_text(f"No Brain Found")

def check_username(update, context):
    logg(update.message)
    message = update.message
    if "reply_to_message" in message.to_dict():
        user = message.reply_to_message.from_user
        mesg = message.reply_to_message
    else:
        user = message.from_user
        mesg = message
    try:
        text = f"""
Username History
👤 {user.id}

1. [{ran_date()}] {user.username}
"""
    except:
        text = f"""
Username History
👤 {user.id}

1. [{ran_date()}] (No Username)
    """
    mesg.reply_text(text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

############################# Handlers #############################

dispatcher.add_handler(MessageHandler(Filters.chat_type.private & Filters.forwarded, Forwarded))
dispatcher.add_handler(CommandHandler("helping", helping))
dispatcher.add_handler(CommandHandler("search_id", search_id))
dispatcher.add_handler(CommandHandler("check_name", check_name))
dispatcher.add_handler(CommandHandler("check_username", check_username))
dispatcher.add_handler(CommandHandler("check_brain", check_brain))
dispatcher.add_error_handler(error)

# Webhook Setup for Koyeb
updater.start_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=TOKEN,
    webhook_url=f"https://{os.environ.get('KOYEB_APP_NAME', 'your-app-name')}.koyeb.app/{TOKEN}",
)

updater.idle()
