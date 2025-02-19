import time
import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, BotCommand
from config import BOT_TOKEN
import os
import requests
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

# Random images for the start message
random_images = [
    "https://envs.sh/Q_x.jpg",
    "https://envs.sh/Q_y.jpg"
]


@Client.on_message(filters.command("start") & filters.private)
async def account_login(client: Client, message: Message):
    random_image = random.choice(random_images)

    caption = (
        f"> **✨👋🏻 Hey {message.from_user.mention} !!**\n\n"
        "**🔋 I am a powerful bot designed to assist you effortlessly.**\n\n"
        "**🔘 Use the buttons below to learn more about my functions!**"
    )

    buttons = InlineKeyboardMarkup([ 
        [InlineKeyboardButton("🕵 Help", callback_data="help"), InlineKeyboardButton("📜 About", callback_data="about")],
        [InlineKeyboardButton("❗❗ Developer ❗❗", url="https://t.me/Axa_bachha")]
    ])
    
    await client.send_photo(
        chat_id=message.chat.id,
        photo=random_image,
        caption=caption,
        reply_markup=buttons
    )
# ------------------- Bot Uptime ------------------- #
@Client.on_callback_query(filters.regex("uptime"))
async def uptime_callback(client: Client, query: CallbackQuery):
    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = time.strftime("%H hours %M minutes %S seconds", time.gmtime(uptime_seconds))
    
    await query.answer(f"🤖 Bot Uptime: {uptime_str}", show_alert=True)

# ------------------- Help & Modules ------------------- #
HELP_TEXT = "> **📖 My Modules**\n\n**• Choose from the options below.**"
MERGER_TXT = "> **⚙️ Merge PDFs & Images**\n\n📄 **/merge** - Start merging\n✅ **Upload your files**\nType `/done` to merge."
RESTRICTED_TXT = "> **💡 Restricted content saver**\n\n🔒 **Private Chats**\n🌐 **Public Chats**\n📂 **Batch Mode**"
ABOUT_TXT = """**⍟───[ MY ᴅᴇᴛᴀɪʟꜱ ]───⍟\n\n• ᴍʏ ɴᴀᴍᴇ : [z900 ⚝](https://t.me/Z900_robot)\n• ᴍʏ ʙᴇsᴛ ғʀɪᴇɴᴅ : [ᴛʜɪs ᴘᴇʀsᴏɴ](tg://settings)\n• ᴅᴇᴠᴇʟᴏᴘᴇʀ : [ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝](https://t.me/Ur_Amit_01)"""

@Client.on_callback_query(filters.regex("help"))
async def help_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("• Join Request Acceptor •", callback_data="request")],
        [InlineKeyboardButton("📃 PDF Merging 📃", callback_data="combiner")],
        [InlineKeyboardButton("🪄 Restricted Content Saver 🪄", callback_data="restricted")],
        [InlineKeyboardButton("🔙 Back 🔙", callback_data="start")]
    ])
    await callback_query.message.edit_text(HELP_TEXT, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("restricted"))
async def restricted_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help")]])
    await callback_query.message.edit_text(RESTRICTED_TXT, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("combiner"))
async def combiner_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help")]])
    await callback_query.message.edit_text(MERGER_TXT, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("request"))
async def request_info_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    request_text = (
        f"> **⚙️ Join Request Acceptor**\n\n"
        "**• I can accept all pending join requests in your channel. 🤝**\n\n"
        "**• Promote @Axa_bachha and @Z900_RoBot with full admin rights in your channel. 🔑**\n\n"
        "**• Send /accept command to start accepting join requests. ▶️**"
    )
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help")]])
    await callback_query.message.edit_text(request_text, reply_markup=reply_markup, disable_web_page_preview=True)

@Client.on_callback_query(filters.regex("about"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="start"), InlineKeyboardButton("🕒 Uptime", callback_data="uptime")]
    ])
    await callback_query.message.edit_text(ABOUT_TXT, reply_markup=reply_markup, disable_web_page_preview=True)
    
#dgdhgdhcgdjcejchdbchdbcjdhjdhcjdhjcdchf

@Client.on_message(filters.command("stickerid") & filters.private)
async def stickerid(bot, message):
    s_msg = await bot.ask(chat_id=message.from_user.id, text="🌟 Now Send Me Your Sticker 📲")
    if s_msg.sticker:
        await s_msg.reply_text(f"> **Sticker ID is** ✨ \n `{s_msg.sticker.file_id}` \n \n> **Unique ID is** 🔑 \n\n`{s_msg.sticker.file_unique_id}`")
    else: 
        await s_msg.reply_text("Oops !! ❌ Not a sticker file 😕")

#jchfvhfuhcudchuecuegdchuehuchuehccuehucehuc

def upload_image_requests(image_path):
    upload_url = "https://envs.sh"

    try:
        with open(image_path, 'rb') as file:
            files = {'file': file} 
            response = requests.post(upload_url, files=files)

            if response.status_code == 200:
                return response.text.strip() 
            else:
                return print(f"Upload failed with status code {response.status_code}")

    except Exception as e:
        print(f"Error during upload: {e}")
        return None

@Client.on_message(filters.command("telegraph"))
async def telegraph_upload(bot, update):
    t_msg = await bot.ask(chat_id = update.from_user.id, text="📸 **Now Send Me Your Photo Or Video Under 5MB To Get Media Link** 🎥")
    if not t_msg.media:
        return await update.reply_text("❌ **Only Media Supported.** 📲")
    path = await t_msg.download()
    uploading_message = await update.reply_text("<b>⏳ ᴜᴘʟᴏᴀᴅɪɴɢ...</b>")
    try:
        image_url = upload_image_requests(path)
        if not image_url:
            return await uploading_message.edit_text("❌ **Failed to upload file.**")
    except Exception as error:
        await uploading_message.edit_text(f"❌ **Upload failed: {error}**")
        return
    await uploading_message.edit_text(
        text=f"<b>🔗 **Link** :-\n{image_url}</b>",
        disable_web_page_preview=True
    )

#jvgfuchjdchjehcjehjehjhcjehcjehhejchejejf

def convert(text):
    audio = BytesIO()
    i = Translator().translate(text, dest="en")
    lang = i.src
    tts = gTTS(text, lang=lang)
    audio.name = lang + ".mp3"
    tts.write_to_fp(audio)
    return audio


@Client.on_message(filters.command("tts"))
async def text_to_speech(bot, message: Message):
    vj = await bot.ask(chat_id = message.from_user.id, text = "Now send me your text.")
    if vj.text:
        m = await vj.reply_text("Processing")
        text = vj.text
        try:
            loop = get_running_loop()
            audio = await loop.run_in_executor(None, convert, text)
            await vj.reply_audio(audio)
            await m.delete()
            audio.close()
        except Exception as e:
            await m.edit(e)
            e = traceback.format_exc()
            print(e)
    else:
        await vj.reply_text("Send me only text Buddy.")


