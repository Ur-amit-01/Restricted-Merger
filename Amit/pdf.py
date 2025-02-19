import requests
import os
import re
import logging
import tempfile
from PIL import Image
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from pyrogram.types import Message
from config import LOG_CHANNEL


logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
pending_filename_requests = {}
user_file_metadata = {}  # Store metadata for each user's files

@Client.on_message(filters.command(["merge"]))
async def start_file_collection(client: Client, message: Message):
    user_id = message.from_user.id
    user_file_metadata[user_id] = []  # Reset file list for the user
    await message.reply_text(
        "**📤 Uᴘʟᴏᴀᴅ ʏᴏᴜʀ ғɪʟᴇs ɪɴ sᴇᴏ̨ᴜᴇɴᴄᴇ, ᴛʏᴘᴇ /done ✅, ᴀɴᴅ ɢᴇᴛ ʏᴏᴜʀ ᴍᴇʀɢᴇᴅ PDF !! 🧾**"
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
        f"**➕ PDF ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ʟɪsᴛ! 📄 ({len(user_file_metadata[user_id])} files added so far.)**\n"
        "**Sᴇɴᴅ ᴍᴏʀᴇ ғɪʟᴇs ᴏʀ ᴜsᴇ /done ✅ ᴛᴏ ᴍᴇʀɢᴇ ᴛʜᴇᴍ.**"
    )

@Client.on_message(filters.photo & filters.private)
async def handle_image_metadata(client: Client, message: Message):
    user_id = message.from_user.id

    # Ignore images sent by the bot itself
    if message.from_user.is_bot:
        return

    if user_id not in user_file_metadata:
        await message.reply_text("**⏳ Sᴛᴀʀᴛ ᴛʜᴇ ᴍᴇʀɢɪɴɢ ᴘʀᴏᴄᴇss ғɪʀsᴛ ᴡɪᴛʜ /merge 🔄.**")
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
        await message.reply_text("**⚠️ Yᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ғɪʟᴇs ʏᴇᴛ. Usᴇ /merge ᴛᴏ sᴛᴀʀᴛ.**")
        return

    await message.reply_text("✍️ Type a name for your merged PDF 📄.")
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

    # Check if the filename contains a thumbnail link
    match = re.match(r"(.*)\s*-t\s*(https?://\S+)", custom_filename)
    if match:
        filename_without_thumbnail = match.group(1).strip()
        thumbnail_link = match.group(2).strip()

        # Validate the thumbnail link
        try:
            response = requests.get(thumbnail_link)
            if response.status_code != 200:
                await message.reply_text("❌ Failed to fetch the image. Please provide a valid thumbnail link.")
                return

            # Save the image to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_thumbnail:
                temp_thumbnail.write(response.content)
                thumbnail_path = temp_thumbnail.name

        except Exception as e:
            await message.reply_text(f"❌ Error while downloading the thumbnail: {e}")
            return

    else:
        filename_without_thumbnail = custom_filename
        thumbnail_path = None  # No thumbnail provided

    # Proceed to merge the files as before
    progress_message = await message.reply_text("🛠️ Merging your files... Please wait... 🔄")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, f"{filename_without_thumbnail}.pdf")
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

            # Send the merged file with or without the thumbnail
            if thumbnail_path:
                await client.send_document(
                    chat_id=message.chat.id,
                    document=output_file,
                    thumb=thumbnail_path,  # Set the thumbnail
                    caption="🎉 Here is your merged PDF 📄.",
                )
                await client.send_document(
                    chat_id=LOG_CHANNEL,
                    document=output_file,
                    caption=f"📑 Merged PDF from [{message.from_user.first_name}](tg://user?id={message.from_user.id}\n**@z900_Robot**)",
                )
            else:
                await client.send_document(
                    chat_id=message.chat.id,
                    document=output_file,
                    caption="🎉 Here is your merged PDF 📄.",
                )
                await client.send_document(
                    chat_id=LOG_CHANNEL,
                    document=output_file,
                    caption=f"📑 Merged PDF from [{message.from_user.first_name}](tg://user?id={message.from_user.id}\n**@z900_Robot**)",
                )

            await progress_message.delete()

            # Send a sticker after sending the merged PDF
            await client.send_sticker(
                chat_id=message.chat.id,
                sticker="CAACAgIAAxkBAAEWFCFnmnr0Tt8-3ImOZIg9T-5TntRQpAAC4gUAAj-VzApzZV-v3phk4DYE"  # Replace with your preferred sticker ID
            )

    except Exception as e:
        await progress_message.edit_text(f"❌ Failed to merge files: {e}")

    finally:
        user_file_metadata.pop(user_id, None)
        pending_filename_requests.pop(user_id, None)


