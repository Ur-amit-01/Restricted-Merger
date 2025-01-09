from pyrogram import Client, filters
from pyrogram.types import Message
import logging

logger = logging.getLogger(__name__)

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    logger.info(f"/start command triggered by user {message.from_user.id}")
    await client.send_message(
        chat_id=message.chat.id,
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot. I can send you restricted content by its post link.\n\nKnow how to use bot by - /help</b>\n\n> **👨‍💻 Dᴇᴠᴇʟᴏᴘᴇʀ : [ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝](https://t.me/Ur_Amit_01)**",
        reply_to_message_id=message.id,
        disable_web_page_preview=True
    )

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    logger.info(f"/help command triggered by user {message.from_user.id}")
    await client.send_message(
        chat_id=message.chat.id,
        text=f"{HELP_TXT}",
        disable_web_page_preview=True
    )
