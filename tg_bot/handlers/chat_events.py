from aiogram import Router
from aiogram.types import ChatMemberUpdated

from services.api import api

router = Router()


@router.my_chat_member()
async def bot_added_to_chat(event: ChatMemberUpdated):
    new_status = event.new_chat_member.status

    if event.chat.type not in ["group", "supergroup"]:
        return

    if new_status in ["member", "administrator"]:
        chat_id = event.chat.id
        await api.create_group(chat_id)