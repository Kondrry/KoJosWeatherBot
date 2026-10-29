import asyncio
import logging
from typing import Any
from weather_api import (
    get_weather_current,
    get_weather_week,
    WEATHER_DESCRIPTIONS,
    get_wind_direction,
    get_weekday
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


# Keyboards

def get_help_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Узнать погоду"), KeyboardButton(text="Узнать погоду на неделю")],
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

def get_weather_week_keyboard(day_index: int, dates: list[str]):
    day_index %= len(dates)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="<", callback_data="previous_day"), InlineKeyboardButton(text=get_weekday(dates[day_index]), callback_data=f"day_{day_index}"), InlineKeyboardButton(text=">", callback_data="next_day")],
            [InlineKeyboardButton(text="Изменить город", callback_data="change_city_week")],
        ]
    )

    return keyboard

def format_weather_week_day(place_name: str, daily: dict[str, Any], day_index: int) -> str:
    weather_code = daily["weather_code"][day_index]
    wind_direction = get_wind_direction(daily["wind_direction_10m_dominant"][day_index])
    date = daily["time"][day_index]
    
    return (
        f'🌤️ Погода в городе {place_name} на {get_weekday(date)}, {date}:\n\n'
        f'Температура: от {daily["temperature_2m_min"][day_index]}°C '
        f'до {daily["temperature_2m_max"][day_index]}°C\n'
        f'Ощущаемая температура: от {daily["apparent_temperature_min"][day_index]}°C '
        f'до {daily["apparent_temperature_max"][day_index]}°C\n'
        f'Осадки: {daily["precipitation_sum"][day_index]} мм\n'
        f'Ветер: до {daily["wind_speed_10m_max"][day_index]} м/с, '
        f'{wind_direction}\n'
        f'Погода: {WEATHER_DESCRIPTIONS.get(weather_code, "Неизвестные условия")}\n\n'
        f'ℹИсточник: Open-Meteo.'
    )

async def show_weather_week_day(callback: CallbackQuery, state: FSMContext, day_index: int) -> None:
    data = await state.get_data()
    daily = data.get("week_daily")
    place_name = data.get("week_place_name")
    if not daily or not place_name or not daily.get("time"):
        await callback.answer("Данные прогноза устарели. Запросите прогноз заново.", show_alert=True)
        return

    dates = daily["time"]
    day_index %= len(dates)
    await state.update_data(day_index=day_index)
    await callback.message.edit_text(
        format_weather_week_day(place_name, daily, day_index),
        reply_markup=get_weather_week_keyboard(day_index, dates)
    )
    await callback.answer()

# Callback queries

@router.callback_query(lambda c: c.data in {"next_day", "previous_day"})
async def process_change_day(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    day_index = data.get("day_index", 0)

    step = 1 if callback.data == "next_day" else -1
    daily = data.get("week_daily")
    if not daily or not daily.get("time"):
        await callback.answer("Данные прогноза устарели. Запросите прогноз заново.", show_alert=True)
        return

    day_index = (day_index + step) % len(daily["time"])
    await show_weather_week_day(callback, state, day_index)

    
@router.callback_query(F.data.startswith("day_"))
async def process_select_day(callback: CallbackQuery, state: FSMContext):
    day_index = int(callback.data.rsplit("_", 1)[1])
    data = await state.get_data()
    if not data.get("week_daily"):
        await show_weather_week_day(callback, state, day_index)
        return
    if day_index == data.get("day_index", 0):
        await callback.answer("Этот день уже выбран.")
        return
    await show_weather_week_day(callback, state, day_index)

@router.callback_query(lambda c: c.data == "more_info")
async def process_more_info(callback: CallbackQuery):
    await callback.message.answer("ℹ️ Дополнительная информация о боте.")
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
@router.message(F.text.lower() == "узнать погоду на неделю")
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

        date = current["time"].split("T")[0]

        await msg.answer(
            f'🌤️ Погода в городе {place_name} на {get_weekday(date)}, {date}:\n\n'
            f'Температура: {current["temperature_2m"]}°C\n'
            f'Ощущается как: {current["apparent_temperature"]}°C\n'
            f'Влажность воздуха: {current["relative_humidity_2m"]}%\n'
            f'Время суток: {"день" if current["is_day"] else "ночь"}\n'
            f'Ветер: {current["wind_speed_10m"]} м/с, {wind_direction}\n'
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

        parts = []
        for part in (
            location.get("name"),
            location.get("country")
        ):
            if part:
                parts.append(part)
        place_name = ", ".join(parts)
        await state.clear()
        await state.update_data(
            week_daily=daily,
            week_place_name=place_name,
            day_index=0,
        )

        await msg.answer(
            format_weather_week_day(place_name, daily, 0),
            reply_markup=get_weather_week_keyboard(0, daily["time"])
        )

    except (aiohttp.ClientError, asyncio.TimeoutError):
        logger.exception("Не удалось получить прогноз погоды на неделю для города %r", city)
        await msg.answer(
           '❌ Не удалось связаться с сервисом погоды. '
            'Пожалуйста, попробуйте снова позже.'
        )
        return

# Other

@router.message()
async def handle_message(msg: Message):
    await msg.answer('❌ Извини, я пока не умею обрабатывать сообщения, кроме команд. Пожалуйста, просмотри список доступных команд:\n /help 🌤️')

@router.message(Command("cancel"))
async def cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('❌ Действие отменено.')