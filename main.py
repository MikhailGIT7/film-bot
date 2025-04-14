import logging
import os
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

genres = {
    "драма": 18,
    "комедия": 35,
    "триллер": 53,
    "фантастика": 878,
    "боевик": 28,
    "приключения": 12
}

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("Привет! Напиши /жанры, чтобы выбрать жанр фильма.")

@dp.message(F.text == "/жанры")
async def genre_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=genre.title(), callback_data=f"genre_{gid}")]
            for genre, gid in genres.items()
        ]
    )
    await message.answer("Выбери жанр:", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("genre_"))
async def genre_selected(callback_query):
    genre_id = callback_query.data.split("_")[1]
    response = requests.get(
        "https://api.themoviedb.org/3/discover/movie",
        params={"api_key": TMDB_API_KEY, "with_genres": genre_id, "sort_by": "popularity.desc", "language": "ru"}
    )
    data = response.json()
    if data.get("results"):
        movie = data["results"][0]
        title = movie["title"]
        overview = movie["overview"]
        text = f"<b>{title}</b>

{overview}"
        await callback_query.message.answer(text)
    else:
        await callback_query.message.answer("Не удалось найти фильмы.")
    await callback_query.answer()

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=f"/webhook/{BOT_TOKEN}")
setup_application(app, dp, bot=bot, on_startup=on_startup)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=10000)
