import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import time
import os
import threading
from os import environ

bot_token = environ.get("TOKEN", "") 
api_hash = environ.get("HASH", "") 
api_id = int(environ.get("ID", ""))
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# download status
def downstatus(statusfile, message):
    while not os.path.exists(statusfile):
        time.sleep(3)
    
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)


# upload status
def upstatus(statusfile, message):
    while not os.path.exists(statusfile):
        time.sleep(3)
    
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            bot.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
            time.sleep(10)
        except:
            time.sleep(5)


# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


# start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bot.send_message(
        message.chat.id,
        f"👋 Hii {message.from_user.mention}, **I am Save Restricted Bot, I can send you restricted content by its post link**\n\n{USAGE}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Updates Channel", url="https://t.me/Amit_0_1")]]),
        reply_to_message_id=message.id
    )


@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    print(message.text)

    # Public chat handling
    if "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        for msgid in range(fromID, toID + 1):
            username = datas[3]

            try:
                msg = bot.get_messages(username, msgid)
            except UsernameNotOccupied:
                bot.send_message(message.chat.id, f"**The username is not occupied by anyone**", reply_to_message_id=message.id)
                return

            try:
                bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
            except Exception as e:
                bot.send_message(message.chat.id, f"**Error** : __{e}__", reply_to_message_id=message.id)

            time.sleep(3)


# Get the type of message
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


USAGE = """**➥ ONLY FOR PUBLIC CHATS 👇**
• Post the link to see the bot in action 😎😁

**➥ MULTI POSTS** (To download multiple posts at once)
Send link in this format (From-to) 👇
https://t.me/xxxx/1001-1010

**➥ Developed by - @Ur_Amit_01 🧸✨**
"""

# Start polling
bot.run()
