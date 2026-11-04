from os import getenv
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
from handlers.routes import router

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.include_router(router)

bot_commands = [
    BotCommand(command="start", description="Запустить бота"),
    BotCommand(command="menu", description="Открыть главное меню"),
    BotCommand(command="about", description="Информация о боте"),
    BotCommand(command="weather", description="Узнать погоду сейчас или на неделю"),
    BotCommand(command="cancel", description="Отменить текущее действие"),
    BotCommand(command="settings", description="Настройки")
]

async def main():
    bot = Bot(token=TOKEN)
    await bot.set_my_commands(bot_commands)

    print('Start...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())