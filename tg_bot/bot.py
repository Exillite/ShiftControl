import asyncio
import os

from aiogram import Bot, Dispatcher

from aiogram.utils.backoff import BackoffConfig
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession

from handlers import start, menu, groups, chat_events, group_detail, objects, settings, group_messages, checks, registration


BOT_TOKEN = os.getenv("BOT_TOKEN")
PROXY_URL = os.getenv("BOT_PROXY_URL")


async def main():
    session = AiohttpSession(proxy=PROXY_URL)

    backoff_config = BackoffConfig(
        min_delay=0.5,
        max_delay=3,
        factor=1.2,
        jitter=0.05
    )

    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher(storage=MemoryStorage())

    # регистрируем роутеры
    dp.include_router(start.router)
    dp.include_router(settings.router)
    dp.include_router(menu.router)
    dp.include_router(groups.router)
    dp.include_router(chat_events.router)
    dp.include_router(group_detail.router)
    dp.include_router(objects.router)
    dp.include_router(checks.router)
    dp.include_router(registration.router)
    dp.include_router(group_messages.router)

    await dp.start_polling(bot, backoff_config=backoff_config)


if __name__ == "__main__":
    asyncio.run(main())