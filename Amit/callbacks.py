import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== START COMMAND ================== #
@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_photo(
        photo="https://envs.sh/Q_x.jpg",  # Replace with your picture URL
        caption=f"Hey {message.from_user.mention}!\nWelcome to the bot.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Developer", url="https://t.me/Axa_bachha")]
        ])
    )
