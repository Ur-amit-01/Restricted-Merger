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
        return await message.reply("🚫 **This command works only in channels.**")
    
    # Proceed if the command is issued in a channel
    channel_id = message.chat.id
    show = await client.send_message(channel_id, "⏳ **Please Wait.....**")
    
    try:
        acc = Client("joinrequest", session_string=SESSION_STRING, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
    except:
        return await show.edit("❌ **Your Login Session Expired. Please update the session string and try again.**")
    
    try:
        # Check if the session account is an admin
        admins = await acc.get_chat_members(channel_id, filter="administrators")
        is_admin = any(admin.user.id == acc.me.id for admin in admins)
        
        if not is_admin:
            # Promote the session account as admin if it's not already
            await acc.promote_chat_member(
                channel_id,
                acc.me.id,
                can_manage_chat=True,
                can_manage_video_chats=True,
                can_post_messages=True,
                can_edit_messages=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_pin_messages=True
            )
            await show.edit("✅ **Session account promoted as admin. Starting to accept join requests.**")
    except Exception as e:
        await show.edit(f"⚠️ **Error: {str(e)}**")
        return
    
    # Directly accept join requests without needing a forwarded message
    msg = await show.edit("✅ **Accepting all join requests... Please wait until it's completed.**")
    
    try:
        while True:
            await acc.approve_all_chat_join_requests(channel_id)
            await asyncio.sleep(1)
            join_requests = [request async for request in acc.get_chat_join_requests(channel_id)]
            if not join_requests:
                break
        await msg.edit("🎉 **Successfully accepted all join requests.**")
    except Exception as e:
        await msg.edit(f"❌ **An error occurred:** {str(e)}")
    
    # After accepting all join requests, make the session account leave the channel
    try:
        await acc.leave_chat(channel_id)
        await msg.edit("👋 **Session account has left the channel.**")
    except Exception as e:
        print(f"⚠️ Error while making session account leave the channel: {e}")


@Client.on_chat_join_request(filters.group | filters.channel)
async def approve_new(client, m):
    if not NEW_REQ_MODE:
        return  # If NEW_REQ_MODE is False, the function exits without processing the join request.

    try:
        await client.approve_chat_join_request(m.chat.id, m.from_user.id)
        try:
            await client.send_message(
                m.from_user.id,
                f"👋 **Hello {m.from_user.mention}!\nWelcome to {m.chat.title}**\n\n__Powered by: @VJ_Botz__"
            )
        except:
            pass
    except Exception as e:
        print(f"⚠️ {str(e)}")
        pass

