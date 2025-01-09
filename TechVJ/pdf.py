import os
import logging   
import asyncio
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from pyrogram.types import Message
import tempfile

logger = logging.getLogger(__name__)

user_pdf_collection = {}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
pending_filename_requests = {}

@Client.on_message(filters.command(["merge"]))
async def start_pdf_collection(client: Client, message: Message):
    logger.info(f"/merge command triggered by user {message.from_user.id}")
    user_id = message.from_user.id
    user_pdf_collection[user_id] = []  # Initialize an empty list for storing PDF files
    await message.reply_text(
        "Now, Send your PDFs 📑 one by one. Use /done ✅ to merge."
    )

@Client.on_message(filters.command(["done"]))
async def request_filename(client: Client, message: Message):
    logger.info(f"/done command triggered by user {message.from_user.id}")
    user_id = message.from_user.id

    # Check if the user has uploaded at least 2 PDFs
    if user_id not in user_pdf_collection or len(user_pdf_collection[user_id]) < 2:
        await message.reply_text(
            "Send at least 2 PDFs 📑 before using /done. Start fresh with /merge 🔄."
        )
        return

    # Ask the user for a filename
    pending_filename_requests[user_id] = True
    await message.reply_text(
        "Send the name for your merged PDF 📄 (no extension) ✍️."
    )

@Client.on_message(filters.text & filters.private & ~filters.regex("https://t.me/"))
async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id

    # Check if the user is in the pending filename list
    if user_id not in pending_filename_requests:
        return  # Ignore if no filename was requested

    # Get the custom filename and sanitize it
    custom_filename = message.text.strip()
    if not custom_filename:  # Validate filename
        await message.reply_text("Filename cannot be empty. Please try again.")
        return

    # Remove any file extensions (e.g., '.pdf') provided by the user
    custom_filename = os.path.splitext(custom_filename)[0]

    # Ensure filename is safe
    custom_filename = custom_filename.replace("/", "_").replace("\\", "_").strip()

    if not custom_filename:  # Check again after sanitization
        await message.reply_text("Invalid filename. Please try again.")
        return

    # Create the output file path with sanitized filename
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        output_file = temp_file.name

    # Merge PDFs
    try:
        merger = PdfMerger()
        for pdf in user_pdf_collection[user_id]:
            merger.append(pdf)
        merger.write(output_file)
        merger.close()

        # Send the merged PDF with the sanitized filename
        await client.send_document(
            chat_id=message.chat.id,
            document=output_file,
            caption=f"Here is your merged PDF. ✅",
            file_name=f"{custom_filename}.pdf",
        )

        # Confirmation message
        await message.reply_text("Your PDFs have been successfully merged!")
    
    except Exception as e:
        await message.reply_text(f"Failed to merge PDFs: {e}")
    
    finally:
        # Clean up temporary files
        for pdf in user_pdf_collection[user_id]:
            if os.path.exists(pdf):
                os.remove(pdf)
        user_pdf_collection.pop(user_id, None)
        if os.path.exists(output_file):
            os.remove(output_file)

        # Remove the user from pending filename requests
        pending_filename_requests.pop(user_id, None)

@Client.on_message(filters.document & filters.private)
async def handle_pdf(client: Client, message: Message):
    user_id = message.from_user.id  # Get the user's ID
    
    # Check if the document is a PDF
    if message.document.mime_type != "application/pdf":
        await message.reply_text("This is not a valid PDF file.")
        return

    # Ensure the user has initiated the merging process
    if user_id not in user_pdf_collection:
        await message.reply_text(
            "To begin merging your PDFs, please start the process by /merge. 🔄"
        )
        return

    # Limit to 20 PDFs per user
    if len(user_pdf_collection[user_id]) >= 20:
        await message.reply_text(
            "You can only upload up to 20 PDFs for merging. Send /done to merge the files."
        )
        return
        
    # Check if the file size exceeds the limit
    if message.document.file_size > MAX_FILE_SIZE:
        await message.reply_text(
            "The file is too large. Please send a PDF smaller than 20MB."
        )
        return
        
    # Download the PDF file
    try:
        temp_file = await message.download()  
        
        file_name = os.path.basename(temp_file)

        user_pdf_collection[user_id].append(temp_file)

        await message.reply_text(
            f"➥ {len(user_pdf_collection[user_id])}. {file_name} ✅ "
            "Send more PDFs or use /done to merge them."
        )
    except Exception as e:
        await message.reply_text(f"❌ Failed to upload the PDF : {e}")
