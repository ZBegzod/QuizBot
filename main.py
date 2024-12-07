import os
import asyncio

from app.user import router
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from app.database.models import async_main
from aiogram.client.default import DefaultBotProperties


async def main():
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    dp.include_routers(router)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    await dp.start_polling(bot)


async def startup(dispatcher: Dispatcher):
    await async_main()
    print('Starting up...')


async def shutdown(dispatcher: Dispatcher):
    print('Shutting down...')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
