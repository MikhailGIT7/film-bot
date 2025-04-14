
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.webhook import WebhookRequestHandler
from aiohttp import web
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.router import Router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://film-bot.onrender.com{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
webhook_router = Router()

# Хендлер команды /start
@webhook_router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("Привет! Я бот, который поможет подобрать фильм на вечер 🍿")

# Добавляем роутер в диспетчер
dp.include_router(webhook_router)

# Обработка webhook-запроса от Telegram
@webhook_router.post(WEBHOOK_PATH)
async def telegram_webhook(update: dict, request: web.Request):
    telegram_update = Update.model_validate(update)
    await dp.feed_update(bot, telegram_update)
    return web.Response()

# Создание веб-приложения
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    logger.info("Webhook удалён")

def create_app():
    app = web.Application()
    app["bot"] = bot
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    return app

# Запуск
if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=10000)
