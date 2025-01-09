import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
            plugins=dict(root="TechVJ"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        await super().start()
        logger.info("Bot Started Powered By @VJ_Botz")

    async def stop(self, *args):
        await super().stop()
        logger.info("Bot Stopped Bye")

Bot().run()
