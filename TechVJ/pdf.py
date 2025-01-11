import os
import logging
import asyncio
from PIL import Image
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from PyPDF2 import PdfMerger
from pyrogram.types import Message
import tempfile
import concurrent.futures

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
user_file_collection = {}  # Store file IDs for each user
pending_filename_requests = {}

# Thread pool executor for concurrent tasks
executor = concurrent.futures.ThreadPoolExecutor()

async def process_pdf(client, user_id, file_id, temp_pdf_files):
    """Async function to download and process PDF"""
    temp_file = await client.download_media(file_id)
    temp_pdf_files.append(temp_file)

def process_image_to_pdf(image_path, temp_image_files):
    """Function to convert image to PDF (run in a separate thread to avoid blocking)"""
    with Image.open(image_path) as img:
        img.convert("RGB").save(image_path, "PDF")
        temp_image_files.append(image_path)

# Handle the /merge command
@Client.on_message(filters.command(["merge"]))
async def start_file_collection(client: Client, message: Message):
    user_id = message.from_user.id
    user_file_collection[user_id] = {"pdfs": [], "images": []}
    await message.reply_text(
        "🔄 Ready to start! Send your PDFs 📑 and images 🖼️ one by one. When you're ready, type /done ✅ to merge them into one PDF. 🌟"
    )

# Handle PDF files
@Client.on_message(filters.document & filters.private)
async def handle_pdf(client: Client, message: Message):
    user_id = message.from_user.id
    document = message.document

    if document.mime_type != "application/pdf":
        await message.reply_text("❌ This is not a valid PDF file. Please send a PDF 📑.")
        return

    if document.file_size > MAX_FILE_SIZE:
        await message.reply_text(
            "🚫 File size is too large! Please send a PDF smaller than 20MB."
        )
        return

    if user_id not in user_file_collection:
        await message.reply_text("⏳ Please start the merging process first by using /merge 🔄.")
        return

    if len(user_file_collection[user_id]["pdfs"]) >= 20:
        await message.reply_text(
            "⚠️ You can only upload up to 20 PDFs. Type /done ✅ to merge them."
        )
        return

    user_file_collection[user_id]["pdfs"].append(document.file_id)
    await message.reply_text(
        f"➕ PDF queued! 📄 ({len(user_file_collection[user_id]['pdfs'])} PDFs added so far.)"
    )

# Handle image files
@Client.on_message(filters.photo & filters.private)
async def handle_image(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_collection:
        await message.reply_text("⏳ Please start the merging process first by using /merge 🔄.")
        return

    user_file_collection[user_id]["images"].append(message.photo.file_id)
    await message.reply_text(
        f"➕ Image queued! 🖼️ ({len(user_file_collection[user_id]['images'])} images added so far.)"
    )

# Handle /done command
@Client.on_message(filters.command(["done"]))
async def merge_files(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_collection or (
        not user_file_collection[user_id]["pdfs"]
        and not user_file_collection[user_id]["images"]
    ):
        await message.reply_text("⚠️ Please upload at least one PDF or image before using /done.")
        return

    await message.reply_text("✍️ Type a name for your merged PDF (without extension).")
    pending_filename_requests[user_id] = True

# Handle the filename text input
@Client.on_message(filters.text & filters.private)
async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in pending_filename_requests:
        return

    filename = message.text.strip().replace("/", "_").replace("\\", "_")
    if not filename:
        await message.reply_text("❌ Invalid filename. Please try again.")
        return

    await message.reply_text("🔄 Downloading files and merging... Please wait.")
    try:
        output_file = os.path.join(tempfile.gettempdir(), f"{filename}.pdf")
        merger = PdfMerger()

        # Download and merge PDFs asynchronously
        temp_pdf_files = []
        tasks = []
        for file_id in user_file_collection[user_id]["pdfs"]:
            tasks.append(process_pdf(client, user_id, file_id, temp_pdf_files))

        # Convert images to PDFs in separate threads
        temp_image_files = []
        for file_id in user_file_collection[user_id]["images"]:
            image_path = await client.download_media(file_id)
            tasks.append(asyncio.to_thread(process_image_to_pdf, image_path, temp_image_files))

        await asyncio.gather(*tasks)

        # Merging PDFs
        for pdf_file in temp_pdf_files:
            merger.append(pdf_file)

        # Merging image PDFs
        for img_file in temp_image_files:
            merger.append(img_file)

        # Save the merged PDF
        merger.write(output_file)
        merger.close()

        # Send the merged PDF to the user
        await client.send_document(
            chat_id=user_id,
            document=output_file,
            caption="🎉 Here is your merged PDF!",
            file_name=f"{filename}.pdf",
        )

    except FloodWait as e:
        logger.error(f"FloodWait error occurred: Must wait {e.x} seconds before retrying.")
        await asyncio.sleep(e.x)  # Wait for the specified time
        await message.reply_text("⚠️ Bot is temporarily flooded with requests. Please try again shortly.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await message.reply_text(f"❌ Failed to merge files: {e}")
    finally:
        # Clean up temporary files after processing
        for pdf_file in temp_pdf_files:
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
        for img_file in temp_image_files:
            if os.path.exists(img_file):
                os.remove(img_file)
        if os.path.exists(output_file):
            os.remove(output_file)

        # Clear the user session data
        user_file_collection.pop(user_id, None)
        pending_filename_requests.pop(user_id, None)

