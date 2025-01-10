from pyrogram import Client, filters
from pyrogram.types import Message
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    logger.info(f"/start command triggered by user {message.from_user.id}")
    await client.send_message(
        chat_id=message.chat.id,
        text=(
            "<b>✨👋 Hey {mention}, Welcome!</b>\n"
            "<i>I am a powerful bot designed to assist you effortlessly.</i>\n\n"
            "> **Here’s what I can do for you: 👇🏻🤖**\n\n"
            "📌 <b>Send restricted content by its post link.</b>\n"
            "📌 <b>Merge multiple PDFs into a single file.</b>\n\n"
            "⚙️ <b>Need help ?? use /help</b>\n\n"
            "> **👨‍💻 Dᴇᴠᴇʟᴏᴘᴇʀ : [ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝](https://t.me/Ur_Amit_01)**"
        ).format(mention=message.from_user.mention),
        disable_web_page_preview=True
    )

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    logger.info(f"/help command triggered by user {message.from_user.id}")
    await client.send_message(
        chat_id=message.chat.id,
        text="<b>Here are the available commands:</b>\n"
             "/start - Start the bot\n"
             "/help - Show help message\n"
             "/cancel - Cancel current operation",
        disable_web_page_preview=True
    )
