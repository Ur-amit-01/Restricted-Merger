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

@Client.on_message(filters.command(["merge"]))
async def start_file_collection(client: Client, message: Message):
    logger.info(f"/merge command triggered by user {message.from_user.id}")
    user_id = message.from_user.id
    user_file_collection[user_id] = {"pdfs": [], "images": []}  # Separate lists for PDFs and images
    await message.reply_text(
        "🔄 Ready to start! Send your PDFs 📑 and images 🖼️ one by one. When you're ready, type /done ✅ to merge them into one PDF. 🌟"
    )

@Client.on_message(filters.document & filters.private)
async def handle_pdf(client: Client, message: Message):
    user_id = message.from_user.id

    if message.document.mime_type != "application/pdf":
        await message.reply_text("❌ This is not a valid PDF file. Please send a PDF 📑.")
        return

    if user_id not in user_file_collection:
        await message.reply_text(
            "⏳ Please start the merging process first by using /merge 🔄."
        )
        return

    if len(user_file_collection[user_id]["pdfs"]) >= 20:
        await message.reply_text(
            "⚠️ You can only upload up to 20 PDFs. Type /done ✅ to merge them."
        )
        return

    if message.document.file_size > MAX_FILE_SIZE:
        await message.reply_text(
            "🚫 File size is too large! Please send a PDF smaller than 20MB."
        )
        return

    try:
        temp_file = await message.download()  
        user_file_collection[user_id]["pdfs"].append(temp_file)

        await message.reply_text(
            f"➕ PDF added! 📄 ({len(user_file_collection[user_id]['pdfs'])} PDFs added so far.)\n"
            "Send more files or use /done ✅ to merge them."
        )
    except Exception as e:
        await message.reply_text(f"❌ Failed to upload the PDF: {e}")

@Client.on_message(filters.photo & filters.private)
async def handle_image(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_collection:
        await message.reply_text(
            "⏳ Please start the merging process first by using /merge 🔄."
        )
        return

    try:
        temp_file = await message.download()  
        user_file_collection[user_id]["images"].append(temp_file)

        await message.reply_text(
            f"➕ Image added! 🖼️ ({len(user_file_collection[user_id]['images'])} images added so far.)\n"
            "Send more files or use /done ✅ to merge them."
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
            "⚠️ Please send at least one PDF 📑 or image 🖼️ before using /done ✅. Start fresh with /merge 🔄."
        )
        return

    await message.reply_text(
        "✍️ Type a name for your merged PDF 📄 (without extension)."
    )
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

    custom_filename = os.path.splitext(custom_filename)[0]
    custom_filename = custom_filename.replace("/", "_").replace("\\", "_").strip()

    if not custom_filename:  
        await message.reply_text("❌ Invalid filename. Please try again.")
        return

    # Send progress message after the filename is received
    progress_message = await message.reply_text(
        "🛠️ Merging your files... Please wait... 🔄"
    )
    
    try:
        # Use a NamedTemporaryFile for the output PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            output_file = temp_file.name

        # Merge PDFs and images asynchronously
        merger = PdfMerger()

        # Merge PDF files
        for pdf_index, pdf in enumerate(user_file_collection[user_id]["pdfs"], start=1):
            merger.append(pdf)
            await progress_message.edit_text(f"📝 Merging PDF {pdf_index} of {len(user_file_collection[user_id]['pdfs'])}...")

        # Convert images to PDFs and add them
        tasks = []
        for img_index, img_path in enumerate(user_file_collection[user_id]["images"], start=1):
            tasks.append(convert_image_to_pdf(img_path, merger, img_index, len(user_file_collection[user_id]["images"]), progress_message))

        # Wait for all image-to-PDF conversions
        await asyncio.gather(*tasks)

        # Write the merged output PDF
        merger.write(output_file)
        merger.close()

        # Send the merged PDF to the user
        await client.send_document(
            chat_id=message.chat.id,
            document=output_file,
            caption=f"🎉 Here is your merged PDF 📄.",
            file_name=f"{custom_filename}.pdf",
        )

        # After sending the merged file, delete the progress message
        await progress_message.delete()
        await message.reply_text("✅ Your files have been successfully merged! 🎊")

    except Exception as e:
        await progress_message.edit_text(f"❌ Failed to merge files: {e}")

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
async def convert_image_to_pdf(img_path, merger, img_index, total_images, progress_message):
    try:
        image = Image.open(img_path)
        image = image.convert("RGB")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as img_pdf:
            image.save(img_pdf.name, "PDF")
            merger.append(img_pdf.name)
        await progress_message.edit_text(f"📸 Converting image {img_index} of {total_images} to PDF... 🔄")
    except Exception as e:
        logger.error(f"Error converting image {img_path} to PDF: {e}")

