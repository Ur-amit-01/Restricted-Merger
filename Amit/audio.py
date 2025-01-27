import os
import shutil
import subprocess
from pyrogram import Client, filters
from pydub import AudioSegment
from pydub.effects import speedup
import logging

# Logger setup
logger = logging.getLogger(__name__)

# Function to download audio from Telegram
async def download_audio(client, message):
    try:
        file_path = await client.download_media(message, file_name="downloaded_audio.mp3")
        return file_path
    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        return None

# Function to apply reverb using ffmpeg
def apply_reverb(input_path, output_path):
    try:
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError("ffmpeg is not installed or not found in PATH")
        
        command = [
            "ffmpeg",
            "-i", input_path,
            "-af", "aecho=0.8:0.88:60:0.4",  # Reverb effect
            output_path,
            "-y"
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    except Exception as e:
        logger.error(f"Error applying reverb: {e}")
        return None

# Function to process audio
def process_audio(file_path):
    temp_path = "temp_slowed_audio.wav"
    try:
        # Slow down audio by 20%
        sound = AudioSegment.from_file(file_path)
        slowed = speedup(sound, 0.8)

        # Export slowed audio temporarily
        slowed.export(temp_path, format="wav")

        # Apply reverb
        output_path = f"processed_{os.path.basename(file_path)}"
        processed_file = apply_reverb(temp_path, output_path)

        return processed_file
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return None
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Function to send processed audio back to user
async def send_processed_audio(client, chat_id, processed_file):
    try:
        await client.send_audio(chat_id=chat_id, audio=processed_file)
        logger.info(f"Processed audio sent: {processed_file}")
    except Exception as e:
        logger.error(f"Error sending processed audio: {e}")

# Pyrogram message handler
@Client.on_message(filters.audio)
async def handle_audio(client, message):
    # Download audio
    file_path = await download_audio(client, message)
    if not file_path:
        return

    # Process audio
    processed_file = process_audio(file_path)
    if not processed_file:
        return

    # Send processed audio
    await send_processed_audio(client, message.chat.id, processed_file)

    # Cleanup original file
    os.remove(file_path)
    os.remove(processed_file)

