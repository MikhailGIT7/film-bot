import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://film-bot-jlbt.onrender.com{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

genres = {
    "Комедия": 35,
    "Боевик": 28,
    "Триллер": 53,
    "Драма": 18,
    "Фантастика": 878,
    "Ужасы": 27
}

genre_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=g)] for g in genres],
    resize_keyboard=True
)

@dp.message(commands=["start"])
async def cmd_start(message: Message):
    await message.answer("Привет! Отправь команду /жанры, чтобы выбрать жанр фильма.")

@dp.message(commands=["жанры"])
async def cmd_genres(message: Message):
    await message.answer("Выбери жанр фильма:", reply_markup=genre_keyboard)

@dp.message()
async def recommend_film(message: Message):
    genre_name = message.text
    genre_id = genres.get(genre_name)
    if not genre_id:
        await message.answer("Пожалуйста, выбери жанр из списка.")
        return

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=ru-RU&sort_by=popularity.desc&with_genres={genre_id}"
    response = requests.get(url)
    data = response.json()

    if "results" not in data or not data["results"]:
        await message.answer("Не удалось найти фильм.")
        return

    movie = data["results"][0]
    title = movie["title"]
    overview = movie.get("overview", "Описание недоступно.")
    rating = movie.get("vote_average", "N/A")

    text = f"<b>{title}</b>

{overview}

Рейтинг: {rating}"
    await message.answer(text)

async def on_startup(dispatcher: Dispatcher):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dispatcher: Dispatcher):
    await bot.delete_webhook()

async def main():
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp)
    return app

if __name__ == "__main__":
    web.run_app(main(), host="0.0.0.0", port=10000)
