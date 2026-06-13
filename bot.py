import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import aiohttp

MOSCOW_TZ = timezone(timedelta(hours=3))

BOT_TOKEN = os.getenv("BOT_TOKEN", "8821412858:AAHKdJcncMwRvrRRg0iXMqlpgE4xfajntlk")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

GREETING = (
    "Здравствуй, я твой персональный синоптик Руслан! 🌤\n\n"
    "Напиши мне название города или отправь свою геолокацию.\n\n"
    "📋 Все команды — /commands"
)

CITY_DB = {
    "москва": {"name": "Москва", "lat": 55.7558, "lon": 37.6173, "country": "Россия", "region": "Московская область"},
    "спб": {"name": "Санкт-Петербург", "lat": 59.9343, "lon": 30.3351, "country": "Россия", "region": "Ленинградская область"},
    "санкт-петербург": {"name": "Санкт-Петербург", "lat": 59.9343, "lon": 30.3351, "country": "Россия", "region": "Ленинградская область"},
    "новосибирск": {"name": "Новосибирск", "lat": 55.0084, "lon": 82.9357, "country": "Россия", "region": "Новосибирская область"},
    "екатеринбург": {"name": "Екатеринбург", "lat": 56.8389, "lon": 60.6057, "country": "Россия", "region": "Свердловская область"},
    "казань": {"name": "Казань", "lat": 55.7887, "lon": 49.1221, "country": "Россия", "region": "Татарстан"},
    "нижний новгород": {"name": "Нижний Новгород", "lat": 56.2965, "lon": 43.9361, "country": "Россия", "region": "Нижегородская область"},
    "челябинск": {"name": "Челябинск", "lat": 55.1644, "lon": 61.4368, "country": "Россия", "region": "Челябинская область"},
    "самара": {"name": "Самара", "lat": 53.1959, "lon": 50.1002, "country": "Россия", "region": "Самарская область"},
    "омск": {"name": "Омск", "lat": 54.9885, "lon": 73.3242, "country": "Россия", "region": "Омская область"},
    "ростов-на-дону": {"name": "Ростов-на-Дону", "lat": 47.2357, "lon": 39.7015, "country": "Россия", "region": "Ростовская область"},
    "уфа": {"name": "Уфа", "lat": 54.7388, "lon": 55.9721, "country": "Россия", "region": "Башкортостан"},
    "красноярск": {"name": "Красноярск", "lat": 56.0153, "lon": 92.8932, "country": "Россия", "region": "Красноярский край"},
    "воронеж": {"name": "Воронеж", "lat": 51.6615, "lon": 39.2003, "country": "Россия", "region": "Воронежская область"},
    "пермь": {"name": "Пермь", "lat": 58.0105, "lon": 56.2502, "country": "Россия", "region": "Пермский край"},
    "волгоград": {"name": "Волгоград", "lat": 48.7071, "lon": 44.5169, "country": "Россия", "region": "Волгоградская область"},
    "краснодар": {"name": "Краснодар", "lat": 45.0355, "lon": 38.9753, "country": "Россия", "region": "Краснодарский край"},
    "саратов": {"name": "Саратов", "lat": 51.5336, "lon": 46.0343, "country": "Россия", "region": "Саратовская область"},
    "тюмень": {"name": "Тюмень", "lat": 57.1553, "lon": 65.5619, "country": "Россия", "region": "Тюменская область"},
    "тольятти": {"name": "Тольятти", "lat": 53.5078, "lon": 49.4042, "country": "Россия", "region": "Самарская область"},
    "ижевск": {"name": "Ижевск", "lat": 56.8528, "lon": 53.2118, "country": "Россия", "region": "Удмуртия"},
    "барнаул": {"name": "Барнаул", "lat": 53.3548, "lon": 83.7696, "country": "Россия", "region": "Алтайский край"},
    "иркутск": {"name": "Иркутск", "lat": 52.2864, "lon": 104.2807, "country": "Россия", "region": "Иркутская область"},
    "хабаровск": {"name": "Хабаровск", "lat": 48.4802, "lon": 135.0927, "country": "Россия", "region": "Хабаровский край"},
    "владивосток": {"name": "Владивосток", "lat": 43.1056, "lon": 131.8735, "country": "Россия", "region": "Приморский край"},
    "ярославль": {"name": "Ярославль", "lat": 57.6261, "lon": 39.8875, "country": "Россия", "region": "Ярославская область"},
    "махачкала": {"name": "Махачкала", "lat": 42.9849, "lon": 47.5047, "country": "Россия", "region": "Дагестан"},
    "томск": {"name": "Томск", "lat": 56.4977, "lon": 84.9744, "country": "Россия", "region": "Томская область"},
    "оренбург": {"name": "Оренбург", "lat": 51.7666, "lon": 55.0977, "country": "Россия", "region": "Оренбургская область"},
    "кемерово": {"name": "Кемерово", "lat": 55.3552, "lon": 86.0878, "country": "Россия", "region": "Кемеровская область"},
    "новокузнецк": {"name": "Новокузнецк", "lat": 53.7557, "lon": 87.1099, "country": "Россия", "region": "Кемеровская область"},
    "астрахань": {"name": "Астрахань", "lat": 46.3476, "lon": 48.0336, "country": "Россия", "region": "Астраханская область"},
    "рязань": {"name": "Рязань", "lat": 54.6269, "lon": 39.6916, "country": "Россия", "region": "Рязанская область"},
    "пенза": {"name": "Пенза", "lat": 53.1959, "lon": 45.0183, "country": "Россия", "region": "Пензенская область"},
    "липецк": {"name": "Липецк", "lat": 52.6122, "lon": 39.5983, "country": "Россия", "region": "Липецкая область"},
    "киров": {"name": "Киров", "lat": 58.6035, "lon": 49.6680, "country": "Россия", "region": "Кировская область"},
    "тула": {"name": "Тула", "lat": 54.1931, "lon": 37.6173, "country": "Россия", "region": "Тульская область"},
    "калининград": {"name": "Калининград", "lat": 54.7104, "lon": 20.4522, "country": "Россия", "region": "Калининградская область"},
    "курск": {"name": "Курск", "lat": 51.7304, "lon": 36.1930, "country": "Россия", "region": "Курская область"},
    "ставрополь": {"name": "Ставрополь", "lat": 45.0445, "lon": 41.9691, "country": "Россия", "region": "Ставропольский край"},
    "ульяновск": {"name": "Ульяновск", "lat": 54.3142, "lon": 48.4031, "country": "Россия", "region": "Ульяновская область"},
    "тверь": {"name": "Тверь", "lat": 56.8587, "lon": 35.9176, "country": "Россия", "region": "Тверская область"},
    "магнитогорск": {"name": "Магнитогорск", "lat": 53.4072, "lon": 59.0473, "country": "Россия", "region": "Челябинская область"},
    "сочи": {"name": "Сочи", "lat": 43.6028, "lon": 39.7342, "country": "Россия", "region": "Краснодарский край"},
    "брянск": {"name": "Брянск", "lat": 53.2436, "lon": 34.3637, "country": "Россия", "region": "Брянская область"},
    "иваново": {"name": "Иваново", "lat": 56.9969, "lon": 40.9737, "country": "Россия", "region": "Ивановская область"},
}

