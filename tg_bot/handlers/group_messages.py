from aiogram import Router, F, Bot
from aiogram.types import Message

from services.queue import send_message_to_queue

router = Router()


@router.message(F.chat.type.in_(["group", "supergroup"]) & F.photo)
async def handle_group_photo(message: Message, bot: Bot):
    await send_message_to_queue(message, bot)
