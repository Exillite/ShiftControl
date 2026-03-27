import os
from celery import Celery
from aiogram.types import Message
from aiogram import Bot

celery = Celery(
    "bot",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

async def send_message_to_queue(message: Message, bot: Bot):
    try:
        photo = message.photo[-1]
        file_id = photo.file_id

        file = await bot.get_file(file_id)

        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"

        
        celery.send_task(
            "core.tasks.new_message.process_new_message",
            kwargs={
                "tg_user_id": message.from_user.id,
                "tg_chat_id": message.chat.id,
                "tg_message_id": message.message_id,
                "message_send_at": message.date,
                "message_text": message.caption or "",
                "message_photo_url": file_url
            }
        )

    except Exception as e:
        print(f"Error processing message: {e}")