
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Обработка команды /start
@dp.message(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привет! Я помогу подобрать фильм на вечер 🎬")

# Webhook handler
async def handle_webhook(request: web.Request):
    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.feed_update(bot, update)
    except Exception as e:
        print(f"Error in webhook: {e}")
    return web.Response()

# Запуск aiohttp сервера
app = web.Application()
app.router.add_post(f"/webhook/{BOT_TOKEN}", handle_webhook)

if __name__ == "__main__":
    print(f"Webhook установлен: https://film-bot.onrender.com/webhook/{BOT_TOKEN}")
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
