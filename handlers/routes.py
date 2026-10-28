import asyncio
import logging
from typing import Any
from weather_api import (
    get_weather_current,
    get_weather_week,
    WEATHER_DESCRIPTIONS,
    get_wind_direction
)
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


# 213 line check todo

# Keyboards

def get_help_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Узнать погоду"), KeyboardButton(text="Узнать погоду на неделю(WIP)")],
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

# Callback queries

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

@router.callback_query(lambda c: c.data == "change_city_week")
async def process_change_city_week(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        'Введите новое название города, чтобы узнать погоду на неделю в нём:\n\nВведите /cancel, чтобы отменить действие.', reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Отменить действие", callback_data="cancel")]])
    )
    await state.set_state(Form.city_week)
    await callback.answer()

# Start

@router.message(Command("start"))
@router.message(F.text.lower() == "перезапустить бота")
async def start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        '👋 Привет! Я бот, который *поможет* тебе узнать погоду в любом городе. 🌤️\n\n💬 Напиши /help для помощи или нажми кнопку ниже',
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
        '📋 <b>Как пользоваться ботом</b>\n\n'
        'Узнай погоду с помощью команды или кнопки меню, затем отправь название города, например: <i>Москва</i> или <i>New York</i>.\n\n'
        '🌤️ <b>Команды</b>\n'
        '<b>/start</b> — запустить или перезапустить бота\n'
        '<b>/weather</b> — узнать текущую погоду\n'
        '<b>/weather_week</b> — узнать прогноз на неделю\n'
        '<b>/about</b> — информация о боте\n'
        '<b>/help</b> — показать эту справку\n'
        '<b>/cancel</b> — отменить ввод города\n\n'
        'Можно также использовать кнопки меню: «Узнать погоду», «Узнать погоду на неделю», «О боте», «Помощь» и «Перезапустить бота».\n\n'
        'После получения прогноза нажми «Изменить город», чтобы узнать погоду в другом городе.',
        parse_mode="HTML", reply_markup=get_help_reply_keyboard())

# About

@router.message(Command("about"))
@router.message(F.text.lower() == "о боте")
async def about(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        f'👋 Привет, {msg.from_user.first_name}! \n\n🌤️ Это бот для получения информации о погоде.\n\n👨‍💻 Мой создатель - @nokojo81\n\n⏳ Информация будет добавлена позже.',
        reply_markup=get_about_inline_keyboard())

# Weather(now)

@router.message(Command('weather'))
@router.message(F.text.lower() == "узнать погоду")
async def weather(msg: Message, state: FSMContext):
        await msg.answer(
            'Введите название города, чтобы узнать погоду в нём:\n\nВведите /cancel, чтобы отменить действие.', reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Отменить действие", callback_data="cancel")]])
        )
        await state.set_state(Form.city)

# Weather(week)

@router.message(Command("weather_week"))
@router.message(F.text.lower() == "узнать погоду на неделю(WIP)")
async def weather_week(msg: Message, state: FSMContext):
    await msg.answer(
        'Введите название города, чтобы узнать погоду на неделю в нём:\n\nВведите /cancel, чтобы отменить действие.', reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Отменить действие", callback_data="cancel")]])
    )
    await state.set_state(Form.city_week)

# Processes

@router.message(Form.city, F.text)
async def process_weather(msg: Message, state: FSMContext):
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
            f'ℹИсточник: Open-Meteo.',
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


# TODO: оформить прогноз отдельно для каждого дня недели и убрать надпись WIP в команде
@router.message(Form.city_week, F.text)
async def process_weather_week(msg: Message, state: FSMContext):
    city = msg.text.strip()
    if not city:
        await msg.answer('❌ Введите название города.')
        return

    await msg.answer(f'🔎 Ищу погоду на неделю в городе: {city}...')

    try:
        weather_info = await get_weather_week(city)
        if weather_info is None:
            await msg.answer(f'❌ Не удалось найти погоду для города: {city}. Пожалуйста, проверьте правильность написания и попробуйте снова.')
            return

        location = weather_info["location"]
        daily = weather_info["daily"]
        weather_code = [
            WEATHER_DESCRIPTIONS.get(code, "Неизвестные условия") for code in daily["weather_code"]
        ]
        wind_direction = [
            get_wind_direction(direction) for direction in daily["wind_direction_10m_dominant"]
        ]
        

        parts = []
        for part in (
            location.get("name"),
            location.get("country")
        ):
            if part:
                parts.append(part)

        place_name = ", ".join(parts)

        await msg.answer(
            f'🌤️ Погода на неделю в городе {place_name}:\n\n'
            f'Температура: от {daily["temperature_2m_min"]}°C до {daily["temperature_2m_max"]}°C\n'
            f'Ощущаемая температура: от {daily["apparent_temperature_min"]}°C до {daily["apparent_temperature_max"]}°C\n'
            f'Суммарное количество осадков: {daily["precipitation_sum"]} мм\n'
            f'Ветер: до {daily["wind_speed_10m_max"]} м/с\n'
            f'Направление ветра: {wind_direction}\n'
            f'Погода: {weather_code}\n\n'
            f'ℹИсточник: Open-Meteo.',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Изменить город", callback_data="change_city_week")]])
        )
    except (aiohttp.ClientError, asyncio.TimeoutError):
        logger.exception("Не удалось получить прогноз погоды на неделю для города %r", city)
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

@router.message(Command("cancel"))
async def cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('❌ Действие отменено.')