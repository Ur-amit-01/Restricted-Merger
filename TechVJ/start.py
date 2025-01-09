from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import time

# Start command handler
@client.on_message(filters.command("start"))
async def send_welcome(client, message):
    # Send a sticker first
    sticker_id = 'CAACAgUAAxkBAAECEpdnLcqQbmvQfCMf5E3rBK2dkgzqiAACJBMAAts8yFf1hVr67KQJnh4E'
    sent_sticker = await client.send_sticker(message.chat.id, sticker_id)
    sticker_message_id = sent_sticker.message_id
    time.sleep(2)
    await client.delete_messages(message.chat.id, sticker_message_id)
    
    # Define the inline keyboard with buttons
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("«ʜᴇʟᴘ» 🕵️", callback_data="help"),
         InlineKeyboardButton("«ᴀʙᴏᴜᴛ» 📄", callback_data="about")],
        [InlineKeyboardButton("•Dᴇᴠᴇʟᴏᴘᴇʀ• ☘", url="https://t.me/Ur_amit_01")]
    ])
    
    # Send the photo with the caption and inline keyboard
    image_url = 'https://graph.org/file/0f1d046b4b3899e1812bf-0e63e80abb1bef1a8b.jpg'
    await client.send_photo(
        message.chat.id, 
        image_url, 
        caption="Aʜ, ᴀ ɴᴇᴡ ᴛʀᴀᴠᴇʟᴇʀ ʜᴀs ᴀʀʀɪᴠᴇᴅ... Wᴇʟᴄᴏᴍᴇ ᴛᴏ ᴍʏ ᴍᴀɢɪᴄᴀʟ ʀᴇᴀʟᴍ !🧞‍♂️✨\n\n• I ᴀᴍ PDF ɢᴇɴɪᴇ, ɪ ᴡɪʟʟ ɢʀᴀɴᴛ ʏᴏᴜʀ ᴘᴅғ ᴡɪsʜᴇs! 📑🪄",
        reply_markup=markup
    )

# Callback query handler
@client.on_callback_query(filters.regex("^(help|about|back)$"))
async def callback_handler(client, callback_query):
    # Define media and caption based on the button clicked
    if callback_query.data == "help":
        new_image_url = 'https://graph.org/file/0f1d046b4b3899e1812bf-0e63e80abb1bef1a8b.jpg'
        new_caption = "Hᴇʀᴇ Is Tʜᴇ Hᴇʟᴘ Fᴏʀ Mʏ Cᴏᴍᴍᴀɴᴅs.:\n1. Send PDF files.\n2. Use /merge when you're ready to combine them.\n3. Max size = 20MB per file.\n\n• Note: My developer is constantly adding new features in my program , if you found any bug or error please report at @Ur_Amit_01"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])
    elif callback_query.data == "about":
        new_image_url = 'https://graph.org/file/0f1d046b4b3899e1812bf-0e63e80abb1bef1a8b.jpg'
        new_caption = ABOUT_TXT
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])
    elif callback_query.data == "back":
        new_image_url = 'https://graph.org/file/0f1d046b4b3899e1812bf-0e63e80abb1bef1a8b.jpg'
        new_caption = "Aʜ, ᴀ ɴᴇᴡ ᴛʀᴀᴠᴇʟᴇʀ ʜᴀs ᴀʀʀɪᴠᴇᴅ... Wᴇʟᴄᴏᴍᴇ ᴛᴏ ᴍʏ ᴍᴀɢɪᴄᴀʟ ʀᴇᴀʟᴍ !🧞‍♂️✨\n\n• I ᴀᴍ PDF ɢᴇɴɪᴇ, ɪ ᴡɪʟʟ ɢʀᴀɴᴛ ʏᴏᴜʀ ᴘᴅғ ᴡɪsʜᴇs! 📑🪄"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Help 🕵️", callback_data="help"),
             InlineKeyboardButton("About 📄", callback_data="about")],
            [InlineKeyboardButton("Developer ☘", url="https://t.me/Ur_amit_01")]
        ])
    
    # Create media object with the new image and caption
    media = InputMediaPhoto(media=new_image_url, caption=new_caption, parse_mode="HTML")
    
    # Edit the original message with the new image and caption
    await client.edit_message_media(
        media=media,
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=markup  # Updated inline keyboard
    )

ABOUT_TXT = """<b><blockquote>⍟───[ MY ᴅᴇᴛᴀɪʟꜱ ]───⍟</blockquote>
    
‣ ᴍʏ ɴᴀᴍᴇ : <a href='https://t.me/PDF_Genie_Robot'>PDF Genie</a>
‣ ᴍʏ ʙᴇsᴛ ғʀɪɴᴇɴᴅ : <a href='tg://settings'>ᴛʜɪs ᴘᴇʀsᴏɴ</a> 
‣ ᴅᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://t.me/Ur_amit_01'>ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝</a> 
‣ ʟɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>ᴘʏʀᴏɢʀᴀᴍ</a> 
‣ ʟᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/download/releases/3.0/'>ᴘʏᴛʜᴏɴ 3</a> 
‣ ᴅᴀᴛᴀ ʙᴀsᴇ : <a href='https://www.mongodb.com/'>ᴍᴏɴɢᴏ ᴅʙ</a> 
‣ ʙᴜɪʟᴅ sᴛᴀᴛᴜs : ᴠ2.7.1 [sᴛᴀʙʟᴇ]</b>"""

# Help command handler
@client.on_message(filters.command("help"))
async def send_help(client, message):
    help_text = "1. Send me PDF files you want to merge.\n"
    help_text += "2. Use /merge to combine the files into one PDF.\n"
    help_text += "3. Use /clear to reset the list of files."
    await client.reply(message.chat.id, help_text)
