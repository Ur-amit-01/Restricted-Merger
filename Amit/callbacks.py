import time
import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, BotCommand
from config import BOT_TOKEN
import os
import requests
import aiohttp
import asyncio
import traceback
from asyncio import get_running_loop
from io import BytesIO
from googletrans import Translator
from gtts import gTTS

# Define the bot's start time
START_TIME = time.time()

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ================== START COMMAND ================== #
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    random_image = random.choice([
        "https://envs.sh/Q_x.jpg",
        "https://envs.sh/Q_y.jpg"
    ])
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🕵 Help", callback_data="help"), 
         InlineKeyboardButton("📜 About", callback_data="about")],
        [InlineKeyboardButton("❗ Developer ❗", url="https://t.me/Axa_bachha")]
    ])
    
    await message.reply_photo(
        photo=random_image,
        caption=f"> **✨👋🏻 Hey {message.from_user.mention}!**\n\nI'm your multi-functional bot!",
        reply_markup=buttons
    )

# ================== TELEGRAPH UPLOAD (NON-BLOCKING) ================== #
async def upload_image(image_path: str) -> str:
    upload_url = "https://envs.sh"
    try:
        async with aiohttp.ClientSession() as session:
            with open(image_path, 'rb') as file:
                data = aiohttp.FormData()
                data.add_field('file', file)
                async with session.post(upload_url, data=data) as resp:
                    return (await resp.text()).strip() if resp.status == 200 else None
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return None

@Client.on_message(filters.command("telegraph") & filters.private)
async def telegraph_handler(client: Client, message: Message):
    msg = await message.reply("📤 **Send me a photo/video...**")
    try:
        media_msg = await client.ask(message.chat.id, "📤 Upload media", timeout=30)
        if not media_msg.media:
            return await msg.edit("❌ Media required")
            
        path = await media_msg.download()
        await msg.edit("⏳ Uploading...")
        url = await upload_image(path)
        await msg.edit(f"🔗 **Link**:\n`{url}`" if url else "❌ Upload failed")
        os.remove(path)
        
    except asyncio.TimeoutError:
        await msg.edit("⌛ Timeout")

# ================== TEXT-TO-SPEECH (ASYNC) ================== #
async def generate_tts(text: str) -> BytesIO:
    loop = get_running_loop()
    audio = BytesIO()
    def sync_tts():
        tts = gTTS(text, lang=Translator().translate(text, dest="en").src)
        tts.write_to_fp(audio)
        return audio
    audio = await loop.run_in_executor(None, sync_tts)
    audio.seek(0)
    return audio

@Client.on_message(filters.command("tts") & filters.private)
async def tts_handler(client: Client, message: Message):
    msg = await message.reply("💬 **Send text...**")
    try:
        text_msg = await client.ask(message.chat.id, "💬 Enter text", timeout=30)
        if not text_msg.text:
            return await msg.edit("❌ Text required")
            
        await msg.edit("🔊 Generating...")
        audio = await generate_tts(text_msg.text)
        await client.send_audio(message.chat.id, audio)
        await msg.delete()
        
    except asyncio.TimeoutError:
        await msg.edit("⌛ Timeout")

# ================== CALLBACKS ================== #


    
