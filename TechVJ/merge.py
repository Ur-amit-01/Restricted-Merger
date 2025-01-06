import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from PyPDF2 import PdfMerger

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

bot = Client("PDFGenieBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

ABOUT_TXT = """<b><blockquote>⍟───[ MY ᴅᴇᴛᴀɪʟꜱ ]───⍟</blockquote>
‣ ᴍʏ ɴᴀᴍᴇ : <a href='https://t.me/PDF_Genie_Robot'>PDF Genie</a>
‣ ᴍʏ ʙᴇsᴛ ғʀɪᴇɴᴅ : <a href='tg://settings'>ᴛʜɪs ᴘᴇʀsᴏɴ</a> 
‣ ᴅᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://t.me/Ur_amit_01'>ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝</a> 
‣ ʟɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>ᴘʏʀᴏɢʀᴀᴍ</a> 
‣ ʟᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/download/releases/3.0/'>ᴘʏᴛʜᴏɴ 3</a> 
‣ ᴅᴀᴛᴀ ʙᴀsᴇ : <a href='https://www.mongodb.com/'>ᴍᴏɴɢᴏ ᴅʙ</a> 
‣ ʙᴜɪʟᴅ sᴛᴀᴛᴜs : ᴠ2.7.1 [sᴛᴀʙʟᴇ]</b>"""

user_files = {}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

# Command: Start
@bot.on_message(filters.command("start"))
async def start(client, message):
    sticker_id = "CAACAgUAAxkBAAECEpdnLcqQbmvQfCMf5E3rBK2dkgzqiAACJBMAAts8yFf1hVr67KQJnh4E"
    sent_sticker = await message.reply_sticker(sticker_id)
    await sent_sticker.delete()

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("«ʜᴇʟᴘ» 🕵️", callback_data="help"),
         InlineKeyboardButton("«ᴀʙᴏᴜᴛ» 📄", callback_data="about")],
        [InlineKeyboardButton("•Dᴇᴠᴇʟᴏᴘᴇʀ• ☘", url="https://t.me/Ur_amit_01")]
    ])

    image_url = "https://graph.org/file/0f1d046b4b3899e1812bf-0e63e80abb1bef1a8b.jpg"
    await message.reply_photo(
        image_url,
        caption=("Aʜ, ᴀ ɴᴇᴡ ᴛʀᴀᴠᴇʟᴇʀ ʜᴀs ᴀʀʀɪᴠᴇᴅ... "
                 "Wᴇʟᴄᴏᴍᴇ ᴛᴏ ᴍʏ ᴍᴀɢɪᴄᴀʟ ʀᴇᴀʟᴍ !🧞‍♂️✨\n\n"
                 "• I ᴀᴍ PDF ɢᴇɴɪᴇ, ɪ ᴡɪʟʟ ɢʀᴀɴᴛ ʏᴏᴜʀ ᴘᴅғ ᴡɪsʜᴇs! 📑🪄"),
        reply_markup=markup
    )

# Callback Query Handler
@bot.on_callback_query()
async def callback(client, query):
    if query.data == "help":
        await query.message.edit_text(
            "This bot helps you merge PDF files. Here's how to use it:\n"
            "1. Send me PDF files.\n"
            "2. Use /merge when you're ready.\n"
            "3. Max file size is 20 MB.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])
        )
    elif query.data == "about":
        await query.message.edit_text(
            ABOUT_TXT,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])
        )
    elif query.data == "back":
        await query.message.edit_text(
            "Welcome back! Use the buttons below to navigate.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("«ʜᴇʟᴘ» 🕵️", callback_data="help"),
                 InlineKeyboardButton("«ᴀʙᴏᴜᴛ» 📄", callback_data="about")],
                [InlineKeyboardButton("•Dᴇᴠᴇʟᴏᴘᴇʀ• ☘", url="https://t.me/Ur_amit_01")]
            ])
        )

# Command: Help
@bot.on_message(filters.command("help"))
async def help(client, message):
    await message.reply(
        "This bot helps you merge PDF files. Here's how to use it:\n"
        "1. Send me PDF files.\n"
        "2. Use /merge when you're ready.\n"
        "3. Max file size is 20 MB."
    )

# Command: Merge
@bot.on_message(filters.command("merge"))
async def merge(client, message):
    user_id = message.from_user.id
    if user_id not in user_files or len(user_files[user_id]) < 2:
        await message.reply("Please send at least two PDF files to merge.")
        return

    merger = PdfMerger()
    for pdf in user_files[user_id]:
        merger.append(pdf)
    merged_file = f"{user_id}_merged.pdf"
    with open(merged_file, "wb") as f:
        merger.write(f)

    await message.reply_document(merged_file)
    os.remove(merged_file)
    user_files[user_id] = []

# Command: Clear
@bot.on_message(filters.command("clear"))
async def clear(client, message):
    user_id = message.from_user.id
    if user_id in user_files:
        for file in user_files[user_id]:
            os.remove(file)
        user_files[user_id] = []
    await message.reply("Your files have been cleared.")

# Document Handler
@bot.on_message(filters.document)
async def document(client, message):
    if message.document.mime_type == "application/pdf":
        if message.document.file_size > MAX_FILE_SIZE:
            await message.reply("File size exceeds 20 MB limit.")
            return

        user_id = message.from_user.id
        if user_id not in user_files:
            user_files[user_id] = []

        file_path = await bot.download_media(message.document)
        user_files[user_id].append(file_path)
        await message.reply(f"Added {message.document.file_name} to the list for merging.")
    else:
        await message.reply("Please send a valid PDF file.")

# Run the bot
bot.run()
