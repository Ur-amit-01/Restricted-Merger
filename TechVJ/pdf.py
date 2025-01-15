import os
import logging
import tempfile
from PIL import Image
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
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
        "🔄 Ready to start! Send your PDFs 📑 and images 🖼️ one by one. When you're ready, type /done ✅ to merge them into one PDF. 🌟"
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

    progress_message = await message.reply_text("🛠️ Downloading and merging your files... Please wait... 🔄")

    try:
        # Temporary directory for downloading files
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, f"{custom_filename}.pdf")
            merger = PdfMerger()

            for index, file_data in enumerate(user_file_metadata[user_id], start=1):
                if file_data["type"] == "pdf":
                    file_path = await client.download_media(file_data["file_id"], file_name=os.path.join(temp_dir, file_data["file_name"]))
                    merger.append(file_path)
                    await progress_message.edit_text(f"📑 Merging PDF {index} of {len(user_file_metadata[user_id])}...")
                elif file_data["type"] == "image":
                    img_path = await client.download_media(file_data["file_id"], file_name=os.path.join(temp_dir, file_data["file_name"]))
                    image = Image.open(img_path).convert("RGB")
                    img_pdf_path = os.path.join(temp_dir, f"{os.path.splitext(file_data['file_name'])[0]}.pdf")
                    image.save(img_pdf_path, "PDF")
                    merger.append(img_pdf_path)
                    await progress_message.edit_text(f"📸 Converting and merging image {index} of {len(user_file_metadata[user_id])}...")

            merger.write(output_file)
            merger.close()

            await client.send_document(
                chat_id=message.chat.id,
                document=output_file,
                caption="🎉 Here is your merged PDF 📄.",
            )
            await progress_message.delete()
            await message.reply_text("✅ Your files have been successfully merged! 🎊")

    except Exception as e:
        await progress_message.edit_text(f"❌ Failed to merge files: {e}")

    finally:
        user_file_metadata.pop(user_id, None)
        pending_filename_requests.pop(user_id, None)
