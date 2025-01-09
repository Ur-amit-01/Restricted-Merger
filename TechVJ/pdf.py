
user_pdf_collection = {}
pending_filename = {}

@Client.on_message(filters.command(["merge"]))
async def start_pdf_collection(client: Client, message: Message):
    user_id = message.from_user.id
    user_pdf_collection[user_id] = []  # Initialize an empty list for storing PDF files
    await message.reply_text(
        "Send me the PDFs you want to merge, one by one. When you're done, send /done."
    )

@Client.on_message(filters.command(["done"]))
async def ask_for_filename(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in user_pdf_collection or len(user_pdf_collection[user_id]) < 2:
        await message.reply_text(
            "You need to send at least 2 PDFs before using /done. Use /merge to start over."
        )
        return
    
    pending_filename[user_id] = True  # Indicate the bot is waiting for a filename
    await message.reply_text(
        "Please reply with the filename (without .pdf) you'd like for the merged PDF."
    )
