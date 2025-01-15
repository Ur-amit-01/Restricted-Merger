import os
import logging
import tempfile
from PIL import Image
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types import Message

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
pending_filename_requests = {}
user_file_metadata = {}  # Store metadata for each user's files


@Client.on_message(filters.command(["merge"]))
async def start_file_collection(client: Client, message: Message):
    user_id = message.from_user.id
    user_file_metadata[user_id] = []  # Reset file list for the user
    await message.reply_text(
        "📤 Upload files in sequence, type /done ✅, and get your merged PDF !! 🚀"
    )


@Client.on_message(filters.document & filters.private)
async def handle_pdf_metadata(client: Client, message: Message):
    user_id = message.from_user.id

    if message.document.mime_type != "application/pdf":
        await message.reply_text("❌ This is not a valid PDF file. Please send a PDF 📑.")
        return

    if user_id not in user_file_metadata:
        await message.reply_text("⏳ Start the merging process first with /merge 🔄.")
        return

    if len(user_file_metadata[user_id]) >= 20:
        await message.reply_text(
            "⚠️ You can upload up to 20 files. Type /done ✅ to merge them."
        )
        return

    if message.document.file_size > MAX_FILE_SIZE:
        await message.reply_text("🚫 File size is too large! Please send a file under 20MB.")
        return

    user_file_metadata[user_id].append(
        {
            "type": "pdf",
            "file_id": message.document.file_id,
            "file_name": message.document.file_name,
        }
    )
    await message.reply_text(
        f"➕ PDF added to the list! 📄 ({len(user_file_metadata[user_id])} files added so far.)\n"
        "Send more files or use /done ✅ to merge them."
    )


@Client.on_message(filters.photo & filters.private)
async def handle_image_metadata(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_metadata:
        await message.reply_text("⏳ Start the merging process first with /merge 🔄.")
        return

    user_file_metadata[user_id].append(
        {
            "type": "image",
            "file_id": message.photo.file_id,
            "file_name": f"photo_{len(user_file_metadata[user_id]) + 1}.jpg",
        }
    )
    await message.reply_text(
        f"➕ Image added to the list! 🖼️ ({len(user_file_metadata[user_id])} files added so far.)\n"
        "Send more files or use /done ✅ to merge them."
    )


@Client.on_message(filters.command(["done"]))
async def merge_files(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in user_file_metadata or not user_file_metadata[user_id]:
        await message.reply_text("⚠️ You haven't added any files yet. Use /merge to start.")
        return

    await message.reply_text("✍️ Type a name for your merged PDF 📄.")
    pending_filename_requests[user_id] = {"filename_request": True}
    
    # Send message with options to add thumbnail or not
    keyboard = [
        [InlineKeyboardButton("Add Thumbnail", callback_data="add_thumbnail"),
         InlineKeyboardButton("No", callback_data="no_thumbnail")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        "Do you want to add a thumbnail to your merged PDF? 📷",
        reply_markup=reply_markup
    )

    # Save filename and move to the next step
    pending_filename_requests[user_id]["filename"] = custom_filename
    pending_filename_requests[user_id]["thumbnail_request"] = True


@Client.on_callback_query(filters.regex("add_thumbnail"))
async def ask_for_thumbnail(client: Client, callback_query):
    user_id = callback_query.from_user.id
    await callback_query.answer()

    # Ask for the thumbnail
    await client.send_message(user_id, "Please send the image you want to use as a thumbnail for the PDF 📸.")
    
    # Update status
    pending_filename_requests[user_id]["thumbnail_request"] = True


@Client.on_callback_query(filters.regex("no_thumbnail"))
async def skip_thumbnail(client: Client, callback_query):
    user_id = callback_query.from_user.id
    await callback_query.answer()

    # Proceed without thumbnail
    pending_filename_requests[user_id]["thumbnail_request"] = False
    await client.send_message(user_id, "No thumbnail will be added. Merging files now... 🔄")


@Client.on_message(filters.photo & filters.private)
async def handle_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in pending_filename_requests or not pending_filename_requests[user_id].get("thumbnail_request"):
        return

    # Save the thumbnail image
    thumbnail_path = os.path.join(tempfile.gettempdir(), f"{user_id}_thumbnail.jpg")
    await message.download(thumbnail_path)

    # Update pending requests with the thumbnail path
    pending_filename_requests[user_id]["thumbnail_path"] = thumbnail_path
    await message.reply_text("Thumbnail added successfully! 🎉 Now I will merge your PDF.")

    # Proceed to merging after the thumbnail is received
    await merge_pdfs_with_thumbnail(client, user_id)


async def merge_pdfs_with_thumbnail(client: Client, user_id: int):
    custom_filename = pending_filename_requests[user_id]["filename"]
    thumbnail_path = pending_filename_requests[user_id].get("thumbnail_path")

    progress_message = await client.send_message(user_id, "🛠️ Merging your files... Please wait... 🔄")

    try:
        # Temporary directory for downloading files
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, f"{custom_filename}.pdf")
            merger = PdfMerger()

            for index, file_data in enumerate(user_file_metadata[user_id], start=1):
                if file_data["type"] == "pdf":
                    file_path = await client.download_media(file_data["file_id"], file_name=os.path.join(temp_dir, file_data["file_name"]))
                    merger.append(file_path)
                    await progress_message.edit_text(f"📑 Merging PDFs {index} of {len(user_file_metadata[user_id])}...")
                elif file_data["type"] == "image":
                    img_path = await client.download_media(file_data["file_id"], file_name=os.path.join(temp_dir, file_data["file_name"]))
                    image = Image.open(img_path).convert("RGB")
                    img_pdf_path = os.path.join(temp_dir, f"{os.path.splitext(file_data['file_name'])[0]}.pdf")
                    image.save(img_pdf_path, "PDF")
                    merger.append(img_pdf_path)
                    await progress_message.edit_text(f"📸 Merging image {index} of {len(user_file_metadata[user_id])}...")

            merger.write(output_file)
            merger.close()

            # Send the merged PDF with a thumbnail if provided
            if thumbnail_path:
                await client.send_document(
                    chat_id=user_id,
                    document=output_file,
                    caption="🎉 Here is your merged PDF with thumbnail 📄.",
                    thumb=thumbnail_path  # Use the thumbnail as a preview for the document
                )
            else:
                await client.send_document(
                    chat_id=user_id,
                    document=output_file,
                    caption="🎉 Here is your merged PDF 📄."
                )
            
            await progress_message.delete()
            await client.send_message(user_id, "🔥 Your PDF is ready! Enjoy! 🎉")

    except Exception as e:
        await progress_message.edit_text(f"❌ Failed to merge files: {e}")

    finally:
        user_file_metadata.pop(user_id, None)
        pending_filename_requests.pop(user_id, None)

