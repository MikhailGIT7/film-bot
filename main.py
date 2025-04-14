
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

GENRES = [
    "Боевик", "Комедия", "Драма", "Фантастика", "Ужасы", "Мелодрама",
    "Триллер", "Анимация", "Документальный", "Приключения"
]

@dp.message(lambda message: message.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Привет! Я помогу подобрать фильм на вечер 🎬")

@dp.message(lambda message: message.text == "/жанры")
async def cmd_genres(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=genre, callback_data=f"genre_{genre}")]
            for genre in GENRES
        ]
    )
    await message.answer("Выберите жанр:", reply_markup=keyboard)

@dp.callback_query(lambda call: call.data.startswith("genre_"))
async def handle_genre_selection(callback_query: types.CallbackQuery):
    genre = callback_query.data.split("_", 1)[1]
    await callback_query.message.answer(f"Вы выбрали жанр: {genre}")
    await callback_query.answer()

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def main():
    app = web.Application()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    return app

if __name__ == "__main__":
    web.run_app(main(), host="0.0.0.0", port=10000)
