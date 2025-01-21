from pyrogram import Client, filters
from gtts import gTTS
from io import BytesIO

# Initialize your client (bot)
client = Client("my_bot")

@client.on_message(filters.command("tts"))
async def tts_command(client, message):
    # Extract the text after the command
    text = message.text[5:].strip()
    if not text:
        await message.reply_text("Please provide text after the /tts command. Example: /tts Hello world")
        return

    try:
        # Convert text to speech
        tts = gTTS(text=text, lang="en")
        audio = BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)

        # Send the audio file
        await client.send_audio(
            chat_id=message.chat.id,
            audio=audio,
            title="TTS Audio"
        )
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
    finally:
        # Clean up memory
        audio.close()
