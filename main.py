
import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Обработка команды /start
@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    logger.info("Обработка команды /start")
    await message.answer("Привет! Я помогу подобрать фильм на вечер 🎬")

# Webhook handler
async def handle_webhook(request: web.Request):
    logger.info("==> Получен webhook-запрос от Telegram")
    try:
        data = await request.json()
        logger.info(f"Данные запроса: {data}")
        update = types.Update(**data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {e}")
    return web.Response()

# Запуск aiohttp сервера
app = web.Application()
app.router.add_post(f"/webhook/{BOT_TOKEN}", handle_webhook)

if __name__ == "__main__":
    logger.info(f"Webhook установлен: https://film-bot.onrender.com/webhook/{BOT_TOKEN}")
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
