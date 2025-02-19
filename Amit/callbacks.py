import time
import logging
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# Initialize Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define bot start time
START_TIME = time.time()

# Random Images
random_images = [
    "https://envs.sh/Q_x.jpg",
    "https://envs.sh/Q_x.jpg"
]
# Function to Get Bot Uptime
def get_uptime():
    uptime_seconds = time.time() - start_time
    days = int(uptime_seconds // (24 * 3600))
    hours = int((uptime_seconds % (24 * 3600)) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    return f"{days}d : {hours}h : {minutes}m : {seconds}s"

# Start Command
@Client.on_message(filters.command("start"))
async def start(client: Client, m: Message):
    random_image = random.choice(random_images)
    caption = (
        "> **✨👋🏻 Hello User!**\n\n"
        "**🔋 I'm a powerful bot designed to assist you effortlessly.**\n"
        "**🔘 Use the buttons below to explore my features!**"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🕵 Help", callback_data="help"), InlineKeyboardButton("📜 About", callback_data="about")],
        [InlineKeyboardButton("❗❗ Developer ❗❗", url="https://t.me/Axa_bachha")]
    ])
    
    await client.send_photo(m.chat.id, photo=random_image, caption=caption, reply_markup=buttons)

# Callback Query Handlers
@Client.on_callback_query(filters.regex("help|about|back"))
async def callback_handler(client: Client, query: CallbackQuery):
    data = query.data
    if data == "help":
        text = "> **📖 My Modules**\n\n**• Choose from the options below.**"
        buttons = [
            [InlineKeyboardButton("📃 PDF Merging 📃", callback_data="combiner")],
            [InlineKeyboardButton("• Join Request acceptor •", callback_data="request")],
            [InlineKeyboardButton("🪄 Restricted content saver 🪄", callback_data="restricted")],
            [InlineKeyboardButton("🔙 Back 🔙", callback_data="back")]
        ]
    elif data == "about":
        text = f"""**⍟───[ MY ᴅᴇᴛᴀɪʟꜱ ]───⍟**
        
• ᴍʏ ɴᴀᴍᴇ : [z900 ⚝](https://t.me/Z900_robot)
• ᴍʏ ʙᴇsᴛ ғʀɪᴇɴᴅ : [ᴛʜɪs ᴘᴇʀsᴏɴ](tg://settings)
• ᴅᴇᴠᴇʟᴏᴘᴇʀ : [ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝](https://t.me/Ur_Amit_01)
⏳ ᴜᴘᴛɪᴍᴇ : {get_uptime()}"""
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="back")]]
    else:  # "back"
        text = "> **✨👋🏻 Hey User!**\n\n**🔋 I'm a powerful bot designed to assist you effortlessly.**\n\n**🔘 Use the buttons below to explore my features!**"
        buttons = [
            [InlineKeyboardButton("🕵 Help", callback_data="help"), InlineKeyboardButton("📜 About", callback_data="about")]
        ]

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# Uptime Handler
@Client.on_callback_query(filters.regex("uptime"))
async def uptime_callback(client: Client, query: CallbackQuery):
    await query.answer(f"🤖 Bot Uptime: {get_uptime()}", show_alert=True)

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
      
