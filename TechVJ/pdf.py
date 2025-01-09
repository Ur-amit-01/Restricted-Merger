import fitz  # PyMuPDF
import logging 
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from PyPDF2 import PdfMerger
import tempfile

# Set up logging
logger = logging.getLogger(__name__)

# PDF inversion function
async def invert_pdf(input_file, output_file):
    try:
        pdf_document = fitz.open(input_file)
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            # Get the page's pixmap (image representation)
            pix = page.get_pixmap()
            # Invert colors
            inverted_pix = pix.invert_()
            # Save the inverted pixmap back to the page
            page.insert_image(page.rect, pixmap=inverted_pix)
        # Save the inverted PDF
        pdf_document.save(output_file)
        pdf_document.close()
    except Exception as e:
        return str(e)
    return None

# Collection for user PDFs (for merging)
user_pdf_collection = {}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
pending_filename_requests = {}

# Keep track of user states
user_states = {}

# Handle /invert command
@Client.on_message(filters.command(["invert"]) & filters.private)
async def handle_invert_command(client: Client, message: Message):
    logger.info(f"/invert command triggered by user {message.from_user.id}")
    user_states[message.from_user.id] = 'invert'  # Set user state to 'invert'
    await message.reply_text("Send me a PDF to invert its colors (positive to negative).")

# Handle /merge command
@Client.on_message(filters.command(["merge"]))
async def start_pdf_collection(client: Client, message: Message):
    logger.info(f"/merge command triggered by user {message.from_user.id}")
    user_id = message.from_user.id
    user_pdf_collection[user_id] = []  # Initialize an empty list for storing PDF files
    user_states[user_id] = 'merge'  # Set user state to 'merge'
    await message.reply_text(
        "Now, Send your PDFs 📑 one by one. Use /done ✅ to merge."
    )

# Handle /done command (for filename)
@Client.on_message(filters.command(["done"]))
async def request_filename(client: Client, message: Message):
    logger.info(f"/done command triggered by user {message.from_user.id}")
    user_id = message.from_user.id

    if user_id not in user_pdf_collection or len(user_pdf_collection[user_id]) < 2:
        await message.reply_text(
            "Send at least 2 PDFs 📑 before using /done. Start fresh with /merge 🔄."
        )
        return

    pending_filename_requests[user_id] = True
    await message.reply_text(
        "Send the name for your merged PDF 📄 (no extension) ✍️."
    )

# Handle filename input
@Client.on_message(filters.text & filters.private & ~filters.regex("https://t.me/"))
async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id not in pending_filename_requests:
        return  

    custom_filename = message.text.strip()
    if not custom_filename:  # Validate filename
        await message.reply_text("Filename cannot be empty. Please try again.")
        return

    custom_filename = os.path.splitext(custom_filename)[0]
    custom_filename = custom_filename.replace("/", "_").replace("\\", "_").strip()

    if not custom_filename:  # Check again after sanitization
        await message.reply_text("Invalid filename. Please try again.")
        return
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        output_file = temp_file.name

    # Merge PDFs
    try:
        merger = PdfMerger()
        for pdf in user_pdf_collection[user_id]:
            merger.append(pdf)
        merger.write(output_file)
        merger.close()

        await client.send_document(
            chat_id=message.chat.id,
            document=output_file,
            caption=f"Here is your merged PDF. ✅",
            file_name=f"{custom_filename}.pdf",
        )

        await message.reply_text("Your PDFs have been successfully merged!")
    
    except Exception as e:
        await message.reply_text(f"Failed to merge PDFs: {e}")
    
    finally:
        # Clean up temporary files
        for pdf in user_pdf_collection[user_id]:
            if os.path.exists(pdf):
                os.remove(pdf)
        user_pdf_collection.pop(user_id, None)
        if os.path.exists(output_file):
            os.remove(output_file)

        pending_filename_requests.pop(user_id, None)

# Handle PDF uploads (for merging or inversion)
@Client.on_message(filters.document & filters.private)
async def handle_pdf(client: Client, message: Message):
    user_id = message.from_user.id  # Get the user's ID

    if message.document.mime_type != "application/pdf":
        await message.reply_text("This is not a valid PDF file.")
        return

    # Handle based on user state
    if user_id not in user_states:
        return

    if user_states[user_id] == 'invert':
        # Inversion process
        await message.reply_text("Inversion process started! Please wait while I convert your PDF to a negative version...")

        try:
            temp_input = await message.download()
            temp_output = f"negative_{os.path.basename(temp_input)}"

            # Invert the PDF colors
            error = await invert_pdf(temp_input, temp_output)
            if error:
                await message.reply_text(f"Failed to invert PDF: {error}")
                return

            # Send the inverted PDF back to the user
            await client.send_document(
                chat_id=message.chat.id,
                document=temp_output,
                caption="Here is your inverted PDF! ✅",
                reply_to_message_id=message.id
            )

            # Clean up temporary files
            os.remove(temp_input)
            os.remove(temp_output)

        except Exception as e:
            await message.reply_text(f"An error occurred: {e}")
        return  # Exit after processing inversion

    elif user_states[user_id] == 'merge':
        # Merge PDFs process
        if len(user_pdf_collection[user_id]) >= 20:
            await message.reply_text(
                "You can only upload up to 20 PDFs for merging. Send /done to merge the files."
            )
            return
        
        if message.document.file_size > MAX_FILE_SIZE:
            await message.reply_text(
                "The file is too large. Please send a PDF smaller than 20MB."
            )
            return
        
        try:
            temp_file = await message.download()  
            file_name = os.path.basename(temp_file)
            user_pdf_collection[user_id].append(temp_file)

            await message.reply_text(
                f"➥ {len(user_pdf_collection[user_id])}. {file_name} ✅ "
                "Send more PDFs or use /done to merge them."
            )
        except Exception as e:
            await message.reply_text(f"❌ Failed to upload the PDF : {e}")

