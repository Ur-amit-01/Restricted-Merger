from pyrogram import Client, filters

@Client.on_message(filters.command("stickerid") & filters.private)
async def stickerid(bot, message):
    # Check if the message is a reply to a sticker
    if message.reply_to_message and message.reply_to_message.sticker:
        s_msg = message.reply_to_message  # Get the sticker from the reply
        await message.reply_text(
            f"> **Sticker ID is** ✨ \n `{s_msg.sticker.file_id}` \n \n> **Unique ID is** 🔑 \n\n`{s_msg.sticker.file_unique_id}`"
        )
    else:
        # If it's not a reply to a sticker, ask the user to send a sticker
        s_msg = await bot.ask(chat_id=message.from_user.id, text="🌟 **Now Send Me Your Sticker 📲**")
        if s_msg.sticker:
            await s_msg.reply_text(
                f"> **Sticker ID is** ✨ \n `{s_msg.sticker.file_id}` \n \n> **Unique ID is** 🔑 \n\n`{s_msg.sticker.file_unique_id}`"
            )
        else:
            await s_msg.reply_text("Oops !! ❌ Not a sticker file 😕")
