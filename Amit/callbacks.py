import logging
import random
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from config import BOT_TOKEN

# Define the bot's start time
START_TIME = time.time()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

random_images = [
    "https://envs.sh/Q_x.jpg",
    "https://envs.sh/Q_x.jpg"
]

# ------------------- Set Commands ------------------- #

OWNER_ID = 6803505727

@Client.on_message(filters.command("set"))
async def set(client, message):
    if message.from_user.id != OWNER_ID:
        await message.reply("You are not authorized to use this command.")
        return

    # Setting all the bot commands
    await client.set_bot_commands([
        BotCommand("start", "🚀 Start the bot and view the welcome message"),
        BotCommand("merge", "📎 Merge multiple PDFs or images into a single PDF"),
        BotCommand("done", "✅ Complete the merging process"),
        BotCommand("stickerid", "🆔 Get sticker ID (For Developers)"),
        BotCommand("telegraph", "🔗 Get a Telegraph link for media"),
        BotCommand("tts", "🗣️ Convert text to speech"),
        BotCommand("accept", "✔️ Accept all pending join requests in your channel"),
    ])    
    await message.reply("✅ Commands configured successfully!")

# ------------------- Start ------------------- #

@Client.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    random_image = random.choice(random_images)
    caption = (
        f"> **✨👋🏻 Hey {message.from_user.mention} !!**\n\n"
        "**🔋 I am a powerful bot designed to assist you effortlessly.**\n\n"
        "**🔘 Use the buttons below to learn more about my functions!**"
    )

    buttons = InlineKeyboardMarkup([ 
        [InlineKeyboardButton("❗❗ Developer ❗❗", url="https://t.me/Axa_bachha")]
    ])
    
    await client.send_photo(
        chat_id=message.chat.id,
        photo=random_image,
        caption=caption,
        reply_markup=buttons
    )