geo_cache: dict[str, dict] = {}
weather_cache: dict[str, tuple[dict, datetime]] = {}
WEATHER_TTL = timedelta(minutes=10)
session: aiohttp.ClientSession | None = None

user_history: dict[int, list[dict]] = {}
user_last_city: dict[int, dict] = {}

MONTHS_RU = ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
DAYS_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

WEATHER_CODES = {
    0: "Ясно ☀️",
    1: "Преимущественно ясно 🌤",
    2: "Переменная облачность ⛅",
    3: "Пасмурно ☁️",
    45: "Туман 🌫",
    48: "Изморозь 🌫",
    51: "Лёгкая морось 🌧",
    53: "Умеренная морось 🌧",
    55: "Сильная морось 🌧",
    61: "Небольшой дождь 🌧",
    63: "Умеренный дождь 🌧",
    65: "Сильный дождь 🌧",
    71: "Небольшой снег ❄️",
    73: "Умеренный снег ❄️",
    75: "Сильный снег ❄️",
    80: "Небольшой ливень 🌧",
    81: "Умеренный ливень 🌧",
    82: "Сильный ливень 🌧",
    95: "Гроза ⛈",
    96: "Гроза с градом ⛈",
    99: "Сильная гроза с градом ⛈",
}


async def get_session() -> aiohttp.ClientSession:
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession()
    return session


