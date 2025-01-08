import httpx
from pyrogram import Client, filters
from pyrogram.types import Message

# Replace these with your actual values
KOYEB_API_TOKEN = "tx5e5ed4i73slutfr3llbkzc2dihgvha2bnyt0law4m0ajmbfxw3xig3390xzmos"
KOYEB_SERVICE_ID = "6e055dcc-1c04-4694-b8a0-6a4b31309151"

@Client.on_message(filters.command("restart") & filters.user(7728066109))
async def restart_bot(client: Client, message: Message):
    try:
        await message.reply_text("Restarting the bot ... 🔄")
        
        # Make the API call to redeploy the service
        headers = {"Authorization": f"Bearer {KOYEB_API_TOKEN}"}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://app.koyeb.com/v1/services/{KOYEB_SERVICE_ID}/deployments",
                headers=headers
            )
        
        # Check the response status
        if response.status_code == 201:
            await message.reply_text("Bot restarted successfully! ✅")
        else:
            await message.reply_text(
                f"Failed to restart the bot. Error: {response.text}"
            )
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
