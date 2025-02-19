import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# Configure logging
logging.basicConfig(
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Bot(Client):
    def __init__(self):
        super().__init__(
            "techvj login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="Amit"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        await super().start()
        logger.info("📀 Bot Started ⚡️ Powered By @Ur_amit_01 🚀")

    async def stop(self, *args):
        await super().stop()
        logger.info("Bot Stopped Bye")

Bot().run()
