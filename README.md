## Описание будет добавлено позже...

# Version 1.2.3
## @KoJosWeatherBot telegram bot in development
## *My *First Project* In **Python***



### Changes 1.2.3
#### eng:
- Added a Settings button and `/settings` command; the settings section is not implemented yet.
- Updated `/menu` with the available commands and current button options.
- Old weekly forecast buttons now show a stale-data notice instead of changing the latest forecast.

#### ru:
- Добавлены кнопка «Настройки» и команда `/settings`; раздел настроек пока не реализован.
- Обновлена команда `/menu`: добавлены актуальный список команд и описание кнопок.
- Старые кнопки недельного прогноза теперь сообщают, что данные устарели, вместо изменения нового прогноза.


### Changes 1.2.2
#### eng:
- The `/weather` command now lets you choose between current weather and a weekly forecast.
- Weather requests now retry after temporary server or connection errors.
- The bot gives clearer messages for common weather API errors.
- Renamed the help button and command to "Menu" and `/menu`.
- Made wind speed and direction clearer in forecast messages.

#### ru:
- Команда `/weather` теперь позволяет выбрать между текущей погодой и прогнозом на неделю.
- Бот повторяет запросы погоды при временных ошибках сервера или соединения.
- Добавлены более понятные сообщения для распространённых ошибок API погоды.
- Кнопка и команда справки переименованы в «Меню» и `/menu`.
- Скорость и направление ветра теперь отображаются понятнее.


### Changes 1.2.1
#### eng:
- You can now browse the weekly forecast one day at a time.
- The forecast updates when you switch days.
- AI helped with part of this update; I'm reviewing and cleaning up the code.

#### ru:
- Теперь прогноз на неделю можно листать по дням.
- При переключении обновляется погода для выбранного дня.
- В части изменений помог ИИ - сейчас я разбираюсь в коде и привожу его в порядок.


### Changes 1.2.0
#### eng:
- Started work on weekly weather forecasts; the feature will be improved in future updates.
- Added the option to change the city while keeping the weekly forecast mode.
- Expanded the help message with available commands and usage instructions.
- Configured Open-Meteo requests to use certifi certificates for SSL verification.

#### ru:
- Начата работа над прогнозом погоды на неделю; функция будет дорабатываться в следующих обновлениях.
- Добавлена возможность сменить город, сохранив режим недельного прогноза.
- Дополнена справка со списком команд и инструкциями по использованию.
- Настроена проверка SSL-сертификатов certifi для запросов к Open-Meteo.


### Changes 1.1.1
#### eng:
- Added current weather lookup by city using Open-Meteo.
- Added compass directions for wind.
- Added options to cancel a city search or choose another city.
- Commands and menu buttons now exit city-entry mode.
- Fixed the current weather fields requested from the API.

#### ru:
- Добавлен поиск текущей погоды по названию города через Open-Meteo.
- Добавлено отображение направления ветра по сторонам света.
- Добавлена возможность отменить поиск или выбрать другой город.
- Команды и кнопки меню теперь завершают режим ввода города.
- Исправлен список запрашиваемых у API погодных параметров.
