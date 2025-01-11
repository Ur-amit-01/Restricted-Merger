import os
import logging
import asyncio
from PIL import Image
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from PyPDF2 import PdfMerger
from pyrogram.types import Message
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
MAX_FILES = 20  # Maximum files per session
user_file_collection = {}  # Store file IDs for each user session
pending_filename_requests = {}

# Start /merge command
@Client.on_message(filters.command(["merge"]) & filters.private)
async def start_file_collection(client: Client, message: Message):
    user_id = message.from_user.id
    user_file_collection[user_id] = {"pdfs": [], "images": []}
    await message.reply_text(
        "✅ Merge process started! Send your PDFs 📑 and images 🖼️ one by one. When ready, type /done to combine them."
    )

# Handle PDF files
@Client.on_message(filters.document & filters.private)
async def handle_pdf(client: Client, message: Message):
    user_id = message.from_user.id
    document = message.document

    if document.mime_type != "application/pdf":
        await message.reply_text("❌ This is not a PDF file. Please send a valid PDF.")
        return

    if document.file_size > MAX_FILE_SIZE:
        await message.reply_text("🚫 File too large! Maximum allowed size is 20MB.")
        return

    if user_id not in user_file_collection:
        await message.reply_text("⚠️ Start the merge process using /merge first.")
        return

    if len(user_file_collection[user_id]["pdfs"]) >= MAX_FILES:
        await message.reply_text("⚠️ Maximum limit reached! Type /done to merge.")
        return

    user_file_collection[user_id]["pdfs"].append(document.file_id)
    await message.reply_text(f"➕ PDF added! Total PDFs: {len(user_file_collection[user_id]['pdfs'])}.")

# Handle images
@Client.on_message(filters.photo & filters.private)
async def handle_image(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_collection:
        await message.reply_text("⚠️ Start the merge process using /merge first.")
        return

    user_file_collection[user_id]["images"].append(message.photo.file_id)
    await message.reply_text(f"➕ Image added! Total images: {len(user_file_collection[user_id]['images'])}.")

# Finalize /done command
@Client.on_message(filters.command(["done"]) & filters.private)
async def finalize_merge(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_collection or (
        not user_file_collection[user_id]["pdfs"]
        and not user_file_collection[user_id]["images"]
    ):
        await message.reply_text("⚠️ No files added. Use /merge to start the process.")
        return

    await message.reply_text("✍️ Please provide a name for your merged PDF.")
    pending_filename_requests[user_id] = True

# Handle filename input
@Client.on_message(filters.text & filters.private)
async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in pending_filename_requests:
        return

    filename = message.text.strip().replace("/", "_").replace("\\", "_")
    if not filename:
        await message.reply_text("❌ Invalid filename. Try again.")
        return

    await message.reply_text("🔄 Merging files. Please wait...")
    try:
        output_file = os.path.join(tempfile.gettempdir(), f"{filename}.pdf")
        merger = PdfMerger()

        # Download and merge PDFs
        temp_files = []
        for file_id in user_file_collection[user_id]["pdfs"]:
            temp_file = await client.download_media(file_id)
            merger.append(temp_file)
            temp_files.append(temp_file)

        # Download and convert images to PDFs
        for file_id in user_file_collection[user_id]["images"]:
            image_file = await client.download_media(file_id)
            with Image.open(image_file) as img:
                pdf_path = f"{image_file}.pdf"
                img.convert("RGB").save(pdf_path)
                merger.append(pdf_path)
                temp_files.append(pdf_path)

        # Save merged PDF
        merger.write(output_file)
        merger.close()

        # Send merged PDF to user
        await client.send_document(
            chat_id=user_id,
            document=output_file,
            caption="🎉 Here is your merged PDF!",
            file_name=f"{filename}.pdf",
        )

    except FloodWait as e:
        logger.warning(f"FloodWait: Bot paused for {e.x} seconds.")
        await asyncio.sleep(e.x)
        await message.reply_text("⚠️ Please try again later.")
    except Exception as e:
        logger.error(f"Merge error: {e}")
        await message.reply_text("❌ An error occurred during the merging process.")
    finally:
        # Clean up temporary files
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists(output_file):
            os.remove(output_file)

        # Clear session data
        user_file_collection.pop(user_id, None)
        pending_filename_requests.pop(user_id, None)


