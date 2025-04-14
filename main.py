import logging
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

router = Router()

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("Привет! Я помогу подобрать фильм на вечер 🎬")

@router.message(F.text == "/жанры")
async def genres_handler(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎭 Драма", callback_data="genre_drama")],
        [InlineKeyboardButton(text="😂 Комедия", callback_data="genre_comedy")],
        [InlineKeyboardButton(text="🎬 Боевик", callback_data="genre_action")],
        [InlineKeyboardButton(text="😱 Ужасы", callback_data="genre_horror")],
    ])
    await message.answer("Выбери жанр:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("genre_"))
async def genre_callback_handler(callback_query):
    genre = callback_query.data.replace("genre_", "")
    await callback_query.message.answer(f"Ты выбрал жанр: {genre.capitalize()}")
    await callback_query.answer()

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot, on_startup=on_startup)

    return app

if __name__ == "__main__":
    import asyncio
    asyncio.run(web._run_app(main(), host="0.0.0.0", port=10000))