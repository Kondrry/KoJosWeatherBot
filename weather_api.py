from typing import Any

import aiohttp


async def get_weather(city: str) -> dict[str, Any] | None:
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(
            "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1,"language": "ru"}
        ) as response:
            response.raise_for_status()
            geocoding_data = await response.json()

        locations = geocoding_data.get("results")
        if not locations:
            return None

        location = locations[0]
        async with session.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,relative_humidity_2m,is_day,"
                    "weather_code,wind_speed_10m,wind_direction_10m"
                ),
                "wind_speed_unit": "ms",
                "timezone": "auto",
            },
        ) as response:
            response.raise_for_status()
            forecast_data = await response.json()

    return {
        "location": location,
        "current": forecast_data["current"],
    }


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