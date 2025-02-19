import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from pyrogram.types import Message

# Configure logging
logging.basicConfig(
    format="%(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

random_images = [
    "https://envs.sh/Q_x.jpg",
    "https://envs.sh/Q_y.jpg"
]

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
        print("Bot started successfully!")
    
    async def set_commands(self, client, message: Message):
        if message.from_user.id not in OWNER_ID:
            await message.reply("🚫 You are not authorized to use this command.")
            return

        await client.set_bot_commands([
            BotCommand("start", "🚀 Start the bot and view the welcome message"),
            BotCommand("merge", "📎 Merge multiple PDFs or images into a single PDF"),
            BotCommand("done", "✅ Complete the merging process"),
            BotCommand("stickerid", "🆔 Get sticker ID (For Developers)"),
            BotCommand("tts", "🗣️ Convert text to speech"),
            BotCommand("accept", "✔️ Accept all pending join requests in your channel"),
        ])

        await message.reply("✅ Commands configured successfully!")

    async def start_command(self, client, message: Message):
        random_image = random.choice(random_images)

        caption = (
            f"> **✨👋🏻 Hey {message.from_user.mention} !!**\n\n"
            "**🔋 I am a powerful bot designed to assist you effortlessly.**\n\n"
            "**🔘 Use the buttons below to learn more about my functions!**"
        )

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🕵 Help", callback_data="help"), InlineKeyboardButton("📜 About", callback_data="about")],
            [InlineKeyboardButton("❗❗ Developer ❗❗", url="https://t.me/Axa_bachha")]
        ])

        await client.send_photo(
            chat_id=message.chat.id,
            photo=random_image,
            caption=caption,
            reply_markup=buttons
        )


# Initialize bot
bot = Bot()

# Register handlers
bot.add_handler(filters.command("set")(bot.set_commands))
bot.add_handler(filters.command("start")(bot.start_command))

# Run the bot
bot.run()
