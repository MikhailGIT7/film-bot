import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
import aiohttp

# Получаем переменные окружения
TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # например: https://film-bot.onrender.com

WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Инициализация бота
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

GENRES = {
    "🎭 Драма": 18,
    "😂 Комедия": 35,
    "💥 Боевик": 28,
    "👻 Ужасы": 27,
    "🧠 Триллер": 53,
    "🚀 Фантастика": 878
}

def genre_keyboard():
    kb = InlineKeyboardMarkup()
    for name in GENRES:
        kb.add(InlineKeyboardButton(text=name, callback_data=f"genre:{name}"))
    return kb

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Привет! Выбери жанр фильма:", reply_markup=genre_keyboard())

@dp.callback_query(F.data.startswith("genre:"))
async def genre_choice(callback: types.CallbackQuery):
    genre_name = callback.data.split(":")[1]
    genre_id = GENRES.get(genre_name)

    movie = await get_movie_by_genre(genre_id)
    if movie:
        text = f"<b>{movie['title']}</b> ({movie['release_date'][:4]})\n⭐ {movie['vote_average']}\n\n{movie['overview']}"
        poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else None
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Смотреть", url=f"https://www.google.com/search?q={movie['title']} смотреть онлайн")],
                [InlineKeyboardButton(text="Другой", callback_data=f"genre:{genre_name}")]
            ]
        )
        if poster_url:
            await callback.message.answer_photo(poster_url, caption=text, reply_markup=kb)
        else:
            await callback.message.answer(text, reply_markup=kb)
    else:
        await callback.message.answer("Фильм не найден, попробуй другой жанр.")

    await callback.answer()

async def get_movie_by_genre(genre_id):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc&language=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data["results"][0] if data.get("results") else None

# Обработка входящих запросов от Telegram
async def webhook_handler(request):
    body = await request.text()
    update = types.Update.model_validate_json(body)
    await dp.feed_update(bot, update)
    return web.Response()

# Настройка aiohttp сервера
app = web.Application()
app.router.add_post(WEBHOOK_PATH, webhook_handler)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True))
    logging.info(f"Webhook установлен: {WEBHOOK_URL}")
    web.run_app(app, port=10000)