async def get_coordinates(city: str):
    key = city.lower().strip()
    if key in CITY_DB:
        return CITY_DB[key]
    if key in geo_cache:
        return geo_cache[key]

    s = await get_session()
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "ru"}
    async with s.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
        data = await resp.json()
        if "results" not in data:
            return None
        result = {
            "name": data["results"][0]["name"],
            "lat": data["results"][0]["latitude"],
            "lon": data["results"][0]["longitude"],
            "country": data["results"][0].get("country", ""),
            "region": data["results"][0].get("admin1", ""),
        }
        geo_cache[key] = result
        return result


async def get_weather(lat: float, lon: float):
    cache_key = f"{round(lat, 2)},{round(lon, 2)}"
    if cache_key in weather_cache:
        cached_data, cached_time = weather_cache[cache_key]
        if datetime.now(MOSCOW_TZ) - cached_time < WEATHER_TTL:
            return cached_data

    s = await get_session()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "timezone": "auto",
    }
    async with s.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
        data = await resp.json()
        weather_cache[cache_key] = (data, datetime.now(MOSCOW_TZ))
        return data


def city_header(city_info: dict) -> str:
    region = city_info.get("region", "")
    if region and region != city_info["name"]:
        return f"🌍 {city_info['name']}, {region}"
    return f"🌍 {city_info['name']}"


def save_history(user_id: int, city_info: dict):
    if user_id not in user_history:
        user_history[user_id] = []
    entry = {"name": city_info["name"], "time": datetime.now(MOSCOW_TZ)}
    user_history[user_id] = [e for e in user_history[user_id] if e["name"] != city_info["name"]]
    user_history[user_id].insert(0, entry)
    user_history[user_id] = user_history[user_id][:10]
    user_last_city[user_id] = city_info


