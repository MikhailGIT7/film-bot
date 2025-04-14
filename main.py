import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
TMDB_TOKEN = os.getenv("TMDB_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://film-bot-jlbt.onrender.com{WEBHOOK_PATH}"

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

async def fetch_movies_by_genre(genre_id):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_TOKEN,
        "with_genres": genre_id,
        "language": "ru-RU",
        "sort_by": "popularity.desc"
    }
    response = requests.get(url, params=params)
    return response.json().get("results", [])[:5]

@dp.message(commands=["start"])
async def start_handler(message: Message):
    await message.answer("Привет! Нажми /жанры чтобы выбрать жанр фильма.")

@dp.message(commands=["жанры"])
async def genre_handler(message: Message):
    genres = {
        "Боевик": 28,
        "Комедия": 35,
        "Драма": 18,
        "Фантастика": 878,
        "Мелодрама": 10749
    }
    builder = InlineKeyboardBuilder()
    for name, genre_id in genres.items():
        builder.button(text=name, callback_data=f"genre_{genre_id}")
    await message.answer("Выберите жанр:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("genre_"))
async def handle_genre_callback(callback_query: types.CallbackQuery):
    genre_id = callback_query.data.split("_")[1]
    movies = await fetch_movies_by_genre(genre_id)
    for movie in movies:
        title = movie.get("title")
        overview = movie.get("overview")
        rating = movie.get("vote_average")
        text = (
            f"<b>{title}</b>
"
            f"{overview}
"
            f"Рейтинг: {rating}"
        )
        await callback_query.message.answer(text)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

app = web.Application()
app["bot"] = bot
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
setup_application(app, dp, bot=bot)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(app, host="0.0.0.0", port=10000)
