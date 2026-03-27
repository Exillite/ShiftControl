import asyncio
import datetime
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
import aiohttp

from celery import Celery


BOT_TOKEN = os.getenv("BOT_TOKEN")

PROXY_URL = os.getenv("BOT_PROXY_URL")

CORE_SERVER_URL = os.getenv("CORE_SERVER_URL")

dp = Dispatcher()

celery = Celery(
    "bot",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)



@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я бот 🚀")



ALLOWED_USERS = {
    "exillite",
    "username2",
    "username3"
}

@dp.message(Command("app"))
async def app_handler(message: Message):
    username = message.from_user.username

    if username not in ALLOWED_USERS:
        await message.answer("⛔ У вас нет доступа")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⚙️ Открыть Mini App",
                web_app=WebAppInfo(url="https://0777399e222ce79b-138-124-104-206.serveousercontent.com")
            )
        ]
    ])

    await message.answer("Доступ разрешён", reply_markup=kb)


@dp.message(F.photo)
async def handle_photo(message: Message):

    try:
        photo = message.photo[-1]

        celery.send_task(
            "core.tasks.new_message.process_new_message",
            kwargs={
                "tg_user_id": message.from_user.id,
                "tg_chat_id": message.chat.id,
                "tg_message_id": message.message_id,
                "message_send_at": message.date,
                "message_text": message.caption or "",
                "message_file_id": photo.file_id
            }
        )

    except Exception as e:
        print(f"Error processing message: {e}")


async def main():
    print("Bot started with proxy...")

    session = AiohttpSession(proxy=PROXY_URL)

    bot = Bot(token=BOT_TOKEN, session=session)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())