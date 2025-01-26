import os
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, NEW_REQ_MODE

# Hardcoded session string, API ID, and API Hash
SESSION_STRING = os.environ.get("SESSION_STRING", "")


@Client.on_message(filters.command('accept'))
async def accept(client, message):
    # Check if the command is issued in a private chat (DM)
    if message.chat.type == enums.ChatType.PRIVATE:
        return await message.reply("**This command works only in channels.**")
    
    # Proceed if the command is issued in a channel
    channel_id = message.chat.id
    show = await client.send_message(channel_id, "**Please Wait.....**")
    
    try:
        acc = Client("joinrequest", session_string=SESSION_STRING, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except:
        return await show.edit("**Your Login Session Expired. Please update the session string and try again.**")
    
    # Directly accept join requests without needing forwarded message
    msg = await show.edit("**Accepting all join requests... Please wait until it's completed.**")
    
    try:
        while True:
            await acc.approve_all_chat_join_requests(channel_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(channel_id)]
            if not join_requests:
                break
        await msg.edit("**Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"**An error occurred:** {str(e)}")


@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if not NEW_REQ_MODE:
        return  # If NEW_REQ_MODE is False, the function exits without processing the join request.

    try:
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        try:
            await client.send_message(
                m.from_user.id,
                "**Hello {}!\nWelcome To {}\n\n__Powered By : @VJ_Botz __**".format(m.from_user.mention, m.chat.title)
            )
        except:
            pass
    except Exception as e:
        print(str(e))
        pass


