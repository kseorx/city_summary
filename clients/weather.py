from clients.http import fetch_get, ExternalServiceError
from requests.exceptions import HTTPError

class CityNotFoundError(Exception):
    pass

def get_weather(city: str) -> dict:
    if not city:
        raise ValueError("Название города не может быть пустым")
        
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    try:
        geo_data = fetch_get(geo_url, params={"name": city, "count": 1, "format": "json"})
    except ExternalServiceError as e:
        raise ExternalServiceError(f"Ошибка сервиса геокодинга: {e}")
        
    if not geo_data.get("results"):
        raise CityNotFoundError(f"Город '{city}' не найден")
        
    location = geo_data["results"][0]
    lat = location["latitude"]
    lon = location["longitude"]
    city_name = location.get("name", city)
    
    weather_url = "https://api.open-meteo.com/v1/forecast"
    try:
        weather_data = fetch_get(weather_url, params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        })
    except ExternalServiceError as e:
        raise ExternalServiceError(f"Ошибка сервиса погоды: {e}")
        
    current = weather_data.get("current_weather")
    if not current:
        raise ExternalServiceError("Не удалось получить данные о текущей погоде")
        
    return {
        "city": city_name,
        "temp_c": current.get("temperature"),
        "description": _get_weather_description(current.get("weathercode")),
    }

def _get_weather_description(code: int) -> str:
    codes = {
        0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
        61: "slight rain", 63: "moderate rain", 71: "slight snow", 95: "thunderstorm"
    }
    return codes.get(code, "unknown")