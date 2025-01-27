import os
import shutil
import subprocess
from pydub import AudioSegment
from pydub.effects import speedup
from pyrogram import Client, filters
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Function to download and process the audio file
async def download_audio(message):
    try:
        # Get the audio file from the message
        file_id = message.audio.file_id
        file_info = await client.get_file(file_id)
        file_path = file_info.file_path

        # Download the file to a local folder
        downloaded_file = await app.download_media(file_info, file_name="downloaded_audio.mp3")

        return downloaded_file
    except Exception as e:
        logging.error(f"Error downloading audio: {e}")
        return None

# Function to apply reverb using ffmpeg
def apply_reverb(input_path, output_path):
    try:
        # Check if ffmpeg is installed
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError("ffmpeg is not installed or not found in PATH")
        
        # ffmpeg command to apply reverb
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
        logging.error(f"Error applying reverb: {e}")
        return None

# Function to process the audio (slow down and add reverb)
def process_audio(file_path):
    try:
        # Load the audio file
        sound = AudioSegment.from_file(file_path)

        # Slow down the audio by 20%
        slowed = speedup(sound, 0.8)

        # Save the slowed file temporarily
        temp_path = "temp_slowed_audio.wav"
        slowed.export(temp_path, format="wav")

        # Apply reverb to the slowed audio
        output_path = f"processed_{os.path.basename(file_path)}"
        processed_file = apply_reverb(temp_path, output_path)

        # Clean up the temporary file
        os.remove(temp_path)

        return processed_file
    except Exception as e:
        logging.error(f"Error processing audio: {e}")
        return None

# Function to send the processed audio back to the user
async def send_processed_audio(chat_id, processed_file):
    try:
        # Send the processed file to the user
        await client.send_audio(chat_id=chat_id, audio=processed_file)
        logging.info(f"Processed file sent to user: {processed_file}")
    except Exception as e:
        logging.error(f"Error sending processed audio: {e}")

# Function to handle the audio processing in the bot
@Client.on_message(filters.audio)
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


