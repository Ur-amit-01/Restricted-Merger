import os
import logging
import asyncio
from PIL import Image
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from pyrogram.types import Message
import tempfile

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
MAX_CONCURRENT_TASKS = 5  # Limit concurrent image processing tasks
pending_filename_requests = {}
user_file_collection = {}  # Store PDFs and images separately for each user

semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)  # Control concurrent tasks


@Client.on_message(filters.command(["merge"]))
async def start_file_collection(client: Client, message: Message):
    logger.info(f"/merge command triggered by user {message.from_user.id}")
    user_id = message.from_user.id
    user_file_collection[user_id] = {"pdfs": [], "images": []}
    await message.reply_text(
        "Sᴇɴᴅ ʏᴏᴜʀ ᴘᴅғs 📑/ ɪᴍᴀɢᴇs 🖼️ ᴏɴᴇ ʙʏ ᴏɴᴇ. Wʜᴇɴ ʏᴏᴜ'ʀᴇ ʀᴇᴀᴅʏ ᴛʏᴘᴇ /done ✅ ᴛᴏ ᴍᴇʀɢᴇ ᴛʜᴇᴍ ɪɴᴛᴏ ᴘᴅғ. 🌟"
    )


@Client.on_message(filters.command(["done"]))
async def merge_files(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_collection or (
        len(user_file_collection[user_id]["pdfs"]) < 1
        and len(user_file_collection[user_id]["images"]) < 1
    ):
        await message.reply_text(
            "⚠️ Please send at least one PDF 📑 or image 🖼️ before using /done ✅."
        )
        return

    await message.reply_text("✍️ Type a name for your merged PDF 📄 (without extension).")
    pending_filename_requests[user_id] = {"filename_request": True}


@Client.on_message(filters.text & filters.private & ~filters.regex("https://t.me/"))
async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in pending_filename_requests or not pending_filename_requests[user_id]["filename_request"]:
        return

    custom_filename = message.text.strip()
    if not custom_filename:
        await message.reply_text("❌ Filename cannot be empty. Please try again.")
        return

    custom_filename = os.path.splitext(custom_filename)[0].replace("/", "_").replace("\\", "_").strip()

    if not custom_filename:
        await message.reply_text("❌ Invalid filename. Please try again.")
        return

    # Send the "Merging your files..." message and save its response
    progress_message = await message.reply_text("🛠️ Merging your files... Please wait... 🔄")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            output_file = temp_file.name

        merger = PdfMerger()

        # Merge PDFs
        for pdf in user_file_collection[user_id]["pdfs"]:
            merger.append(pdf)

        # Process images concurrently
        tasks = [
            process_image_to_pdf(img_path, merger)
            for img_path in user_file_collection[user_id]["images"]
        ]
        await asyncio.gather(*tasks)

        merger.write(output_file)
        merger.close()

        # Send the merged PDF to the user
        await client.send_document(
            chat_id=message.chat.id,
            document=output_file,
            caption="🎉 Here is your merged PDF 📄.",
            file_name=f"{custom_filename}.pdf",
        )

        # Delete the "Merging your files..." message
        await progress_message.delete()
        await message.reply_text("✅ Your files have been successfully merged! 🎊")

    except Exception as e:
        logger.error(f"Error during merging: {e}")
        await progress_message.delete()
        await message.reply_text(f"❌ Failed to merge files: {e}")

    finally:
        # Cleanup temporary files
        for file_path in user_file_collection[user_id]["pdfs"] + user_file_collection[user_id]["images"]:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists(output_file):
            os.remove(output_file)
        user_file_collection.pop(user_id, None)
        pending_filename_requests.pop(user_id, None)

