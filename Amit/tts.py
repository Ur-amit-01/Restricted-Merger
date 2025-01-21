import traceback
from asyncio import get_running_loop
from io import BytesIO
from googletrans import Translator
from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.types import Message


def convert(text):
    audio = BytesIO()
    translated = Translator().translate(text, dest="en")
    lang = translated.src
    tts = gTTS(text, lang=lang)
    audio.name = lang + ".mp3"
    tts.write_to_fp(audio)
    return audio


@Client.on_message(filters.command("tts"))
async def text_to_speech(client: Client, message: Message):
    try:
        await message.reply_text("Please send me the text you want to convert to speech.")
        
        # Wait for user response
        response = await client.listen(message.chat.id, filters=filters.text, timeout=60)
        
        if response.text:
            m = await response.reply_text("Processing...")
            text = response.text
            loop = get_running_loop()
            audio = await loop.run_in_executor(None, convert, text)

            await response.reply_audio(audio, caption="Here is your audio!")
            await m.delete()
            audio.close()
        else:
            await response.reply_text("You need to send text for conversion.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(error_message)
        await message.reply_text(f"An error occurred:\n\n{e}")
