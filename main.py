import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp import web
import aiohttp

TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML, session=AiohttpSession())
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
    for name in GENRES.keys():
        kb.add(InlineKeyboardButton(text=name, callback_data=f"genre:{name}"))
    return kb

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("Привет! Я помогу подобрать фильм на вечер. Выбери жанр:", reply_markup=genre_keyboard())

@dp.callback_query(F.data.startswith("genre:"))
async def genre_selected(callback: types.CallbackQuery):
    genre_name = callback.data.split(":")[1]
    genre_id = GENRES[genre_name]

    movie = await get_movie_by_genre(genre_id)
    if movie:
        text = f"<b>{movie['title']}</b> ({movie['release_date'][:4]})\n⭐ {movie['vote_average']}\n\n{movie['overview']}"
        poster = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else None

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎬 Смотреть", url=f"https://www.google.com/search?q={movie['title']} смотреть")],
                [InlineKeyboardButton(text="🔁 Другой", callback_data=f"genre:{genre_name}")]
            ]
        )

        if poster:
            await callback.message.answer_photo(photo=poster, caption=text, reply_markup=kb)
        else:
            await callback.message.answer(text, reply_markup=kb)
    else:
        await callback.message.answer("Не удалось найти фильм. Попробуйте другой жанр.")

    await callback.answer()

async def get_movie_by_genre(genre_id):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&sort_by=popularity.desc&language=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            if data.get("results"):
                return data["results"][0]
            return None

async def webhook_handler(request):
    body = await request.text()
    update = types.Update.model_validate_json(body)
    await dp.feed_update(bot, update)
    return web.Response()

app = web.Application()
app.router.add_post(WEBHOOK_PATH, webhook_handler)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True))
    logging.info(f"Webhook установлен вручную: {WEBHOOK_URL}")
    web.run_app(app, port=10000)
