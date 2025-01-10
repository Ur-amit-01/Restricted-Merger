import os
import logging   
import asyncio
from PIL import Image
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from pyrogram.types import Message
import tempfile

logger = logging.getLogger(__name__)

# user_pdf_collection = {}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
pending_filename_requests = {}

user_file_collection = {}  # Store PDFs and images separately for each user

@Client.on_message(filters.command(["merge"]))
async def start_file_collection(client: Client, message: Message):
    logger.info(f"/merge command triggered by user {message.from_user.id}")
    user_id = message.from_user.id
    user_file_collection[user_id] = {"pdfs": [], "images": []}  # Separate lists for PDFs and images
    await message.reply_text(
        "Now, send your PDFs 📑 and images 🖼️ one by one. Use /done ✅ to merge them into a single PDF."
    )

@Client.on_message(filters.document & filters.private)
async def handle_pdf(client: Client, message: Message):
    user_id = message.from_user.id

    if message.document.mime_type != "application/pdf":
        await message.reply_text("This is not a valid PDF file.")
        return

    if user_id not in user_file_collection:
        await message.reply_text(
            "To begin merging your files, please start the process by /merge. 🔄"
        )
        return

    if len(user_file_collection[user_id]["pdfs"]) >= 20:
        await message.reply_text(
            "You can only upload up to 20 PDFs for merging. Send /done to merge the files."
        )
        return

    if message.document.file_size > MAX_FILE_SIZE:
        await message.reply_text(
            "The file is too large. Please send a PDF smaller than 20MB."
        )
        return

    try:
        temp_file = await message.download()  
        user_file_collection[user_id]["pdfs"].append(temp_file)

        await message.reply_text(
            f"➥ PDF added! ({len(user_file_collection[user_id]['pdfs'])} PDFs added so far.)"
            " Send more files or use /done to merge them."
        )
    except Exception as e:
        await message.reply_text(f"❌ Failed to upload the PDF: {e}")

@Client.on_message(filters.photo & filters.private)
async def handle_image(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_collection:
        await message.reply_text(
            "To begin merging your files, please start the process by /merge. 🔄"
        )
        return

    try:
        temp_file = await message.download()  
        user_file_collection[user_id]["images"].append(temp_file)

        await message.reply_text(
            f"➥ Image added! ({len(user_file_collection[user_id]['images'])} images added so far.)"
            " Send more files or use /done to merge them."
        )
    except Exception as e:
        await message.reply_text(f"❌ Failed to upload the image: {e}")

@Client.on_message(filters.command(["done"]))
async def merge_files(client: Client, message: Message):
    logger.info(f"/done command triggered by user {message.from_user.id}")
    user_id = message.from_user.id

    if user_id not in user_file_collection or (
        len(user_file_collection[user_id]["pdfs"]) < 1 
        and len(user_file_collection[user_id]["images"]) < 1
    ):
        await message.reply_text(
            "Send at least one PDF 📑 or image 🖼️ before using /done. Start fresh with /merge 🔄."
        )
        return

    await message.reply_text(
        "Send the name for your merged PDF 📄 (no extension) ✍️."
    )
    pending_filename_requests[user_id] = True

@Client.on_message(filters.text & filters.private & ~filters.regex("https://t.me/"))
async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in pending_filename_requests:
        return  

    custom_filename = message.text.strip()
    if not custom_filename:  
        await message.reply_text("Filename cannot be empty. Please try again.")
        return

    custom_filename = os.path.splitext(custom_filename)[0]
    custom_filename = custom_filename.replace("/", "_").replace("\\", "_").strip()

    if not custom_filename:  
        await message.reply_text("Invalid filename. Please try again.")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        output_file = temp_file.name

    try:
        # Merge PDFs
        merger = PdfMerger()
        for pdf in user_file_collection[user_id]["pdfs"]:
            merger.append(pdf)

        # Convert images to PDFs and add them
        for img_path in user_file_collection[user_id]["images"]:
            image = Image.open(img_path)
            image = image.convert("RGB")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as img_pdf:
                image.save(img_pdf.name, "PDF")
                merger.append(img_pdf.name)

        merger.write(output_file)
        merger.close()

        await client.send_document(
            chat_id=message.chat.id,
            document=output_file,
            caption=f"Here is your merged PDF. ✅",
            file_name=f"{custom_filename}.pdf",
        )

        await message.reply_text("Your files have been successfully merged!")

    except Exception as e:
        await message.reply_text(f"Failed to merge files: {e}")

    finally:
        # Clean up temporary files
        for pdf in user_file_collection[user_id]["pdfs"]:
            if os.path.exists(pdf):
                os.remove(pdf)
        for img in user_file_collection[user_id]["images"]:
            if os.path.exists(img):
                os.remove(img)
        if os.path.exists(output_file):
            os.remove(output_file)

        user_file_collection.pop(user_id, None)
        pending_filename_requests.pop(user_id, None)
