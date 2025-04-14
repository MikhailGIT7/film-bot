import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://film-bot-jlbt.onrender.com{WEBHOOK_PATH}"

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

GENRES = {
    "Комедия": 35,
    "Боевик": 28,
    "Фэнтези": 14,
    "Драма": 18
}

@dp.message(lambda message: message.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот, который поможет выбрать фильм на вечер. Напиши /жанры чтобы выбрать жанр.")

@dp.message(lambda message: message.text == "/жанры")
async def cmd_genres(message: Message):
    builder = InlineKeyboardBuilder()
    for genre in GENRES:
        builder.button(text=genre, callback_data=f"genre_{GENRES[genre]}")
    await message.answer("Выберите жанр:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data.startswith("genre_"))
async def genre_selected(callback_query: types.CallbackQuery):
    genre_id = callback_query.data.split("_")[1]
    response = requests.get(
        f"https://api.themoviedb.org/3/discover/movie",
        params={"api_key": TMDB_API_KEY, "with_genres": genre_id, "language": "ru"}
    )
    data = response.json()
    if data.get("results"):
        movie = data["results"][0]
        title = movie.get("title", "Без названия")
        overview = movie.get("overview", "Описание отсутствует")
        text = f"<b>{title}</b>

{overview}"
        await callback_query.message.answer(text)
    else:
        await callback_query.message.answer("Не удалось найти фильмы в этом жанре.")

async def handle_webhook(request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")

def main():
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.on_startup.append(on_startup)
    web.run_app(app, port=10000)

if __name__ == "__main__":
    main()
