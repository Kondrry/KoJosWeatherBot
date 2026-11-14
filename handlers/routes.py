import asyncio
import logging
from typing import Any
from translations import TRANSLATIONS
from weather_api import (
    get_weather_current,
    get_weather_week,
    get_wind_direction,
    get_weekday,
)
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand,
    BotCommandScopeChat,
)
from forms.user_info import Form
from aiogram.fsm.context import FSMContext
import aiohttp
import aiosqlite

router = Router()
logger = logging.getLogger(__name__)

# My first db interaction!!!(except translation)!!! last update :\ i guess

DB_NAME = "weather_report_bot.db"

def translate(language, section, key, **values):
    catalog = TRANSLATIONS.get(language, TRANSLATIONS["ru"])
    return catalog[section][key].format(**values)


def button_text_filter(button_key):
    labels = {
        catalog["buttons"][button_key].casefold()
        for catalog in TRANSLATIONS.values()
    }
    return lambda message: message.text is not None and message.text.casefold() in labels


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                fav_city TEXT,
                language TEXT NOT NULL DEFAULT 'ru'
                )
        """)
        cursor = await db.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in await cursor.fetchall()}
        if "language" not in columns:
            await db.execute(
                "ALTER TABLE users ADD COLUMN language TEXT NOT NULL DEFAULT 'ru'"
            )
        await db.commit()


async def get_user_language(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT language FROM users WHERE id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
    if row and row[0] in TRANSLATIONS:
        return row[0]
    return "ru"


async def set_user_language(user_id, username, language):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO users (id, username, language)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                username = excluded.username,
                language = excluded.language
            """,
            (user_id, username, language),
        )
        await db.commit()


