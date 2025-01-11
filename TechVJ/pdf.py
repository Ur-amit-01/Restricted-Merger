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
pending_filename_requests = {}
user_file_collection = {}  # Store PDFs and images separately for each user

def to_small_caps(text):
    small_caps_map = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    return text.translate(small_caps_map)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
pending_filename_requests = {}
user_file_collection = {}  # Store PDFs and images separately for each user

@Client.on_message(filters.command(["merge"]))
async def start_file_collection(client: Client, message: Message):
    logger.info(f"/merge command triggered by user {message.from_user.id}")
    user_id = message.from_user.id
    user_file_collection[user_id] = {"pdfs": [], "images": []}  # Separate lists for PDFs and images
    await message.reply_text(
        to_small_caps("🔄 ready to start! send your pdfs 📑 and images 🖼️ one by one. when you're ready, type /done ✅ to merge them into one pdf. 🌟")
    )

@Client.on_message(filters.document & filters.private)
async def handle_pdf(client: Client, message: Message):
    user_id = message.from_user.id

    if message.document.mime_type != "application/pdf":
        await message.reply_text(to_small_caps("❌ this is not a valid pdf file. please send a pdf 📑."))
        return

    if user_id not in user_file_collection:
        await message.reply_text(
            to_small_caps("⏳ please start the merging process first by using /merge 🔄.")
        )
        return

    if len(user_file_collection[user_id]["pdfs"]) >= 20:
        await message.reply_text(
            to_small_caps("⚠️ you can only upload up to 20 pdfs. type /done ✅ to merge them.")
        )
        return

    if message.document.file_size > MAX_FILE_SIZE:
        await message.reply_text(
            to_small_caps("🚫 file size is too large! please send a pdf smaller than 20mb.")
        )
        return

    try:
        temp_file = await message.download()  
        user_file_collection[user_id]["pdfs"].append(temp_file)

        await message.reply_text(
            to_small_caps(f"➕ pdf added! 📄 ({len(user_file_collection[user_id]['pdfs'])} pdfs added so far.)\n"
                          "send more files or use /done ✅ to merge them.")
        )
    except Exception as e:
        await message.reply_text(to_small_caps(f"❌ failed to upload the pdf: {e}"))

@Client.on_message(filters.photo & filters.private)
async def handle_image(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_collection:
        await message.reply_text(
            to_small_caps("⏳ please start the merging process first by using /merge 🔄.")
        )
        return

    try:
        temp_file = await message.download()  
        user_file_collection[user_id]["images"].append(temp_file)

        await message.reply_text(
            to_small_caps(f"➕ image added! 🖼️ ({len(user_file_collection[user_id]['images'])} images added so far.)\n"
                          "send more files or use /done ✅ to merge them.")
        )
    except Exception as e:
        await message.reply_text(to_small_caps(f"❌ failed to upload the image: {e}"))

@Client.on_message(filters.command(["done"]))
async def merge_files(client: Client, message: Message):
    logger.info(f"/done command triggered by user {message.from_user.id}")
    user_id = message.from_user.id

    if user_id not in user_file_collection or (
        len(user_file_collection[user_id]["pdfs"]) < 1 
        and len(user_file_collection[user_id]["images"]) < 1
    ):
        await message.reply_text(
            to_small_caps("⚠️ please send at least one pdf 📑 or image 🖼️ before using /done ✅. start fresh with /merge 🔄.")
        )
        return

    await message.reply_text(
        to_small_caps("✍️ type a name for your merged pdf 📄 (without extension).")
    )
    pending_filename_requests[user_id] = {"filename_request": True}

@Client.on_message(filters.text & filters.private & ~filters.regex("https://t.me/"))
async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in pending_filename_requests or not pending_filename_requests[user_id]["filename_request"]:
        return  

    custom_filename = message.text.strip()
    if not custom_filename:  
        await message.reply_text(to_small_caps("❌ filename cannot be empty. please try again."))
        return

    custom_filename = os.path.splitext(custom_filename)[0]
    custom_filename = custom_filename.replace("/", "_").replace("\\", "_").strip()

    if not custom_filename:  
        await message.reply_text(to_small_caps("❌ invalid filename. please try again."))
        return

    # Send initial message that the merging is starting
    merge_message = await message.reply_text(
        to_small_caps("🛠️ merging your files... please wait... 🔄")
    )
    
    try:
        # Use a NamedTemporaryFile for the output PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            output_file = temp_file.name

        # Merge PDFs and images asynchronously
        merger = PdfMerger()

        # Merge PDF files
        for pdf in user_file_collection[user_id]["pdfs"]:
            merger.append(pdf)
        # Convert images to PDFs and add them
        tasks = []
        for img_path in user_file_collection[user_id]["images"]:
            tasks.append(convert_image_to_pdf(img_path, merger))

        # Wait for all image-to-PDF conversions
        await asyncio.gather(*tasks)

        # Write the merged output PDF
        merger.write(output_file)
        merger.close()

        # Send the merged PDF to the user
        await client.send_document(
            chat_id=message.chat.id,
            document=output_file,
            caption=to_small_caps(f"🎉 here is your merged pdf 📄."),
            file_name=f"{custom_filename}.pdf",
        )

        # After sending the merged file, delete the merging message
        await merge_message.delete()
        await message.reply_text(to_small_caps("✅ your files have been successfully merged! 🎊"))

    except Exception as e:
        await merge_message.edit_text(to_small_caps(f"❌ failed to merge files: {e}"))

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

# Helper function to convert images to PDFs asynchronously
async def convert_image_to_pdf(img_path, merger):
    try:
        image = Image.open(img_path)
        image = image.convert("RGB")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as img_pdf:
            image.save(img_pdf.name, "PDF")
            merger.append(img_pdf.name)
    except Exception as e:
        logger.error(f"Error converting image {img_path} to PDF: {e}")

