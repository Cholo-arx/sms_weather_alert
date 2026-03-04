import os
import requests
from dotenv import load_detenv

load_detenv

OPEN_API_KEY = os.getenv("OPENWEATHER_API_KEY")
SEMAPHORE_API_KEY = os.getenv("SEMAPHORE_API_KEY")
SEMAPHORE_SENDER = os.getenv("SEMAPHORE_SENDER_NAME", "WeatherAlert")
ALERT_TO_NUMBER = os.getenv("ALERT_TO_NUMBER")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

#  Warning thresholds
THRESHOLD = {
    "temp_high_c": 41,
    "temp_low_c": 0,
    "wind_speed_mps": 15,
    "humidity_pct": 90,
    "rain_1h_mm": 20,
}

# OpenWeatherMap codes
SEVERE_WEATHER_IDS = {
    # Thunderstorm
    200, 201, 202, 210, 211, 212, 221, 230, 231, 232,
    # Heavy rain / drizzle
    302, 312, 314, 321, 502, 503, 504, 511,
    # Extreme
    900, 901, 902, 903, 904, 905, 906,
    # Tornado, fog, squalls
    781,
}


def fetch_weather(city: str) -> dict:
    """Fetch current weather data from OpenWeatherMap."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q":     city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_weather_by_coords(lat: float, lon: float) -> dict:
    """Fetch current weather using latitude/longitude."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def analyze_weather(data: dict) -> list[str]:
    """
    Check weather data against thresholds.
    Returns a list of warning strings (empty = no warnings).
    """
    warnings = []

    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind_spd = data["wind"]["speed"]
    weather_id = data["weather"][0]["id"]
    description = data["weather"][0]["description"].capitalize()
    city = data["name"]
    country = data["sys"]["country"]

    rain_1h = data.get("rain", {}).get("1h", 0)

    # Temperature
    if temp >= THRESHOLDS["temp_high_c"]:
        warnings.append(f"Extreme heat: {temp:.1f}°C in {city}")
    elif temp <= THRESHOLDS["temp_low_c"]:
        warnings.append(f"Freezing temperature: {temp:.1f}°C in {city}")

    # Wind
    if wind_spd >= THRESHOLDS["wind_speed_mps"]:
        warnings.append(f"Strong winds: {wind_spd:.1f} m/s in {city}")

    # Humidity
    if humidity >= THRESHOLDS["humidity_pct"]:
        warnings.append(f"Very high humidity: {humidity}% in {city}")

    # Rain
    if rain_1h >= THRESHOLDS["rain_1h_mm"]:
        warnings.append(f"Heavy rain: {rain_1h:.1f} mm/hr in {city}")

    # Severe weather condition code
    if weather_id in SEVERE_WEATHER_IDS:
        warnings.append(
            f"Severe weather alert: {description} in {city}, {country}")

    return warnings


def check_and_alert(city: str, to_number: str = None) -> None:
    """
    Main pipeline:
      1. Fetch weather for city
      2. Analyse for warnings
      3. Send SMS if warnings exist
    """
    print(f"[+] Fetching weather for: {city}")
    data = fetch_weather(city)

    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind_spd = data["wind"]["speed"]
    description = data["weather"][0]["description"].capitalize()

    print(f"Condition : {description}")
    print(f"Temp      : {temp:.1f}°C")
    print(f"Humidity  : {humidity}%")
    print(f"Wind      : {wind_spd:.1f} m/s")

    warnings = analyze_weather(data)

    if not warnings:
        print("[✓] No weather warnings. No SMS sent.")
        return
