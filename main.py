import logging
import os
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

GENRES = {
    "Комедия": 35,
    "Боевик": 28,
    "Фантастика": 878,
    "Драма": 18,
    "Триллер": 53,
    "Мелодрама": 10749
}

@dp.message(lambda message: message.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я помогу выбрать фильм на вечер. Напиши /жанры, чтобы выбрать жанр.")

@dp.message(lambda message: message.text == "/жанры")
async def cmd_genres(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=genre, callback_data=f"genre_{genre}")] for genre in GENRES
    ])
    await message.answer("Выбери жанр:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("genre_"))
async def handle_genre(callback_query: types.CallbackQuery):
    genre_name = callback_query.data.split("_")[1]
    genre_id = GENRES.get(genre_name)
    if genre_id:
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc"
        response = requests.get(url).json()
        movies = response.get("results", [])
        if movies:
            movie = movies[0]
            title = movie["title"]
            overview = movie.get("overview", "Описание отсутствует.")
            text = f"<b>{title}</b>"

{overview}"
            await bot.send_message(callback_query.from_user.id, text)
        else:
            await bot.send_message(callback_query.from_user.id, "Фильмы не найдены.")
    else:
        await bot.send_message(callback_query.from_user.id, "Ошибка при выборе жанра.")
    await callback_query.answer()

async def on_startup(bot: Bot) -> None:
    webhook_url = f"{WEBHOOK_URL}/webhook/{API_TOKEN}"
    await bot.set_webhook(webhook_url)
    logging.info(f"Webhook установлен: {webhook_url}")

async def main():
    app = web.Application()
    dp.startup.register(on_startup)
    webhook_path = f"/webhook/{API_TOKEN}"
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)
    return app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(main(), host="0.0.0.0", port=10000)