def get_alerts(city_info: dict, weather: dict) -> list[str]:
    alerts = []
    current = weather["current_weather"]
    temp = current["temperature"]
    wind = current["windspeed"]
    code = current["weathercode"]

    if temp <= -20:
        alerts.append(f"🥶 ЭКСТРЕМЛЬНЫЙ МОРОЗ: {temp}°C! Оставайтесь дома!")
    elif temp <= -10:
        alerts.append(f"❄️ Сильный мороз: {temp}°C. Одевайтесь тепло!")
    elif temp >= 35:
        alerts.append(f"🔥 ЭКСТРЕМЛЬНАЯ ЖАРА: {temp}°C! Пейте больше воды!")
    elif temp >= 30:
        alerts.append(f"🌡 Жара: {temp}°C. Избегайте солнца с 12:00 до 16:00.")

    if wind >= 25:
        alerts.append(f"💨 СИЛЬНЫЙ ВЕТЕР: {wind} км/ч! Будьте осторожны!")
    elif wind >= 15:
        alerts.append(f"🌬 Порывистый ветер: {wind} км/ч.")

    if code in (95, 96, 99):
        alerts.append("⛈ ГРОЗА! Не выходите из дома!")
    elif code in (65, 82):
        alerts.append("🌧 Сильный ливень! Возможны подтопления.")
    elif code in (73, 75):
        alerts.append("❄️ Сильный снегопад! Осторожно на дорогах.")

    daily = weather.get("daily")
    if daily:
        for i in range(min(3, len(daily["time"]))):
            d_max = daily["temperature_2m_max"][i]
            d_min = daily["temperature_2m_min"][i]
            d_wind = daily["windspeed_10m_max"][i]
            d_prec = daily["precipitation_sum"][i]
            date = daily["time"][i]
            day_name = "Сегодня" if i == 0 else "Завтра" if i == 1 else date

            if d_wind >= 25:
                alerts.append(f"💨 {day_name}: ветер до {d_wind} км/ч!")
            if d_prec >= 20:
                alerts.append(f"🌧 {day_name}: осадки {d_prec} мм!")
            if d_max >= 35:
                alerts.append(f"🔥 {day_name}: жара до {d_max}°C!")
            if d_min <= -20:
                alerts.append(f"🥶 {day_name}: мороз до {d_min}°C!")

    return alerts


def format_weather(city_info: dict, weather: dict) -> str:
    current = weather["current_weather"]
    temp = current["temperature"]
    wind = current["windspeed"]
    code = current["weathercode"]
    description = WEATHER_CODES.get(code, "Неизвестно")

    now_hour = current["time"][:13]
    humidity = 0
    current_idx = 0
    for i, t in enumerate(weather["hourly"]["time"]):
        if t[:13] == now_hour:
            humidity = weather["hourly"]["relative_humidity_2m"][i]
            current_idx = i
            break

    alerts = get_alerts(city_info, weather)
    alerts_text = ""
    if alerts:
        alerts_text = "\n\n⚠️ ПРЕДУПРЕЖДЕНИЯ:\n" + "\n".join(alerts)

    hourly_lines = []
    hourly = weather["hourly"]
    for i in range(current_idx, min(current_idx + 12, len(hourly["time"]))):
        t = hourly["time"][i]
        hour = t[11:16]
        h_temp = hourly["temperature_2m"][i]
        h_wind = hourly["wind_speed_10m"][i]
        h_hum = hourly["relative_humidity_2m"][i]
        h_code = hourly["weathercode"][i]
        h_desc = WEATHER_CODES.get(h_code, "")
        hourly_lines.append(f"🕐 {hour}  {h_temp}°C  {h_desc}  💧{h_hum}%  💨{h_wind}км/ч")

    hourly_text = "\n".join(hourly_lines)

    return (
        f"{city_header(city_info)}\n\n"
        f"🌡 Температура: {temp}°C\n"
        f"☁️ Погода: {description}\n"
        f"💨 Ветер: {wind} км/ч\n"
        f"💧 Влажность: {humidity}%"
        f"{alerts_text}\n\n"
        f"📅 Прогноз по часам:\n"
        f"{hourly_text}"
    )


def format_weekly(city_info: dict, weather: dict) -> str:
    daily = weather.get("daily")
    if not daily:
        return "❌ Нет данных о прогнозе на неделю."

    lines = [f"{city_header(city_info)}", f"📅 Прогноз на 7 дней:\n"]

    for i in range(min(7, len(daily["time"]))):
        date_str = daily["time"][i]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = DAYS_RU[dt.weekday()]
        month_name = MONTHS_RU[dt.month - 1]
        d_max = daily["temperature_2m_max"][i]
        d_min = daily["temperature_2m_min"][i]
        d_wind = daily["windspeed_10m_max"][i]
        d_prec = daily["precipitation_sum"][i]
        d_code = daily["weathercode"][i]
        d_desc = WEATHER_CODES.get(d_code, "")
        label = "Сегодня" if i == 0 else "Завтра" if i == 1 else f"{day_name}, {dt.day} {month_name}"
        lines.append(
            f"📆 {label}\n"
            f"   {d_desc}\n"
            f"   🌡 {d_min}°C ... {d_max}°C  💨 {d_wind} км/ч  🌧 {d_prec} мм\n"
        )

    return "\n".join(lines)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(GREETING)


