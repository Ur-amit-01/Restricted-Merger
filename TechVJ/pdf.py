import os
import logging   
import asyncio
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from pyrogram.types import Message
import tempfile

user_pdf_collection = {}
pending_filename = {}

logger = logging.getLogger(__name__)

@Client.on_message(filters.command(["merge"]))
async def start_pdf_collection(client: Client, message: Message):
    logger.info(f"/merge command triggered by user {message.from_user.id}")
    user_id = message.from_user.id
    user_pdf_collection[user_id] = []  # Initialize an empty list for storing PDF files
    await message.reply_text(
        "Send me the PDFs you want to merge, one by one. When you're done, send /done."
    )

@Client.on_message(filters.command(["done"]))
async def ask_for_filename(client: Client, message: Message):
    logger.info(f"/done command triggered by user {message.from_user.id}")
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

@Client.on_message(filters.text & filters.private)
async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id

    # Check if the bot is waiting for a filename
    if user_id not in pending_filename:
        return

    filename = message.text.strip()
    if not filename:
        await message.reply_text("Invalid filename. Please try again.")
        return

    pending_filename.pop(user_id, None)  # Remove pending state

    # Create a temporary file with the given filename
    output_file = f"{filename}.pdf"

    # Merge the PDFs
    try:
        merger = PdfMerger()
        for pdf in user_pdf_collection[user_id]:
            merger.append(pdf)
        merger.write(output_file)
        merger.close()
        
        # Send the merged PDF
        await client.send_document(
            chat_id=message.chat.id,
            document=output_file,
            caption="Here is your merged PDF. ✅",
            reply_to_message_id=message.id
        )
        
        # Send a confirmation message
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

@Client.on_message(filters.document & filters.private)
async def handle_pdf(client, message):
    user_id = message.from_user.id  # Get the user's ID
    
    # Check if the document is a PDF
    if message.document.mime_type != "application/pdf":
        await message.reply_text("This is not a valid PDF file.")
        return

    # Ensure the user has initiated the merging process
    if user_id not in user_pdf_collection:
        await message.reply_text(
            "You need to start the merging process first. Use /merge to begin."
        )
        return

    # Limit to 20 PDFs per user
    if len(user_pdf_collection[user_id]) >= 20:
        await message.reply_text(
            "You can only upload up to 20 PDFs for merging. Send /done to merge the files."
        )
        return

    # Download the PDF file
    try:
        temp_file = await message.download()  # Download the file to a temporary location
        user_pdf_collection[user_id].append(temp_file)  # Add the file path to the user's list

        await message.reply_text(
            f"PDF {len(user_pdf_collection[user_id])} uploaded successfully. "
            "Send more PDFs or use /done to merge them."
        )
    except Exception as e:
        await message.reply_text(f"Failed to upload the PDF: {e}")
