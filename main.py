
import logging
import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 10000))

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

GENRES = {
    "Комедия": 35,
    "Боевик": 28,
    "Драма": 18,
    "Фантастика": 878,
    "Ужасы": 27,
    "Мелодрама": 10749,
    "Триллер": 53,
}

@dp.message()
async def handle_all_messages(message: Message):
    if message.text == "/start":
        await message.answer("Привет! Я помогу подобрать фильм на вечер.")
    elif message.text == "/жанры":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=genre, callback_data=f"genre_{genre_id}")]
            for genre, genre_id in GENRES.items()
        ])
        await message.answer("Выбери жанр:", reply_markup=keyboard)

@dp.callback_query()
async def handle_genre_callback(callback: types.CallbackQuery):
    genre_id = callback.data.split("_")[1]
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc"
    response = requests.get(url).json()
    if response["results"]:
        movie = response["results"][0]
        title = movie.get("title", "Без названия")
        overview = movie.get("overview", "Нет описания")
        text = f"<b>{title}</b>
{overview}"
        await callback.message.answer(text)
    else:
        await callback.message.answer("Не удалось найти фильм.")

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

async def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    await on_startup(bot)
    return app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(main(), host=WEBAPP_HOST, port=WEBAPP_PORT)
