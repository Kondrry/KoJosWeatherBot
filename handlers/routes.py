from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer(
        '👋 Привет! Я бот, который *поможет* тебе узнать погоду в любом городе. 🌤️\n\n💬 Напиши /help для помощи',
        parse_mode="Markdown")

@router.message(Command("help"))
async def help(msg: Message):
    await msg.answer(
        '📋 Список доступных команд:\n\n<b>/start</b> - <i>Запустить бота 🚀</i>\n<b>/help</b> - <i>Получить помощь 💡</i>\n<b>/about</b> - <i>Узнать о боте ℹ️</i>\n\nЧтобы узнать погоду в городе, просто напиши его название. Например: "Москва" или "New York". 🌍 (WIP)',
        parse_mode="HTML")

@router.message(Command("about"))
async def about(msg: Message):
    await msg.answer(f'👋 Привет, {msg.from_user.first_name}! \n\n🌤️ Это бот для получения информации о погоде.\n\n👨‍💻 Мой создатель - @nokojo81\n\n⏳ Информация будет добавлена позже.')

@router.message()
async def handle_message(msg: Message):
    await msg.answer('❌ Извини, я пока не умею обрабатывать сообщения, кроме команд. Пожалуйста, просмотри список доступных команд:\n /help 🌤️')