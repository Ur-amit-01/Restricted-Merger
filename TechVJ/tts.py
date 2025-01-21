import traceback
from asyncio import get_running_loop
from io import BytesIO
from googletrans import Translator
from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.types import Message

# Convert text to audio
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
        vj = await client.ask(
            chat_id=message.from_user.id,
            text="Now send me your text.",
            filters=filters.text,
        )

        if vj.text:
            m = await vj.reply_text("Processing...")
            text = vj.text
            loop = get_running_loop()
            audio = await loop.run_in_executor(None, convert, text)

            await vj.reply_audio(audio, caption="Here is your TTS audio!")
            await m.delete()
            audio.close()
        else:
            await vj.reply_text("Send me text only, buddy!")
    except Exception as e:
        error_message = traceback.format_exc()
        print(error_message)
        await message.reply_text(f"An error occurred:\n\n{e}")
