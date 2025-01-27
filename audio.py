import os
from pydub import AudioSegment
from pydub.effects import speedup, reverb
from pyrogram import Client, filters
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Pyrogram Client Setup
app = Client("my_bot")

# Function to download and process the audio file
async def download_audio(message):
    try:
        # Get the audio file from the message
        file_id = message.audio.file_id
        file_info = await app.get_file(file_id)
        file_path = file_info.file_path

        # Download the file to a local folder
        downloaded_file = await app.download_media(file_info, file_name="downloaded_audio.mp3")

        return downloaded_file
    except Exception as e:
        logging.error(f"Error downloading audio: {e}")
        return None

# Function to process the audio (slow down and add reverb)
def process_audio(file_path):
    try:
        # Load the audio file
        sound = AudioSegment.from_file(file_path)

        # Slow down the audio by 20%
        slowed = speedup(sound, 0.8)

        # Apply reverb to the slowed audio
        audio_with_reverb = reverb(slowed)

        # Define the output path for the processed file
        output_path = f"processed_{os.path.basename(file_path)}"

        # Export the processed audio
        audio_with_reverb.export(output_path, format="mp3")

        return output_path
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return None

# Function to send the processed audio back to the user
async def send_processed_audio(chat_id, processed_file):
    try:
        # Send the processed file to the user
        await app.send_audio(chat_id=chat_id, audio=processed_file)
        logging.info(f"Processed file sent to user: {processed_file}")
    except Exception as e:
        logging.error(f"Error sending processed audio: {e}")

# Function to handle the audio processing in the bot
@app.on_message(filters.audio)
async def handle_audio(client, message):
    # Download the audio
    file_path = await download_audio(message)
    if not file_path:
        return

    # Process the audio
    processed_file = process_audio(file_path)
    if not processed_file:
        return

    # Send the processed audio back to the user
    await send_processed_audio(message.chat.id, processed_file)
