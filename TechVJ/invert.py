import fitz  # PyMuPDF
import logging 
import os
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

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

@Client.on_message(filters.command(["invert"]) & filters.private)
async def handle_invert_command(client: Client, message: Message):
    logger.info(f"/invert command triggered by user {message.from_user.id}")
    await message.reply_text("Send me a PDF to invert its colors (positive to negative).")

@Client.on_message(filters.document & filters.private)
async def handle_pdf_inversion(client: Client, message: Message):
    if message.document.mime_type != "application/pdf":
        await message.reply_text("This is not a valid PDF file. Please send a PDF.")
        return

    # Send a confirmation message before starting the inversion process
    await message.reply_text("Inversion process started! Please wait while I convert your PDF to a negative version...")

    # Download the PDF file
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