async def add_fav_city(user_id, username, fav_city):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO users (id, username, fav_city)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                username = excluded.username,
                fav_city = excluded.fav_city
            """,
            (user_id, username, fav_city),
        )
        await db.commit()


async def get_fav_city(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT fav_city FROM users WHERE id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
    return row[0] if row and row[0] else None


async def get_fav_city_or_prompt(message: Message, user_id: int, language: str):
    fav_city = await get_fav_city(user_id)
    if fav_city:
        return fav_city

    await message.answer(
        translate(language, "messages", "fav_city_missing"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text=TRANSLATIONS[language]["buttons"]["change_fav_city"],
                    callback_data="change_fav_city",
                )
            ]]
        ),
    )
    return None


async def get_users():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT * FROM users")
        result = await cursor.fetchall()
        return result 


# Keyboards - start

def get_menu_reply_keyboard(language="ru"):
    buttons = TRANSLATIONS[language]["buttons"]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=buttons["weather"])],
            [
                KeyboardButton(text=buttons["about"]),
                KeyboardButton(text=buttons["menu"]),
                KeyboardButton(text=buttons["restart"]),
            ],
            [KeyboardButton(text=buttons["settings"])],
        ],
        resize_keyboard=True
    )

    return keyboard

def get_about_inline_keyboard(language="ru"):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=TRANSLATIONS[language]["buttons"]["contact_developer"],
                    url="https://t.me/nokojo81",
                )
            ],
            [
                InlineKeyboardButton(
                    text=TRANSLATIONS[language]["buttons"]["more_info"],
                    callback_data="more_info",
                )
            ],
        ]
    )

    return keyboard

def get_weather_week_keyboard(day_index: int, dates: list[str], language: str = "ru"):
    day_index %= len(dates)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="<", callback_data="previous_day"),
                InlineKeyboardButton(
                    text=get_weekday(dates[day_index], language),
                    callback_data=f"day_{day_index}",
                ),
                InlineKeyboardButton(text=">", callback_data="next_day"),
            ],
            [
                InlineKeyboardButton(
                    text=TRANSLATIONS[language]["buttons"]["change_city"],
                    callback_data="change_city_week",
                )
            ],
        ]
    )

    return keyboard

# Keyboards - end

# Weather formatting and display functions - start

def format_weather_week_day(
    place_name: str,
    daily: dict[str, Any],
    day_index: int,
    language: str = "ru",
) -> str:
    weather_code = daily["weather_code"][day_index]
    date = daily["time"][day_index]
    weather = TRANSLATIONS[language]["weather"]

    return translate(
        language,
        "weather",
        "weekly_template",
        place_name=place_name,
        weekday=get_weekday(date, language),
        date=date,
        temperature_min=daily["temperature_2m_min"][day_index],
        temperature_max=daily["temperature_2m_max"][day_index],
        apparent_temperature_min=daily["apparent_temperature_min"][day_index],
        apparent_temperature_max=daily["apparent_temperature_max"][day_index],
        precipitation=daily["precipitation_sum"][day_index],
        wind_speed_max=daily["wind_speed_10m_max"][day_index],
        wind_direction=get_wind_direction(
            daily["wind_direction_10m_dominant"][day_index],
            language,
        ),
        description=weather["descriptions"].get(weather_code, weather["unknown"]),
    )

async def show_weather_week_day(callback: CallbackQuery, state: FSMContext, day_index: int) -> None:
    data = await state.get_data()
    daily = data.get("week_daily")
    place_name = data.get("week_place_name")
    language = await get_user_language(callback.from_user.id)
    if (
        not callback.message
        or callback.message.message_id != data.get("week_message_id")
        or not daily
        or not place_name
        or not daily.get("time")
    ):
        await callback.answer(
            translate(language, "messages", "stale_forecast"),
            show_alert=True,
        )
        return

    dates = daily["time"]
    day_index %= len(dates)
    await state.update_data(day_index=day_index)
    await callback.message.edit_text(
        format_weather_week_day(place_name, daily, day_index, language),
        reply_markup=get_weather_week_keyboard(day_index, dates, language),
    )
    await callback.answer()

# Weather formatting and display functions - end

# Callback queries: CQ - start

@router.callback_query(lambda c: c.data in {"next_day", "previous_day"})
async def process_change_day(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    day_index = data.get("day_index", 0)

    step = 1 if callback.data == "next_day" else -1
    daily = data.get("week_daily")
    if not daily or not daily.get("time"):
        language = await get_user_language(callback.from_user.id)
        await callback.answer(
            translate(language, "messages", "stale_forecast"),
            show_alert=True,
        )
        return

    day_index = (day_index + step) % len(daily["time"])
    await show_weather_week_day(callback, state, day_index)

    
@router.callback_query(lambda c: c.data.startswith("day_"))
async def process_select_day(callback: CallbackQuery, state: FSMContext):
    day_index = int(callback.data.rsplit("_", 1)[1])
    data = await state.get_data()
    if not data.get("week_daily"):
        await show_weather_week_day(callback, state, day_index)
        return
    if day_index == data.get("day_index", 0):
        language = await get_user_language(callback.from_user.id)
        await callback.answer(
            translate(language, "messages", "day_already_selected")
        )
        return
    await show_weather_week_day(callback, state, day_index)

@router.callback_query(lambda c: c.data == "more_info")
async def process_more_info(callback: CallbackQuery):
    language = await get_user_language(callback.from_user.id)
    await callback.message.answer(translate(language, "messages", "more_info"))
    await callback.answer()

@router.callback_query(lambda c: c.data == "cancel")
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    language = await get_user_language(callback.from_user.id)
    await state.clear()
    await callback.message.answer(translate(language, "messages", "cancelled"))
    await callback.answer()

@router.callback_query(lambda c: c.data == "change_city")
async def process_change_city(callback: CallbackQuery, state: FSMContext):
    language = await get_user_language(callback.from_user.id)
    await callback.message.answer(
        translate(language, "messages", "change_city"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text=TRANSLATIONS[language]["buttons"]["cancel"],
                    callback_data="cancel",
                )
            ]]
        ),
    )
    await state.set_state(Form.city)
    await callback.answer()

@router.callback_query(lambda c: c.data == "change_city_week")
async def process_change_city_week(callback: CallbackQuery, state: FSMContext):
    language = await get_user_language(callback.from_user.id)
    await callback.message.answer(
        translate(language, "messages", "change_city_week"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text=TRANSLATIONS[language]["buttons"]["cancel"],
                    callback_data="cancel",
                )
            ]]
        ),
    )
    await state.set_state(Form.city_week)
    await callback.answer()

@router.callback_query(lambda c: c.data == "weather_now")
async def process_weather_now(callback: CallbackQuery, state: FSMContext):
    language = await get_user_language(callback.from_user.id)
    if (await state.get_data()).get("fav_city_search_enabled", False):
        await callback.answer()
        city = await get_fav_city_or_prompt(
            callback.message,
            callback.from_user.id,
            language,
        )
        if city:
            await send_current_weather(callback.message, city, language)
        return

    await callback.message.answer(
        translate(language, "messages", "enter_city"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text=TRANSLATIONS[language]["buttons"]["cancel"],
                    callback_data="cancel",
                )
            ]]
        ),
    )
    await state.set_state(Form.city)
    await callback.answer()

@router.callback_query(lambda c: c.data == 'weather_week')
async def process_weather_week_choice(callback: CallbackQuery, state: FSMContext):
    language = await get_user_language(callback.from_user.id)
    if (await state.get_data()).get("fav_city_search_enabled", False):
        await callback.answer()
        city = await get_fav_city_or_prompt(
            callback.message,
            callback.from_user.id,
            language,
        )
        if city:
            await send_weekly_weather(
                callback.message,
                state,
                city,
                language,
            )
        return

    await callback.message.answer(
        translate(language, "messages", "enter_city_week"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text=TRANSLATIONS[language]["buttons"]["cancel"],
                    callback_data="cancel",
                )
            ]]
        ),
    )
    await state.set_state(Form.city_week)
    await callback.answer()

@router.callback_query(lambda c: c.data == "change_fav_city")
async def process_change_fav_city(callback: CallbackQuery, state: FSMContext):
    language = await get_user_language(callback.from_user.id)
    await callback.message.answer(
        translate(language, "messages", "enter_fav_city"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(
                    text=TRANSLATIONS[language]["buttons"]["cancel"],
                    callback_data="cancel",
                )
            ]]
        ),
    )

    await state.set_state(Form.fav_city)
    await callback.answer()

@router.callback_query(lambda c: c.data == "change_language")
async def process_change_language(callback: CallbackQuery):
    language = await get_user_language(callback.from_user.id)
    await callback.message.answer(
        translate(language, "messages", "language_prompt"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Русский", callback_data="set_language_ru"),
                InlineKeyboardButton(text="English", callback_data="set_language_en")],
            ]
        )
    )

    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("set_language_"))
async def process_set_language(callback: CallbackQuery):
    language_code = callback.data.split("_")[-1]
    if language_code not in TRANSLATIONS:
        current_language = await get_user_language(callback.from_user.id)
        await callback.answer(
            translate(current_language, "messages", "language_unavailable"),
            show_alert=True,
        )
        return

    await set_user_language(
        callback.from_user.id,
        callback.from_user.username,
        language_code,
    )
    commands = TRANSLATIONS[language_code]["commands"]
    await callback.bot.set_my_commands(
        [
            BotCommand(command="start", description=commands["start"]),
            BotCommand(command="menu", description=commands["menu"]),
            BotCommand(command="about", description=commands["about"]),
            BotCommand(command="weather", description=commands["weather"]),
            BotCommand(command="cancel", description=commands["cancel"]),
            BotCommand(command="settings", description=commands["settings"]),
        ],
        scope=BotCommandScopeChat(chat_id=callback.from_user.id),
    )
    await callback.message.answer(
        translate(language_code, "messages", "language_saved"),
        reply_markup=get_menu_reply_keyboard(language_code),
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "fav_city_toggle")
async def process_fav_city_toggle(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    enabled = not data.get("fav_city_search_enabled", False)
    await state.update_data(fav_city_search_enabled=enabled)

    language = await get_user_language(callback.from_user.id)
    buttons = TRANSLATIONS[language]["buttons"]
    status = " ✅" if enabled else " ❌"

    await callback.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=buttons["weather_now"], callback_data="weather_now"),
                InlineKeyboardButton(text=buttons["weather_week"], callback_data="weather_week"),
            ],
            [
                InlineKeyboardButton(
                    text=buttons["fav_city_search"].format(status=status),
                    callback_data="fav_city_toggle",
                )
            ],
        ])
    )
    await callback.answer()

# CQ - end


# Commands - start

# Start

@router.message(Command("start"))
@router.message(button_text_filter("restart"))
async def start(msg: Message, state: FSMContext):
    language = await get_user_language(msg.from_user.id)
    await state.clear()
    await msg.answer(
        translate(language, "messages", "start"),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[
                KeyboardButton(
                    text=TRANSLATIONS[language]["buttons"]["menu"]
                )
            ]],
            resize_keyboard=True,
        ),
    )


# Menu

@router.message(Command("menu"))
@router.message(button_text_filter("menu"))
async def menu(msg: Message, state: FSMContext):
    language = await get_user_language(msg.from_user.id)
    await state.clear()
    await msg.answer(
        translate(language, "messages", "menu"),
        parse_mode="HTML",
        reply_markup=get_menu_reply_keyboard(language),
    )

# About

@router.message(Command("about"))
@router.message(button_text_filter("about"))
async def about(msg: Message, state: FSMContext):
    language = await get_user_language(msg.from_user.id)
    await state.clear()
    await msg.answer(
        translate(
            language,
            "messages",
            "about",
            first_name=msg.from_user.first_name,
        ),
        reply_markup=get_about_inline_keyboard(language),
    )

# Weather

@router.message(Command('weather'))
@router.message(button_text_filter("weather"))
async def weather(msg: Message, state: FSMContext):
    language = await get_user_language(msg.from_user.id)
    buttons = TRANSLATIONS[language]["buttons"]
    await state.clear()
    await msg.answer(
        translate(language, "messages", "weather_period"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=buttons["weather_now"],
                        callback_data="weather_now",
                    ),
                    InlineKeyboardButton(
                        text=buttons["weather_week"],
                        callback_data="weather_week",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=buttons["fav_city_search"].format(status=" ❌"),
                        callback_data="fav_city_toggle",
                    )
                ]
            ]
        ),
    )

# Settings

@router.message(Command("settings"))
@router.message(button_text_filter("settings"))
async def settings(msg: Message, state: FSMContext):
    language = await get_user_language(msg.from_user.id)
    buttons = TRANSLATIONS[language]["buttons"]
    await state.clear()
    await msg.answer(
        translate(language, "messages", "settings"),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=buttons["change_fav_city"],
                        callback_data="change_fav_city",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=buttons["change_language"],
                        callback_data="change_language",
                    )
                ],
            ]
        ),
    )
    


# Commands - end


# Processes - start

@router.message(Form.city, F.text)
async def process_weather(msg: Message, state: FSMContext):
    language = await get_user_language(msg.from_user.id)
    city = msg.text.strip()
    if not city:
        await msg.answer(translate(language, "messages", "empty_city"))
        return

    await send_current_weather(msg, city, language)


async def send_current_weather(msg: Message, city: str, language: str):
    await msg.answer(
        translate(language, "messages", "searching_current", city=city)
    )

    try:
        weather_info = await get_weather_current(city, language)
        if weather_info is None:
            await msg.answer(
                translate(language, "messages", "city_not_found", city=city)
            )
            return

        location = weather_info["location"]
        current = weather_info["current"]
        weather_code = current["weather_code"]
        parts = []
        for part in (
            location.get("name"),
            location.get("country")
        ):
            if part:
                parts.append(part)

        place_name = ", ".join(parts)
        date = current["time"].split("T")[0]
        weather = TRANSLATIONS[language]["weather"]

        await msg.answer(
            translate(
                language,
                "weather",
                "current_template",
                place_name=place_name,
                weekday=get_weekday(date, language),
                date=date,
                temperature=current["temperature_2m"],
                apparent_temperature=current["apparent_temperature"],
                humidity=current["relative_humidity_2m"],
                time_of_day=weather["day" if current["is_day"] else "night"],
                wind_speed=current["wind_speed_10m"],
                wind_direction=get_wind_direction(
                    current["wind_direction_10m"],
                    language,
                ),
                description=weather["descriptions"].get(
                    weather_code,
                    weather["unknown"],
                ),
            ),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text=TRANSLATIONS[language]["buttons"]["change_city"],
                        callback_data="change_city",
                    )
                ]]
            ),
        )
    except aiohttp.ClientResponseError as error:
        logger.exception("Ошибка сервиса погоды для города %r", city)
        api_errors = TRANSLATIONS[language]["api_errors"]
        await msg.answer(
            api_errors.get(error.status, api_errors["default"])
        )
        return
    except (aiohttp.ClientError, asyncio.TimeoutError):
        logger.exception("Не удалось получить прогноз погоды для города %r", city)
        await msg.answer(
            TRANSLATIONS[language]["api_errors"]["default"]
        )
        return

@router.message(Form.city_week, F.text)
async def process_weather_week(msg: Message, state: FSMContext):
    language = await get_user_language(msg.from_user.id)
    city = msg.text.strip()
    if not city:
        await msg.answer(translate(language, "messages", "empty_city"))
        return

    await send_weekly_weather(msg, state, city, language)


async def send_weekly_weather(
    msg: Message,
    state: FSMContext,
    city: str,
    language: str,
):
    await msg.answer(
        translate(language, "messages", "searching_week", city=city)
    )

    try:
        weather_info = await get_weather_week(city, language)
        if weather_info is None:
            await msg.answer(
                translate(language, "messages", "city_not_found", city=city)
            )
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
        fav_city_search_enabled = (await state.get_data()).get(
            "fav_city_search_enabled",
            False,
        )
        await state.clear()
        await state.update_data(
            week_daily=daily,
            week_place_name=place_name,
            day_index=0,
            language=language,
            fav_city_search_enabled=fav_city_search_enabled,
        )

        forecast_message = await msg.answer(
            format_weather_week_day(place_name, daily, 0, language),
            reply_markup=get_weather_week_keyboard(0, daily["time"], language)
        )
        await state.update_data(week_message_id=forecast_message.message_id)

    except aiohttp.ClientResponseError as error:
        logger.exception("Ошибка сервиса погоды для города %r", city)
        api_errors = TRANSLATIONS[language]["api_errors"]
        await msg.answer(
            api_errors.get(error.status, api_errors["default"])
        )
        return
    except (aiohttp.ClientError, asyncio.TimeoutError):
        logger.exception("Не удалось получить прогноз погоды на неделю для города %r", city)
        await msg.answer(
            TRANSLATIONS[language]["api_errors"]["default"]
        )
        return

@router.message(Form.fav_city, F.text)
async def process_fav_city(msg: Message, state: FSMContext):
    language = await get_user_language(msg.from_user.id)
    fav_city = msg.text.strip()
    if not fav_city:
        await msg.answer(translate(language, "messages", "empty_city"))
        return

    await add_fav_city(msg.from_user.id, msg.from_user.username, fav_city)
    fav_city_search_enabled = (await state.get_data()).get(
        "fav_city_search_enabled",
        False,
    )
    await state.clear()
    await state.update_data(fav_city_search_enabled=fav_city_search_enabled)
    await msg.answer(
        translate(language, "messages", "fav_city_saved", city=fav_city)
    )

# Processes - end


# Other

@router.message(Command("cancel"))
async def cancel(msg: Message, state: FSMContext):
    language = await get_user_language(msg.from_user.id)
    await state.clear()
    await msg.answer(translate(language, "messages", "cancelled"))

@router.message()
async def handle_message(msg: Message):
    language = await get_user_language(msg.from_user.id)
    await msg.answer(translate(language, "messages", "unhandled_message"))
