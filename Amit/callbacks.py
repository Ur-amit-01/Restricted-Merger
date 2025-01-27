from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

MERGE_TXT = """**⚙️ Hᴇʟᴘ Dᴇsᴄʀɪᴘᴛɪᴏɴ ⚙️**

📄 **/merge** - Start the merging process.  
⏳ **Upload your files (PDFs or Images) in sequence.**  
✅ **Type /done** to merge the uploaded files into a single PDF.

🔹 **Supported Files:**  
- 📑 PDFs: Add up to 20 PDF files.  
- 🖼️ Images: Convert images to PDF pages.

⚠️ **Restrictions:**  
- Max File Size: 20MB  
- Max Files per Merge: 20.

🔸 **Customizations:**  
- 📝 Filename: Provide a custom name for your PDF.  
- 📸 Thumbnail: Use (Filename) -t (Thumbnail link)."""

@Client.on_callback_query(filters.regex("mergehelp"))
async def mergehelp_callback(client: Client, callback_query):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="help")]
    ])
    await callback_query.message.edit_text(MERGE_TXT, reply_markup=reply_markup)


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
      