@dp.message(Command("commands"))
async def cmd_commands(message: Message):
    text = (
        "📋 Список команд:\n\n"
        "🏙 Название города — текущая погода + прогноз по часам на 12ч\n"
        "📍 Геолокация — погода по вашему местоположению\n"
        "📅 /week — прогноз на 7 дней\n"
        "📜 /history — история запросов\n"
        "⚠️ /alerts — предупреждения о погоде\n"
        "📧 /feedback — отправить отзыв"
    )
    await message.answer(text)


@dp.message(Command("week"))
async def cmd_week(message: Message):
    user_id = message.from_user.id
    if user_id not in user_last_city:
        await message.answer("Сначала напишите название города, затем /week")
        return
    city_info = user_last_city[user_id]
    try:
        weather = await get_weather(city_info["lat"], city_info["lon"])
        if "daily" not in weather:
            await message.answer("❌ Не удалось получить прогноз на неделю.")
            return
        result = format_weekly(city_info, weather)
        await message.answer(result)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@dp.message(Command("history"))
async def cmd_history(message: Message):
    user_id = message.from_user.id
    if user_id not in user_history or not user_history[user_id]:
        await message.answer("📭 История пуста.")
        return
    lines = ["📜 Ваши последние запросы:\n"]
    for i, entry in enumerate(user_history[user_id], 1):
        t = entry["time"].strftime("%H:%M")
        lines.append(f"{i}. {entry['name']} ({t})")
    await message.answer("\n".join(lines))


@dp.message(Command("feedback"))
async def cmd_feedback(message: Message):
    text = (
        "📧 Хотите оставить отзыв?\n\n"
        "Напишите нам на почту:\n"
        "malciksupreme@gmail.com\n\n"
        "Мы читаем каждый отзыв и стараемся стать лучше!"
    )
    await message.answer(text)


@dp.message(Command("alerts"))
async def cmd_alerts(message: Message):
    user_id = message.from_user.id
    if user_id not in user_last_city:
        await message.answer("Сначала напишите название города, затем /alerts")
        return
    city_info = user_last_city[user_id]
    weather = await get_weather(city_info["lat"], city_info["lon"])
    alerts = get_alerts(city_info, weather)
    if not alerts:
        await message.answer(f"✅ {city_info['name']}: нет предупреждений. Погода спокойная!")
    else:
        text = f"⚠️ Предупреждения для {city_info['name']}:\n\n" + "\n".join(alerts)
        await message.answer(text)


@dp.message(F.location)
async def handle_location(message: Message):
    lat = message.location.latitude
    lon = message.location.longitude
    city_info = {
        "name": "Ваше местоположение",
        "lat": lat,
        "lon": lon,
        "country": "Россия",
        "region": f"{round(lat, 4)}, {round(lon, 4)}",
    }
    save_history(message.from_user.id, city_info)
    weather = await get_weather(lat, lon)
    result = format_weather(city_info, weather)
    await message.answer(result)


@dp.message(F.text)
async def handle_city(message: Message):
    city = message.text.strip()
    if city.startswith("/"):
        return
    city_info = await get_coordinates(city)
    if not city_info:
        await message.answer("❌ Город не найден. Попробуй написать по-другому.")
        return

    save_history(message.from_user.id, city_info)
    weather = await get_weather(city_info["lat"], city_info["lon"])
    result = format_weather(city_info, weather)
    await message.answer(result)


async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        await dp.start_polling(bot)
    finally:
        if session and not session.closed:
            await session.close()


if __name__ == "__main__":
    asyncio.run(main())
