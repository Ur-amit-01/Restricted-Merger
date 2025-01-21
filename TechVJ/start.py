import os
import logging
import time
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, BOT_TOKEN, ERROR_MESSAGE

start_time = time.time()
logger = logging.getLogger(__name__)
    
SESSION_STRING = os.environ.get("SESSION_STRING", "")

class batch_temp(object):
    IS_BATCH = {}

def get_uptime():
    uptime_seconds = time.time() - start_time
    days = int(uptime_seconds // (24 * 3600))
    hours = int((uptime_seconds % (24 * 3600)) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"


async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(1)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"> **Downloading 📥** \n\n**{txt}**")
            await asyncio.sleep(2)
        except:
            await asyncio.sleep(2)

async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(1)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"> **Uploading 📤** \n\n**{txt}**")
            await asyncio.sleep(2)
        except:
            await asyncio.sleep(2)

async def progress(current, total, message, type):
    try:
        # Initialize or reset the start time for each task
        if not hasattr(progress, "start_time") or progress.task_type != type:
            progress.start_time = time.time()
            progress.task_type = type  # Keep track of the current task type

        # Calculate elapsed time
        elapsed_time = time.time() - progress.start_time  # Elapsed time in seconds

        # Calculate percentage progress
        percent = current * 100 / total
        processed = current / (1024 * 1024)  # Processed in MB
        total_size = total / (1024 * 1024)  # Total size in MB
        
        # Calculate the download/upload speed in MB/s
        speed = current / elapsed_time / (1024 * 1024) if elapsed_time > 0 else 0

        # Format the elapsed time in a readable format (hours, minutes, seconds)
        hours, remainder = divmod(int(elapsed_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_time = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"
        
        # Update progress message in file
        with open(f'{message.id}{type}status.txt', "w") as fileup:
            fileup.write(f"**📊 Progress**: {percent:.1f}%\n"
                         f"**📦 Processed**: {processed:.2f}MB/{total_size:.2f}MB\n"
                         f"**⚡ Speed**: {speed:.2f} MB/s\n"
                         f"**⏱️ Time Elapsed**: {formatted_time}\n")
        
        # Update the message with the progress
        if percent % 5 == 0:  # Update every 5% for smoother experience
            try:
                await message.edit_text(
                    f"**🚀 Task Progress:**\n"
                    f"📊 Progress: {percent:.1f}%\n"
                    f"📦 Processed: {processed:.2f}MB of {total_size:.2f}MB\n"
                    f"⚡ Speed: {speed:.2f} MB/s\n"
                    f"⏱️ Time Elapsed: {formatted_time}"
                )
            except Exception as e:
                # In case of any errors, log them
                logger.error(f"Error updating message: {e}")
        
    except Exception as e:
        logger.error(f"Error in progress function: {e}")

#————————————————————————————————————————————————————————————————————————————————————————————import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    logger.info(f"/start command triggered by {message.from_user.id}")  # Log the start command
    start_text = (
        f"> **✨👋🏻 Hey {message.from_user.mention} !!**\n\n"
        "**🔋 ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀꜰᴜʟ ʙᴏᴛ ᴅᴇꜱɪɢɴᴇᴅ ᴛᴏ ᴀꜱꜱɪꜱᴛ ʏᴏᴜ ᴇꜰꜰᴏʀᴛʟᴇꜱꜱʟʏ.**\n\n"
        "**🔘 Usᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍʏ ғᴜɴᴄᴛɪᴏɴs!**"
    )
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("💡 About", callback_data="about"), InlineKeyboardButton("📖 Help", callback_data="help")]
    ])
    await message.reply_text(start_text, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("about"))
async def about_callback(client: Client, callback_query):
    try:
        uptime = get_uptime()
        ABOUT_TXT_MSG = ABOUT_TXT.format(uptime=uptime)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ])

        await callback_query.message.edit_text(
            ABOUT_TXT_MSG,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in 'about_callback': {e}")
        await callback_query.answer("An error occurred. Please try again later.", show_alert=True)


ABOUT_TXT = """**⍟───[ MY ᴅᴇᴛᴀɪʟꜱ ]───⍟

• ᴍʏ ɴᴀᴍᴇ : [z900 ⚝](https://t.me/Z900_robot)
• ᴍʏ ʙᴇsᴛ ғʀɪᴇɴᴅ : [ᴛʜɪs ᴘᴇʀsᴏɴ](tg://settings)
• ᴅᴇᴠᴇʟᴏᴘᴇʀ : [ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝](https://t.me/Ur_Amit_01)
⏳ ᴜᴘᴛɪᴍᴇ : {uptime}**"""

#🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺🌺#

@Client.on_callback_query(filters.regex("help"))
async def help_callback(client: Client, callback_query):
    logger.info(f"Help callback triggered by {callback_query.from_user.id}")  # Log the callback query
    help_text = (
        "**📖 Help Menu:**\n\n"
        "Here’s how you can use me:\n"
        "1. Send me a Telegram post link to download restricted content.\n"
        "2. Merge PDFs by sending me multiple PDF files.\n\n"
        "Need more assistance? Feel free to ask!"
    )
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])
    await callback_query.message.edit_text(help_text, reply_markup=reply_markup)


@Client.on_callback_query(filters.regex("back"))
async def back_callback(client: Client, callback_query):
    logger.info(f"Back callback triggered by {callback_query.from_user.id}")  # Log the callback query
    start_text = (
        f"> **✨👋🏻 Hey {callback_query.from_user.mention} !!**\n\n"
        "**🔋 ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀꜰᴜʟ ʙᴏᴛ ᴅᴇꜱɪɢɴᴇᴅ ᴛᴏ ᴀꜱꜱɪꜱᴛ ʏᴏᴜ ᴇꜰꜰᴏʀᴛʟᴇꜱꜱʟʏ.**\n\n"
        "**🔘 Usᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍʏ ғᴜɴᴄᴛɪᴏɴs!**"
    )
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("💡 About", callback_data="about"), InlineKeyboardButton("📖 Help", callback_data="help")]
    ])
    await callback_query.message.edit_text(start_text, reply_markup=reply_markup)


#————————————————————————————————————————————————————————————————————————————————————————————


@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    logger.info(f"/cancel command triggered by user {message.from_user.id}")
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id,
        text="**Batch Successfully Cancelled.**"
    )


@Client.on_message(filters.text & filters.private & filters.regex("https://t.me/"))
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


