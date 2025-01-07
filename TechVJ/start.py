import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, BOT_TOKEN, ERROR_MESSAGE
from TechVJ.strings import HELP_TXT
import subprocess
import glob
import logging
import re
from collections import Counter
from os.path import basename
from telegram import Update
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from PyPDF2 import PdfMerger, PdfReader

# Directory to store uploaded files
UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Resolve file name conflicts
def resolve_file_name_conflict(output_path):
    base, ext = os.path.splitext(output_path)
    counter = 1
    while os.path.exists(output_path):
        output_path = f"{base} ({counter}){ext}"
        counter += 1
    return output_path

# Analyze filenames to generate a merged filename
def analyze_and_generate_filename(file_paths, upload_dir):
    if not file_paths:
        return os.path.join(upload_dir, "merged.pdf")

    words_list = []
    for file_path in file_paths:
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        words = re.findall(r'\b\w+\b', file_name.lower())
        words_list.extend(words)

    word_counts = Counter(words_list)

    common_words = [word for word, count in word_counts.items() if count == len(file_paths)]

    if common_words:
        common_part = "_".join(common_words[:3])
        merged_filename = f"{common_part}_merged.pdf"
    else:
        merged_filename = "merged.pdf"

    merged_file_path = os.path.join(upload_dir, merged_filename)
    return resolve_file_name_conflict(merged_file_path)

# Handle file uploads
async def handle_file(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    file_name = document.file_name
    file_type = document.mime_type
    file_path = os.path.join(UPLOAD_DIR, basename(file_name))

    file_path = resolve_file_name_conflict(file_path)

    if "status_message" not in context.user_data:
        context.user_data["status_message"] = await update.message.reply_text(
            "Processing your file..."
        )
    else:
        pass

    file = await document.get_file()
    await file.download_to_drive(file_path)

    if file_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        await context.user_data["status_message"].edit_text(f"File {file_name} not supported. Only PDF and Word are accepted.")
        os.remove(file_path)
        return

    if file_type != "application/pdf":
        try:
            pdf_path = convert_to_pdf(file_path)
            await context.user_data["status_message"].edit_text(f"File {file_name} successfully converted to PDF!")
            file_path = pdf_path
        except Exception as e:
            await context.user_data["status_message"].edit_text(f"Failed to convert {file_name}. Error: {e}")
            os.remove(file_path)
            return

    context.user_data.setdefault("files", []).append(file_path)

    if len(context.user_data["files"]) == 1:
        await context.user_data["status_message"].reply_text(
            "Do you want to merge all files into one PDF or leave them as they are?",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Merge", callback_data="merge"), InlineKeyboardButton("Leave", callback_data="leave")]])
        )
    else:
        await context.user_data["status_message"].edit_text(f"File {file_name} processed.")

# Convert Word to PDF
def convert_to_pdf(input_path: str) -> str:
    output_path = input_path.rsplit(".", 1)[0] + ".pdf"
    output_path = resolve_file_name_conflict(output_path)
    command = ["soffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", UPLOAD_DIR]
    subprocess.run(command, check=True)
    return output_path

# Merge PDFs
async def merge_pdfs(update: Update, context: CallbackContext) -> None:
    files = context.user_data.get("files", [])
    if not files:
        await update.message.reply_text("No files to merge.")
        return

    output_path = analyze_and_generate_filename(files, UPLOAD_DIR)
    merger = PdfMerger()

    try:
        for file_path in files:
            with open(file_path, 'rb') as pdf:
                merger.append(PdfReader(pdf))
        merger.write(output_path)
        merger.close()

        await update.message.reply_text("Files successfully merged! Sending...")
        await update.message.reply_document(document=open(output_path, "rb"))

    except Exception as e:
        await update.message.reply_text(f"Error merging files: {e}")

    finally:
        for file_path in files:
            try:
                os.remove(file_path)
            except FileNotFoundError:
                logger.error(f"Error removing file {file_path}")
        context.user_data.clear()

# Cancel the operation
async def cancel(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Operation cancelled. All uploaded files removed.")
    for file_path in context.user_data.get("files", []):
        os.remove(file_path)
    context.user_data["files"] = []

# Handle callback queries (e.g., merge or leave options)
async def callback_query_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "merge":
        await merge_pdfs(update, context)
    elif query.data == "leave":
        await query.edit_message_text("Files are kept as they are.")
        await send_files(update, context)

# Send files to user
async def send_files(update: Update, context: CallbackContext) -> None:
    files = context.user_data.get("files", [])
    for file_path in files:
        await update.message.reply_document(document=open(file_path, "rb"))

    for file in files:
        os.remove(file)
    context.user_data.clear()

# Main function
def main() -> None:
    token = "BOT_TOKEN"
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(CallbackQueryHandler(callback_query_handler))

    logger.info("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
    
# Provide your session string here
SESSION_STRING = os.environ.get("SESSION_STRING", "")

class batch_temp(object):
    IS_BATCH = {}

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot. I can send you restricted content by its post link.\n\nKnow how to use bot by - /help</b>\n\n> **👨‍💻 Dᴇᴠᴇʟᴏᴘᴇʀ : [ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝](https://t.me/Ur_Amit_01)**",
        reply_to_message_id=message.id,
        disable_web_page_preview=True
    )

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"{HELP_TXT}",
        disable_web_page_preview=True
    )

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id,
        text="**Batch Successfully Cancelled.**"
    )


@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For It To Complete. If You Want To Cancel This Task Then Use - /cancel**")

        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        batch_temp.IS_BATCH[message.from_user.id] = False

        # Connect using the session string
        acc = Client("manual_session", session_string=SESSION_STRING, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()

        for msgid in range(fromID, toID + 1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break

            # Handle private chats
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # Handle public chats
            else:
                username = datas[3]
                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied:
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return

                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            await asyncio.sleep(1)
        batch_temp.IS_BATCH[message.from_user.id] = True
        await acc.disconnect()

# Reuse the handle_private and get_message_type functions from the original code without modification

# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
            
    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass
        
