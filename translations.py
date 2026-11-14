TRANSLATIONS = {
    "ru": {
        "commands": {
            "start": "Запустить бота",
            "menu": "Открыть главное меню",
            "about": "Информация о боте",
            "weather": "Узнать погоду сейчас или на неделю",
            "cancel": "Отменить текущее действие",
            "settings": "Настройки",
        },
        "buttons": {
            "weather": "Узнать погоду",
            "about": "О боте",
            "menu": "Меню",
            "restart": "Перезапустить бота",
            "settings": "Настройки",
            "contact_developer": "Связаться с разработчиком",
            "more_info": "Подробнее",
            "change_city": "Изменить город",
            "change_fav_city": "Изменить любимый город",
            "change_language": "Изменить язык",
            "cancel": "Отменить действие",
            "weather_now": "Погода сейчас",
            "weather_week": "Погода на неделю",
            "fav_city_search": "Поиск по любимому городу{status}",
        },
        "messages": {
            "start": (
                "👋 Привет! Я бот, который *поможет* тебе узнать погоду в любом городе. 🌤️\n\n"
                "💬 Напиши /menu, чтобы открыть меню, или нажми кнопку ниже"
            ),
            "menu": (
                "📋 <b>Как пользоваться ботом</b>\n\n"
                "Нажми «Узнать погоду» или введи /weather, выбери текущую погоду либо прогноз "
                "на неделю и отправь название города, например: <i>Москва</i> или <i>New York</i>.\n\n"
                "🌤️ <b>Команды</b>\n"
                "<b>/start</b> — запустить или перезапустить бота\n"
                "<b>/weather</b> — выбрать текущую погоду или прогноз на неделю\n"
                "<b>/settings</b> — открыть настройки\n"
                "<b>/about</b> — информация о боте\n"
                "<b>/menu</b> — показать это меню\n"
                "<b>/cancel</b> — отменить текущее действие\n\n"
                "Также можно воспользоваться кнопками «Узнать погоду», «Настройки», «О боте» и "
                "«Меню». Во время прогноза нажми «Изменить город», чтобы выбрать другой город."
            ),
            "about": (
                "👋 Привет, {first_name}!\n\n"
                "🌤️ Я показываю текущую погоду и прогноз на неделю для выбранного или любимого города.\n"
                "🌐 Доступны русский и английский языки.\n\n"
                "Данные о погоде предоставляет Open-Meteo.\n"
                "👨‍💻 Создатель — @nokojo81."
            ),
            "weather_period": "🌤️ На какой период показать погоду?\n",
            "settings": (
                "⚙️ Настройки бота.\n\n"
                "Здесь можно изменить язык и любимый город (или города), а также другие параметры."
            ),
            "more_info": "ℹ️ Дополнительная информация о боте.",
            "cancelled": "❌ Действие отменено.",
            "change_city": (
                "🌦️ Введите новое название города, чтобы узнать погоду в нём:\n\n"
                "❌ Введите /cancel, чтобы отменить действие."
            ),
            "change_city_week": (
                "📅 Введите новое название города, чтобы узнать погоду на неделю в нём:\n\n"
                "❌ Введите /cancel, чтобы отменить действие."
            ),
            "enter_city": "🌦️ Введите название города:\n\n❌ Введите /cancel, чтобы отменить действие.",
            "enter_city_week": "📅 Введите название города для прогноза на неделю:\n\n❌ Введите /cancel, чтобы отменить действие.",
            "enter_fav_city": (
                "🏙️ Введите название города, чтобы изменить любимый город:\n\n"
                "❌ Введите /cancel, чтобы отменить действие."
            ),
            "language_prompt": "Выберите язык / Choose a language:",
            "language_saved": "✅ Язык изменён на русский.",
            "language_unavailable": "❌ Выбранный язык недоступен.",
            "language_placeholder": "Нет🤫",
            "stale_forecast": "Данные прогноза устарели. Запросите прогноз заново.",
            "day_already_selected": "Этот день уже выбран.",
            "empty_city": "❌ Введите название города.",
            "searching_current": "🔎 Ищу погоду в городе: {city}...",
            "searching_week": "🔎 Ищу погоду на неделю в городе: {city}...",
            "city_not_found": (
                "❌ Не удалось найти погоду для города: {city}. "
                "Пожалуйста, проверьте правильность написания и попробуйте снова."
            ),
            "fav_city_missing": (
                "❌ Любимый город не задан. Укажите его в настройках, затем повторите запрос."
            ),
            "fav_city_saved": "✅ Любимый город успешно изменён на: {city}.",
            "unhandled_message": (
                "❌ Извини, я пока не умею обрабатывать сообщения, кроме команд. "
                "Пожалуйста, просмотри список доступных команд:\n /menu 🌤️"
            ),
        },
        "weather": {
            "current_template": (
                "🌤️ Погода в городе {place_name} на {weekday}, {date}:\n\n"
                "Температура: {temperature}°C\n"
                "Ощущается как: {apparent_temperature}°C\n"
                "Влажность воздуха: {humidity}%\n"
                "Время суток: {time_of_day}\n"
                "Ветер: {wind_speed} м/с\n"
                "Направление ветра: {wind_direction}\n"
                "Погода: {description}\n\n"
                "ℹ️ Источник: Open-Meteo."
            ),
            "weekly_template": (
                "🌤️ Погода в городе {place_name} на {weekday}, {date}:\n\n"
                "Температура: от {temperature_min}°C до {temperature_max}°C\n"
                "Ощущаемая температура: от {apparent_temperature_min}°C "
                "до {apparent_temperature_max}°C\n"
                "Осадки: {precipitation} мм\n"
                "Ветер: до {wind_speed_max} м/с,\n"
                "Направление ветра: {wind_direction}\n"
                "Погода: {description}\n\n"
                "ℹ️ Источник: Open-Meteo."
            ),
            "day": "день",
            "night": "ночь",
            "unknown": "Неизвестные условия",
            "unknown_wind": "Неизвестно",
            "weekdays_short": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "wind_directions": [
                "Север (С)",
                "Северо-северо-восток (ССВ)",
                "Северо-восток (СВ)",
                "Востоко-северо-восток (ВСВ)",
                "Восток (В)",
                "Востоко-юго-восток (ВЮВ)",
                "Юго-восток (ЮВ)",
                "Юго-юго-восток (ЮЮВ)",
                "Юг (Ю)",
                "Юго-юго-запад (ЮЮЗ)",
                "Юго-запад (ЮЗ)",
                "Западо-юго-запад (ЗЮЗ)",
                "Запад (З)",
                "Западо-северо-запад (ЗСЗ)",
                "Северо-запад (СЗ)",
                "Северо-северо-запад (ССЗ)",
            ],
            "descriptions": {
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
            },
        },
        "api_errors": {
            429: "Слишком много запросов к сервису погоды. Подождите немного и попробуйте снова.",
            500: "В сервисе погоды произошла внутренняя ошибка. Попробуйте позже.",
            502: "Сервис погоды получил некорректный ответ. Попробуйте позже.",
            503: "Сервис погоды перегружен или временно недоступен. Попробуйте позже.",
            504: "Сервис погоды не ответил вовремя. Попробуйте позже.",
            "default": "❌ Не удалось связаться с сервисом погоды. Пожалуйста, попробуйте позже.",
        },
    },
    "en": {
        "commands": {
            "start": "Start the bot",
            "menu": "Open the main menu",
            "about": "About the bot",
            "weather": "Get current or weekly weather",
            "cancel": "Cancel the current action",
            "settings": "Settings",
        },
        "buttons": {
            "weather": "Get weather",
            "about": "About",
            "menu": "Menu",
            "restart": "Restart the bot",
            "settings": "Settings",
            "contact_developer": "Contact the developer",
            "more_info": "More information",
            "change_city": "Change city",
            "change_fav_city": "Change favorite city",
            "change_language": "Change language",
            "cancel": "Cancel",
            "weather_now": "Current weather",
            "weather_week": "Weekly forecast",
            "fav_city_search": "Search by favorite city{status}",
        },
        "messages": {
            "start": (
                "👋 Hi! I'm a bot that *helps* you check the weather in any city. 🌤️\n\n"
                "💬 Send /menu to open the menu, or press the button below."
            ),
            "menu": (
                "📋 <b>How to use the bot</b>\n\n"
                "Press “Get weather” or send /weather, choose current weather or a weekly forecast, "
                "and enter a city name, for example: <i>London</i> or <i>New York</i>.\n\n"
                "🌤️ <b>Commands</b>\n"
                "<b>/start</b> — start or restart the bot\n"
                "<b>/weather</b> — choose current weather or a weekly forecast\n"
                "<b>/settings</b> — open settings\n"
                "<b>/about</b> — about the bot\n"
                "<b>/menu</b> — show this menu\n"
                "<b>/cancel</b> — cancel the current action\n\n"
                "You can also use the “Get weather”, “Settings”, “About”, and “Menu” buttons. "
                "During a weekly forecast, press “Change city” to look up another city."
            ),
            "about": (
                "👋 Hi, {first_name}!\n\n"
                "🌤️ I provide current weather and weekly forecasts for any city or your favorite city.\n"
                "🌐 Available in Russian and English.\n\n"
                "Weather data is provided by Open-Meteo.\n"
                "👨‍💻 Created by @nokojo81."
            ),
            "weather_period": "🌤️ Which forecast would you like to see?\n",
            "settings": (
                "⚙️ Bot settings.\n\n"
                "You can change the language and favorite city (or cities), along with other options."
            ),
            "more_info": "ℹ️ More information about the bot.",
            "cancelled": "❌ Action cancelled.",
            "change_city": (
                "🌦️ Enter a new city name to get its weather:\n\n"
                "❌ Send /cancel to cancel."
            ),
            "change_city_week": (
                "📅 Enter a new city name to get its weekly forecast:\n\n"
                "❌ Send /cancel to cancel."
            ),
            "enter_city": "🌦️ Enter a city name:\n\n❌ Send /cancel to cancel.",
            "enter_city_week": "📅 Enter a city name for the weekly forecast:\n\n❌ Send /cancel to cancel.",
            "enter_fav_city": (
                "🏙️ Enter a city name to change your favorite city:\n\n"
                "❌ Send /cancel to cancel."
            ),
            "language_prompt": "Choose a language / Выберите язык:",
            "language_saved": "✅ Language changed to English.",
            "language_unavailable": "❌ The selected language is unavailable.",
            "language_placeholder": "Not yet 🤫",
            "stale_forecast": "This forecast is outdated. Please request a new forecast.",
            "day_already_selected": "This day is already selected.",
            "empty_city": "❌ Please enter a city name.",
            "searching_current": "🔎 Looking up the weather in {city}...",
            "searching_week": "🔎 Looking up the weekly forecast for {city}...",
            "city_not_found": (
                "❌ Could not find weather for {city}. "
                "Check the spelling and try again."
            ),
            "fav_city_missing": (
                "❌ No favorite city is set. Add one in Settings, then try again."
            ),
            "fav_city_saved": "✅ Favorite city changed to: {city}.",
            "unhandled_message": (
                "❌ Sorry, I can only process commands and supported actions right now. "
                "See the available commands with /menu 🌤️"
            ),
        },
        "weather": {
            "current_template": (
                "🌤️ Weather in {place_name} on {weekday}, {date}:\n\n"
                "Temperature: {temperature}°C\n"
                "Feels like: {apparent_temperature}°C\n"
                "Humidity: {humidity}%\n"
                "Time of day: {time_of_day}\n"
                "Wind: {wind_speed} m/s\n"
                "Wind direction: {wind_direction}\n"
                "Conditions: {description}\n\n"
                "ℹ️ Source: Open-Meteo."
            ),
            "weekly_template": (
                "🌤️ Weather in {place_name} for {weekday}, {date}:\n\n"
                "Temperature: {temperature_min}°C to {temperature_max}°C\n"
                "Feels like: {apparent_temperature_min}°C to {apparent_temperature_max}°C\n"
                "Precipitation: {precipitation} mm\n"
                "Wind: up to {wind_speed_max} m/s,\n"
                "Wind direction: {wind_direction}\n"
                "Conditions: {description}\n\n"
                "ℹ️ Source: Open-Meteo."
            ),
            "day": "day",
            "night": "night",
            "unknown": "Unknown conditions",
            "unknown_wind": "Unknown",
            "weekdays_short": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "wind_directions": [
                "North (N)",
                "North-northeast (NNE)",
                "Northeast (NE)",
                "East-northeast (ENE)",
                "East (E)",
                "East-southeast (ESE)",
                "Southeast (SE)",
                "South-southeast (SSE)",
                "South (S)",
                "South-southwest (SSW)",
                "Southwest (SW)",
                "West-southwest (WSW)",
                "West (W)",
                "West-northwest (WNW)",
                "Northwest (NW)",
                "North-northwest (NNW)",
            ],
            "descriptions": {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Fog",
                48: "Depositing rime fog",
                51: "Light drizzle",
                53: "Moderate drizzle",
                55: "Dense drizzle",
                56: "Light freezing drizzle",
                57: "Dense freezing drizzle",
                61: "Slight rain",
                63: "Moderate rain",
                65: "Heavy rain",
                66: "Light freezing rain",
                67: "Heavy freezing rain",
                71: "Slight snow fall",
                73: "Moderate snow fall",
                75: "Heavy snow fall",
                77: "Snow grains",
                80: "Slight rain showers",
                81: "Moderate rain showers",
                82: "Violent rain showers",
                85: "Slight snow showers",
                86: "Heavy snow showers",
                95: "Thunderstorm",
                96: "Thunderstorm with slight hail",
                99: "Thunderstorm with heavy hail",
            },
        },
        "api_errors": {
            429: "Too many requests to the weather service. Please wait a moment and try again.",
            500: "The weather service encountered an internal error. Please try again later.",
            502: "The weather service returned an invalid response. Please try again later.",
            503: "The weather service is overloaded or temporarily unavailable. Please try again later.",
            504: "The weather service did not respond in time. Please try again later.",
            "default": "❌ Could not connect to the weather service. Please try again later.",
        },
    },
}

