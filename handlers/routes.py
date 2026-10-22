import asyncio
import logging
from typing import Any
from weather_api import get_weather_current, WEATHER_DESCRIPTIONS, get_wind_direction
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from forms.user_info import Form
from aiogram.fsm.context import FSMContext
import aiohttp

router = Router()
logger = logging.getLogger(__name__)


# Keyboards

def get_help_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Узнать погоду")],
            [KeyboardButton(text="О боте"), KeyboardButton(text="Помощь"), KeyboardButton(text="Перезапустить бота")]
        ],
        resize_keyboard=True
    )

    return keyboard

def get_about_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Связаться с разработчиком", url="https://t.me/nokojo81")],
            [InlineKeyboardButton(text="Подробнее", callback_data="more_info")]
        ]
    )

    return keyboard

@router.callback_query(lambda c: c.data == "more_info")
async def process_more_info(callback: CallbackQuery):
    await callback.message.answer("ℹ️ Здесь будет дополнительная информация о боте. (WIP)")
    await callback.answer()

@router.callback_query(lambda c: c.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('❌ Действие отменено.')
    await callback.answer()

@router.callback_query(lambda c: c.data == "change_city")
async def process_change_city(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        'Введите новое название города, чтобы узнать погоду в нём:\n\nВведите /cancel, чтобы отменить действие.', reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Отменить действие", callback_data="cancel")]])
    )
    await state.set_state(Form.city)
    await callback.answer()

# Start

@router.message(Command("start"))
@router.message(F.text.lower() == "перезапустить бота")
async def start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        '👋 Привет! Я бот, который *поможет* тебе узнать погоду в любом городе. 🌤️\n\n💬 Напиши /help для помощи',
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Помощь")]], resize_keyboard=True)
    )


# Help

@router.message(Command("help"))
@router.message(F.text.lower() == "помощь")
async def help(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        '📋 Список доступных команд:\n\n<b>/start</b> - <i>Запустить бота 🚀</i>\n<b>/weather</b> - <i>Узнать погоду 🌤️</i>\n<b>/help</b> - <i>Получить помощь 💡</i>\n<b>/about</b> - <i>Узнать о боте ℹ️</i>\n\nЧтобы узнать погоду в городе, просто напиши команду <b>Узнать погоду</b> и его название. Например: "Москва" или "New York". 🌍 (WIP)',
        parse_mode="HTML", reply_markup=get_help_reply_keyboard())

# About

@router.message(Command("about"))
@router.message(F.text.lower() == "о боте")
async def about(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        f'👋 Привет, {msg.from_user.first_name}! \n\n🌤️ Это бот для получения информации о погоде.\n\n👨‍💻 Мой создатель - @nokojo81\n\n⏳ Информация будет добавлена позже.',
        reply_markup=get_about_inline_keyboard())

# Weather

@router.message(Command("cancel"))
async def cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('❌ Действие отменено.')

@router.message(Command('weather'))
@router.message(F.text.lower() == "узнать погоду")
async def weather(msg: Message, state: FSMContext):
        await msg.answer(
            'Введите название города, чтобы узнать погоду в нём:\n\nВведите /cancel, чтобы отменить действие.', reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Отменить действие", callback_data="cancel")]])
        )
        await state.set_state(Form.city)

@router.message(Form.city, F.text)
async def process_city(msg: Message, state: FSMContext):
    city = msg.text.strip()
    if not city:
        await msg.answer('❌ Введите название города.')
        return

    await msg.answer(f'🔎 Ищу погоду в городе: {city}...')

    try:
        weather_info = await get_weather_current(city)
        if weather_info is None:
            await msg.answer(f'❌ Не удалось найти погоду для города: {city}. Пожалуйста, проверьте правильность написания и попробуйте снова.')
            return

        location = weather_info["location"]
        current = weather_info["current"]
        weather_code = current["weather_code"]
        wind_direction = get_wind_direction(current["wind_direction_10m"])
        # меньше писать но труднее понять --\\
        
        # place_name = ", ".join(
        #     part
        #     for part in (location.get("name"), location.get("admin1"), location.get("country"))
        #     if part
        # )
        # --//

        # больше писать но легче понять --\\
        parts = []
        for part in (
            location.get("name"),
            location.get("country")
        ):
            if part:
                parts.append(part)

        place_name = ", ".join(parts)
        # --//

        await msg.answer(
            f'🌤️ Погода в городе {place_name}:\n\n'
            f'Температура: {current["temperature_2m"]}°C\n'
            f'Влажность воздуха: {current["relative_humidity_2m"]}%\n'
            f'Время суток: {"день" if current["is_day"] else "ночь"}\n'
            f'Скорость ветра: {current["wind_speed_10m"]} м/с\n'
            f'Направление ветра: {wind_direction}\n'
            f'Погода: {WEATHER_DESCRIPTIONS.get(weather_code, "Неизвестные условия")}\n\n'
            f'❗️ Данные предоставлены Open-Meteo и могут быть неточными.',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Изменить город", callback_data="change_city")]])
        )
    except (aiohttp.ClientError, asyncio.TimeoutError):
        logger.exception("Не удалось получить прогноз погоды для города %r", city)
        await msg.answer(
            '❌ Не удалось связаться с сервисом погоды. '
            'Пожалуйста, попробуйте снова позже.'
        )
        return

    await state.clear()

# Other

@router.message()
async def handle_message(msg: Message):
    await msg.answer('❌ Извини, я пока не умею обрабатывать сообщения, кроме команд. Пожалуйста, просмотри список доступных команд:\n /help 🌤️')