import os
from pyrogram import Client, filters
from PyPDF2 import PdfMerger

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

bot = Client("PDFGenieBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

user_files = {}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

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
