import time
import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, BotCommand
from config import BOT_TOKEN
import requests

# Define the bot's start time
START_TIME = time.time()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

random_images = [
    "https://envs.sh/Q_x.jpg",
    "https://envs.sh/Q_x.jpg"
]

# ------------------- Set Commands ------------------- #

OWNER_ID = 6803505727
@Client.on_message(filters.command("set"))
async def set(client, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply("You are not authorized to use this command.")
        return

    # Setting all the bot commands
    await client.set_bot_commands([
        BotCommand("start", "🚀 Start the bot and view the welcome message"),
        BotCommand("merge", "📎 Merge multiple PDFs or images into a single PDF"),
        BotCommand("done", "✅ Complete the merging process"),
        BotCommand("stickerid", "🆔 Get sticker ID (For Developers)"),
        BotCommand("telegraph", "🔗 Get a Telegraph link for media"),
        BotCommand("tts", "🗣️ Convert text to speech"),
        BotCommand("accept", "✔️ Accept all pending join requests in your channel"),
    ])
    
    await message.reply("✅ Commands configured successfully!")


# ------------------- Start ------------------- #

@Client.on_message(filters.command("start"))
@Client.on_callback_query(filters.regex("start"))
async def account_login(client: Client, m: Message):
    random_image = random.choice(random_images)

    caption = (
        f"> **✨👋🏻 Hey {m.from_user.mention} !!**\n\n"
        "**🔋 ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀꜰᴜʟ ʙᴏᴛ ᴅᴇꜱɪɢɴᴇᴅ ᴛᴏ ᴀꜱꜱɪꜱᴛ ʏᴏᴜ ᴇꜰꜰᴏʀᴛʟᴇꜱꜱʟʏ.**\n\n"
        "**🔘 Usᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍʏ ғᴜɴᴄᴛɪᴏɴs!**"
    )

    buttons = InlineKeyboardMarkup([ 
        [InlineKeyboardButton("🕵 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("📜 ᴀʙᴏᴜᴛ", callback_data="about")],
        [InlineKeyboardButton("❗❗ ᴅᴇᴠᴇʟᴏᴘᴇʀ ❗❗", url="https://t.me/Axa_bachha")]
    ])
    
    await client.send_photo(
        chat_id=m.chat.id,
        photo=random_image,
        caption=caption,
        reply_markup=buttons
    )

@Client.on_callback_query(filters.regex("uptime"))
async def uptime_callback(client: Client, query: CallbackQuery):
    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = time.strftime("%H hours %M minutes %S seconds", time.gmtime(uptime_seconds))
    
    await query.answer(f"🤖 Bot Uptime: {uptime_str}", show_alert=True)

#--------------------------------------------------------

RESTRICTED_TXT = """> **💡 Restricted content saver**

**1. 🔒 Private Chats**
➥ Send the invite link (if not already a member).  
➥ Send the post link to download content.

**2. 🌐 Public Chats**
➥ Simply share the post link.

**3. 📂 Batch Mode**
➥ Download multiple posts using this format:  
> https://t.me/xxxx/1001-1010"""

#------------------- MERGE -------------------#

MERGER_TXT = """> **⚙️ Hᴇʟᴘ Dᴇsᴄʀɪᴘᴛɪᴏɴ ⚙️**

📄 **/merge** - Start the merging process.  
⏳ **Upload your files (PDFs or Images) in sequence.**  
✅ **Type /done** to merge the uploaded files into a single PDF.

> 🌺 **Supported Files:**  
**• 📑 PDFs: Add up to 20 PDF files.**
**• 🖼️ Images: Convert images to PDF pages.**

> ⚠️ **Restrictions:**  
**• Max File Size: 20MB**
**• Max Files per Merge: 20**

> ✨ **Customizations:**  
**• 📝 Filename: Provide a custom name for your PDF.**
**• 📸 Thumbnail: Use (Filename) -t (Thumbnail link).**"""

#--------------------------------------------------------

@Client.on_callback_query(filters.regex("restricted"))
async def restricted_callback(client: Client, callback_query):
    await callback_query.answer()  # Acknowledge the callback
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="help")]
    ])
    await callback_query.message.edit_text(
        RESTRICTED_TXT,
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("combiner"))
async def combiner_callback(client: Client, callback_query):
    await callback_query.answer()  # Acknowledge the callback
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="help")]
    ])
    await callback_query.message.edit_text(
        MERGER_TXT,
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("request"))
async def request_info_callback(client: Client, callback_query):
    try:
        await callback_query.answer()  # Acknowledge the callback
        logger.info(f"Request callback triggered by {callback_query.from_user.id}")  # Log the callback query
        request_text = (
            f"> **⚙️ Join request acceptor**\n\n"
            "**• I can accept all pending join requests in your channel. 🤝**\n\n"
            "**• Promote @Axa_bachha and @Z900_RoBot with full admin rights in your channel. 🔑**\n\n"
            "**• Send /accept command to start accepting join requests. ▶️**"
        )
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 Back", callback_data="help")
            ]
        ])
        await callback_query.message.edit_text(
            request_text, 
            reply_markup=reply_markup, 
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in 'request_info_callback': {e}")
        await callback_query.answer("An error occurred. Please try again later.", show_alert=True)
      

@Client.on_callback_query(filters.regex("about"))
async def about_callback(client: Client, callback_query):
    try:
        await callback_query.answer()
        ABOUT_TXT_MSG = ABOUT_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="start"), InlineKeyboardButton("🕒 ᴜᴘᴛɪᴍᴇ", callback_data="uptime")]
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
"""


@Client.on_callback_query(filters.regex("help"))
async def help_callback(client: Client, callback_query):
    try:
        await callback_query.answer()  # Acknowledge the callback
        logger.info(f"Help callback triggered by {callback_query.from_user.id}")  # Log the callback query
        help_text = (
            "> **📖 My Modules**\n\n"
            "**• Choose from the options below.**"
        )
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("• Join Request acceptor •", callback_data="request")],
            [InlineKeyboardButton("📃 PDF Merging 📃", callback_data="combiner")],
            [InlineKeyboardButton("🪄 Restricted content saver 🪄", callback_data="restricted")],
            [InlineKeyboardButton("🔙 Back 🔙", callback_data="start")]
        ])
        await callback_query.message.edit_text(help_text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in 'help_callback': {e}")
        await callback_query.answer("An error occurred. Please try again later.", show_alert=True)


