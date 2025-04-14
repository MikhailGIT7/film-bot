import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from dotenv import load_dotenv
import requests

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

GENRES = {
    "28": "Экшен",
    "35": "Комедия",
    "18": "Драма",
    "27": "Ужасы",
    "10749": "Романтика",
    "878": "Фантастика"
}

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Привет! Я помогу подобрать фильм на вечер 🎬")

@dp.message(F.text == "/жанры")
async def cmd_genres(message: Message):
    kb = InlineKeyboardBuilder()
    for genre_id, genre_name in GENRES.items():
        kb.button(text=genre_name, callback_data=f"genre_{genre_id}")
    kb.adjust(2)
    await message.answer("Выбери жанр:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("genre_"))
async def genre_selected(callback: CallbackQuery):
    genre_id = callback.data.split("_")[1]
    genre_name = GENRES.get(genre_id, "Жанр")

    url = f"https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_id,
        "sort_by": "popularity.desc",
        "language": "ru-RU",
        "page": 1
    }

    response = requests.get(url, params=params)
    data = response.json()
    movies = data.get("results", [])
    if not movies:
        await callback.message.answer("Не удалось найти фильмы по жанру.")
        return

    movie = movies[0]
    title = movie.get("title", "Фильм")
    overview = movie.get("overview", "Описание недоступно.")
    rating = movie.get("vote_average", "–")

    text = f"<b>{title}</b>

{overview}

Рейтинг: {rating} ⭐️"
    await callback.message.answer(text)
    await callback.answer()

# Webhook
async def handle_webhook(request):
    body = await request.json()
    update = types.Update(**body)
    await dp.feed_update(bot, update)
    return web.Response()

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

def start():
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.on_startup.append(on_startup)
    web.run_app(app, port=10000)

if __name__ == "__main__":
    start()
