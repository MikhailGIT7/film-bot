import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Хендлер команды /start
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Привет! Я помогу подобрать фильм на вечер 🎬")

# Хендлер команды /жанры
@dp.message(F.text == "/жанры")
async def cmd_genres(message: Message):
    genres = ["Комедия", "Боевик", "Фантастика", "Драма", "Триллер"]
    builder = InlineKeyboardBuilder()
    for genre in genres:
        builder.button(text=genre, callback_data=f"genre_{genre.lower()}")
    builder.adjust(2)
    await message.answer("Выбери жанр:", reply_markup=builder.as_markup())

# Обработка выбора жанра
@dp.callback_query(F.data.startswith("genre_"))
async def genre_selected(callback: types.CallbackQuery):
    genre = callback.data.replace("genre_", "").capitalize()
    await callback.message.answer(f"Отлично, ищу фильмы в жанре: {genre} 🎥")
    await callback.answer()

# Установка вебхука
async def on_startup(app):
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook установлен автоматически: {WEBHOOK_URL}")

# Aiohttp-приложение
app = web.Application()
app["bot"] = bot

# Подключение вебхука
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
app.on_startup.append(on_startup)

# Запуск сервера
if __name__ == "__main__":
    logging.info("Запуск бота через webhook")
    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=10000)