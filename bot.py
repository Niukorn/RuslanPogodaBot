import asyncio
import logging
import os
import io
from datetime import datetime, timedelta, timezone
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BufferedInputFile
from PIL import Image, ImageDraw, ImageFont
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
    0: "Ясно",
    1: "Преим. ясно",
    2: "Облачно",
    3: "Пасмурно",
    45: "Туман",
    48: "Изморозь",
    51: "Морось",
    53: "Морось",
    55: "Сильная морось",
    61: "Дождь",
    63: "Дождь",
    65: "Сильный дождь",
    71: "Снег",
    73: "Снег",
    75: "Сильный снег",
    80: "Ливень",
    81: "Ливень",
    82: "Сильный ливень",
    95: "Гроза",
    96: "Гроза с градом",
    99: "Сильная гроза",
}

WEATHER_EMOJI = {
    0: "☀️", 1: "🌤", 2: "⛅", 3: "☁️",
    45: "🌫", 48: "🌫",
    51: "🌧", 53: "🌧", 55: "🌧",
    61: "🌧", 63: "🌧", 65: "🌧",
    71: "❄️", 73: "❄️", 75: "❄️",
    80: "🌧", 81: "🌧", 82: "🌧",
    95: "⛈", 96: "⛈", 99: "⛈",
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


def save_history(user_id: int, city_info: dict):
    if user_id not in user_history:
        user_history[user_id] = []
    entry = {"name": city_info["name"], "country": city_info.get("country", ""), "time": datetime.now(MOSCOW_TZ)}
    user_history[user_id] = [e for e in user_history[user_id] if e["name"] != city_info["name"]]
    user_history[user_id].insert(0, entry)
    user_history[user_id] = user_history[user_id][:10]
    user_last_city[user_id] = city_info


def get_temp_color(temp: float) -> tuple:
    if temp <= -20:
        return (30, 60, 120)
    elif temp <= -10:
        return (50, 80, 150)
    elif temp <= 0:
        return (70, 100, 170)
    elif temp <= 10:
        return (90, 140, 190)
    elif temp <= 20:
        return (60, 160, 120)
    elif temp <= 30:
        return (200, 160, 60)
    else:
        return (200, 80, 60)


def get_alerts(city_info: dict, weather: dict) -> list[str]:
    alerts = []
    current = weather["current_weather"]
    temp = current["temperature"]
    wind = current["windspeed"]
    code = current["weathercode"]

    if temp <= -20:
        alerts.append("ЭКСТРЕМЛЬНЫЙ МОРОЗ!")
    elif temp <= -10:
        alerts.append("Сильный мороз")
    elif temp >= 35:
        alerts.append("ЭКСТРЕМЛЬНАЯ ЖАРА!")
    elif temp >= 30:
        alerts.append("Жара")

    if wind >= 25:
        alerts.append("СИЛЬНЫЙ ВЕТЕР!")
    elif wind >= 15:
        alerts.append("Порывистый ветер")

    if code in (95, 96, 99):
        alerts.append("ГРОЗА!")
    elif code in (65, 82):
        alerts.append("Сильный ливень")
    elif code in (73, 75):
        alerts.append("Сильный снегопад")

    return alerts


def city_header(city_info: dict) -> str:
    region = city_info.get("region", "")
    if region and region != city_info["name"]:
        return f"{city_info['name']}, {region}"
    return city_info["name"]


def create_weather_card(city_info: dict, weather: dict) -> bytes:
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

    bg_color = get_temp_color(temp)
    dark_bg = tuple(max(0, c - 50) for c in bg_color)

    width, height = 800, 550
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(bg_color[0] * (1 - ratio) + dark_bg[0] * ratio)
        g = int(bg_color[1] * (1 - ratio) + dark_bg[1] * ratio)
        b = int(bg_color[2] * (1 - ratio) + dark_bg[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except Exception:
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 80)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 32)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 22)
            font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 18)
        except Exception:
            font_large = ImageFont.load_default(size=80)
            font_medium = ImageFont.load_default(size=32)
            font_small = ImageFont.load_default(size=22)
            font_tiny = ImageFont.load_default(size=18)

    city_name = city_header(city_info)
    draw.text((40, 25), city_name, fill="white", font=font_medium)

    temp_text = f"{temp}°C"
    draw.text((40, 70), temp_text, fill="white", font=font_large)

    draw.text((40, 165), description, fill=(255, 255, 255), font=font_medium)

    y_info = 215
    draw.text((40, y_info), f"Ветер: {wind} км/ч", fill="white", font=font_small)
    draw.text((350, y_info), f"Влажность: {humidity}%", fill="white", font=font_small)

    alerts = get_alerts(city_info, weather)
    if alerts:
        draw.rectangle([(30, 260), (width - 30, 295)], fill=(180, 50, 50))
        draw.text((40, 265), f"ВНИМАНИЕ: {', '.join(alerts)}", fill="white", font=font_small)

    hourly = weather["hourly"]
    table_y = 310

    draw.rectangle([(30, table_y), (width - 30, table_y + 35)], fill=(255, 255, 255, 40))
    draw.text((40, table_y + 7), "Время", fill="white", font=font_tiny)
    draw.text((150, table_y + 7), "Темп", fill="white", font=font_tiny)
    draw.text((280, table_y + 7), "Погода", fill="white", font=font_tiny)
    draw.text((440, table_y + 7), "Ветер", fill="white", font=font_tiny)
    draw.text((600, table_y + 7), "Влажн.", fill="white", font=font_tiny)

    rows = min(7, len(hourly["time"]) - current_idx)
    for i in range(rows):
        idx = current_idx + i
        row_y = table_y + 35 + i * 32
        if row_y > height - 40:
            break

        t = hourly["time"][idx]
        hour = t[11:16]
        h_temp = hourly["temperature_2m"][idx]
        h_wind = hourly["wind_speed_10m"][idx]
        h_hum = hourly["relative_humidity_2m"][idx]
        h_code = hourly["weathercode"][idx]
        h_desc = WEATHER_CODES.get(h_code, "")

        if i % 2 == 0:
            draw.rectangle([(30, row_y), (width - 30, row_y + 30)], fill=(255, 255, 255, 20))

        draw.text((40, row_y + 4), hour, fill="white", font=font_tiny)
        draw.text((150, row_y + 4), f"{h_temp}°C", fill="white", font=font_tiny)
        draw.text((280, row_y + 4), h_desc, fill="white", font=font_tiny)
        draw.text((440, row_y + 4), f"{h_wind} км/ч", fill="white", font=font_tiny)
        draw.text((600, row_y + 4), f"{h_hum}%", fill="white", font=font_tiny)

    now = datetime.now(MOSCOW_TZ).strftime("%H:%M  %d.%m.%Y")
    draw.text((width - 200, height - 30), now, fill=(255, 255, 255, 180), font=font_tiny)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def format_weather_text(city_info: dict, weather: dict) -> str:
    current = weather["current_weather"]
    temp = current["temperature"]
    wind = current["windspeed"]
    code = current["weathercode"]
    description = WEATHER_CODES.get(code, "Неизвестно")
    emoji = WEATHER_EMOJI.get(code, "🌤")

    now_hour = current["time"][:13]
    humidity = 0
    for i, t in enumerate(weather["hourly"]["time"]):
        if t[:13] == now_hour:
            humidity = weather["hourly"]["relative_humidity_2m"][i]
            break

    return (
        f"{city_header(city_info)}\n\n"
        f"{emoji} {temp}°C — {description}\n"
        f"💨 {wind} км/ч  💧 {humidity}%"
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
        d_emoji = WEATHER_EMOJI.get(d_code, "🌤")
        label = "Сегодня" if i == 0 else "Завтра" if i == 1 else f"{day_name}, {dt.day} {month_name}"
        lines.append(
            f"📆 {label}\n"
            f"   {d_emoji} {d_min}°C ... {d_max}°C  💨 {d_wind} км/ч  🌧 {d_prec} мм\n"
        )

    return "\n".join(lines)


async def get_city_by_coords(lat: float, lon: float) -> dict:
    s = await get_session()
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": "", "count": 1, "language": "ru"}
    async with s.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
        data = await resp.json()

    return {
        "name": "Ваше местоположение",
        "lat": lat,
        "lon": lon,
        "country": "Россия",
        "region": f"{round(lat, 4)}, {round(lon, 4)}",
    }


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(GREETING)


@dp.message(Command("commands"))
async def cmd_commands(message: Message):
    text = (
        "📋 Список команд:\n\n"
        "🏙 Название города — погода с картинкой\n"
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
        await message.answer(f"✅ {city_info['name']}: нет предупреждений.")
    else:
        text = f"⚠️ Предупреждения для {city_info['name']}:\n\n" + "\n".join(alerts)
        await message.answer(text)


@dp.message(F.location)
async def handle_location(message: Message):
    lat = message.location.latitude
    lon = message.location.longitude
    city_info = await get_city_by_coords(lat, lon)
    save_history(message.from_user.id, city_info)
    weather = await get_weather(lat, lon)

    card = create_weather_card(city_info, weather)
    photo = BufferedInputFile(card, filename="weather.png")
    await message.answer_photo(photo)


@dp.message(F.text)
async def handle_city(message: Message):
    city = message.text.strip()
    if city.startswith("/"):
        return
    city_info = await get_coordinates(city)
    if not city_info:
        await message.answer("❌ Город не найден.")
        return

    save_history(message.from_user.id, city_info)
    weather = await get_weather(city_info["lat"], city_info["lon"])

    card = create_weather_card(city_info, weather)
    photo = BufferedInputFile(card, filename="weather.png")
    await message.answer_photo(photo)


async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        await dp.start_polling(bot)
    finally:
        if session and not session.closed:
            await session.close()


if __name__ == "__main__":
    asyncio.run(main())
