from pyrogram import Client, filters
from gtts import gTTS
from io import BytesIO

# Replace with your bot's token
BOT_TOKEN = "BOT_TOJEN"
API_ID = 123456  # Replace with your API ID
API_HASH = "your_api_hash"  # Replace with your API Hash

app = Client("tts_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Hello! Send the /tts command followed by text, and I'll convert it to speech!")

@app.on_message(filters.command("tts"))
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

# Run the bot
app.run()
