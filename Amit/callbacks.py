import time
import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================== START COMMAND ================== #
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    # Random image for the start message
    random_image = random.choice([
        "https://envs.sh/Q_x.jpg",
        "https://envs.sh/Q_y.jpg"
    ])
    
    # Buttons for the start message
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🕵 Help", callback_data="help"), 
         InlineKeyboardButton("📜 About", callback_data="about")],
        [InlineKeyboardButton("❗ Developer ❗", url="https://t.me/Axa_bachha")]
    ])
    
    # Send the start message with photo and buttons
    await message.reply_photo(
        photo=random_image,
        caption = (
        f"> **✨👋🏻 Hey {message.from_user.mention} !!**\n\n"
        "**🔋 I am a powerful bot designed to assist you effortlessly.**\n\n"
        "**🔘 Use the buttons below to learn more about my functions!**"
        ),
        reply_markup=buttons
    )

# ================== START THE BOT ================== #
