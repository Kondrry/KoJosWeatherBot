from datetime import date
import asyncio
from typing import Any
import ssl
import aiohttp
import certifi


async def get_json_with_retry(session: aiohttp.ClientSession, url: str, params: dict[str, Any]) -> dict[str, Any]:
    retry_statuses = {429, 500, 502, 503, 504}
    max_retries = 3

    for attempt in range(max_retries):
        try:
            async with session.get(url, params=params) as response:
                if response.status not in retry_statuses:
                    response.raise_for_status()
                    print(f"//Successfully fetched data from: \n{url}?{url_encode_params(params)}\nOn attempt {attempt + 1}//\n")
                    return await response.json()

                if attempt == max_retries - 1:
                    response.raise_for_status()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
            if attempt == max_retries - 1:
                raise

        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)

    raise RuntimeError(f"//Failed to fetch data from \n{url}?{url_encode_params(params)}\nAfter {max_retries} attempts.//\n")


def url_encode_params(params: dict[str, Any]) -> str:
    return "&".join(f"{k}={v}" for k, v in params.items() if v is not None)


async def get_weather_current(city: str) -> dict[str, Any] | None:
    timeout = aiohttp.ClientTimeout(total=10)
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
    ) as session:
        geocoding_data = await get_json_with_retry(
            session,
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "ru"},
        )

        locations = geocoding_data.get("results")
        if not locations:
            return None

        location = locations[0]
        forecast_data = await get_json_with_retry(
            session,
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,apparent_temperature,relative_humidity_2m,is_day,"
                    "weather_code,wind_speed_10m,wind_direction_10m"
                ),
                "wind_speed_unit": "ms",
                "timezone": "auto",
            },
        )

    return {
        "location": location,
        "current": forecast_data["current"],
    }


async def get_weather_week(city: str) -> dict[str, Any] | None:
    timeout = aiohttp.ClientTimeout(total=10)
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(
        timeout=timeout,
        connector=connector,
    ) as session:
        geocoding_data = await get_json_with_retry(
            session,
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "ru"},
        )

        locations = geocoding_data.get("results")
        if not locations:
            return None

        location = locations[0]
        forecast_data = await get_json_with_retry(
            session,
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "daily": (
                    "temperature_2m_min,temperature_2m_max,apparent_temperature_min,apparent_temperature_max,"
                    "precipitation_sum,wind_speed_10m_max,wind_direction_10m_dominant,weather_code"
                ),
                "wind_speed_unit": "ms",
                "timezone": "auto",
            },
        )
            
        return {
            "location": location,
            "daily": forecast_data["daily"],
        }

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

WEATHER_DESCRIPTIONS = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Изморозь",
    51: "Лёгкая морось",
    53: "Умеренная морось",
    55: "Сильная морось",
    56: "Лёгкая ледяная морось",
    57: "Сильная ледяная морось",
    61: "Небольшой дождь",
    63: "Умеренный дождь",
    65: "Сильный дождь",
    66: "Лёгкий ледяной дождь",
    67: "Сильный ледяной дождь",
    71: "Небольшой снег",
    73: "Умеренный снег",
    75: "Сильный снег",
    77: "Снежная крупа",
    80: "Небольшой ливень",
    81: "Умеренный ливень",
    82: "Сильный ливень",
    85: "Небольшой снежный ливень",
    86: "Сильный снежный ливень",
    95: "Гроза",
    96: "Гроза с небольшим градом",
    99: "Гроза с сильным градом",
}

WEATHER_API_ERROR_MESSAGES = {
    429: "Слишком много запросов к сервису погоды. Подождите немного и попробуйте снова.",
    500: "В сервисе погоды произошла внутренняя ошибка. Попробуйте позже.",
    502: "Сервис погоды получил некорректный ответ. Попробуйте позже.",
    503: "Сервис погоды перегружен или временно недоступен. Попробуйте позже.",
    504: "Сервис погоды не ответил вовремя. Попробуйте позже.",
}
WEATHER_API_DEFAULT_ERROR_MESSAGE = (
    "❌ Не удалось связаться с сервисом погоды. Пожалуйста, попробуйте позже."
)

def get_wind_direction(degrees):
    if degrees is None:
        return "Неизвестно"

    directions = [
        "Север (С)", "Северо-северо-восток (ССВ)", "Северо-восток (СВ)", "Востоко-северо-восток (ВСВ)",
        "Восток (В)", "Востоко-юго-восток (ВЮВ)", "Юго-восток (ЮВ)", "Юго-юго-восток (ЮЮВ)",
        "Юг (Ю)", "Юго-юго-запад (ЮЮЗ)", "Юго-запад (ЮЗ)", "Западо-юго-запад (ЗЮЗ)",
        "Запад (З)", "Западо-северо-запад (ЗСЗ)", "Северо-запад (СЗ)", "Северо-северо-запад (ССЗ)"
    ]

    index = int((degrees + 11.25) / 22.5) % 16
    return directions[index]


def get_weekday(date_str: str) -> str:
    day = date.fromisoformat(date_str)
    return WEEKDAYS[day.weekday()]
