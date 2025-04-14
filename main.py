
import asyncio
import os
import requests
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_TOKEN = os.getenv("TMDB_TOKEN")

dp = Dispatcher()

GENRES = {
    "драма": 18,
    "комедия": 35,
    "триллер": 53,
    "ужасы": 27,
    "фантастика": 878,
    "боевик": 28
}


def get_movie_by_genre(genre_id):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_TOKEN,
        "with_genres": genre_id,
        "sort_by": "popularity.desc",
        "language": "ru"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results:
            return None
        return results[0]
    except Exception as e:
        print(f"Error fetching movie: {e}")
        return None


@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("Привет! Напиши /жанры, чтобы выбрать жанр фильма.")


@dp.message(F.text == "/жанры")
async def show_genres(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=genre.capitalize(), callback_data=genre)]
            for genre in GENRES
        ]
    )
    await message.answer("Выберите жанр:", reply_markup=keyboard)


@dp.callback_query()
async def handle_genre(callback: types.CallbackQuery):
    genre = callback.data.lower()
    genre_id = GENRES.get(genre)
    if not genre_id:
        await callback.answer("Неизвестный жанр.")
        return

    movie = get_movie_by_genre(genre_id)
    if not movie:
        await callback.message.answer("Не удалось найти фильм.")
        await callback.answer()
        return

    title = movie.get("title")
    overview = movie.get("overview")
    poster_path = movie.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

    text = f"<b>{title}</b>\n\n{overview}"

    if poster_url:
        await callback.message.answer_photo(photo=poster_url, caption=text, parse_mode=ParseMode.HTML)
    else:
        await callback.message.answer(text, parse_mode=ParseMode.HTML)

    await callback.answer()


async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
