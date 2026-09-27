from clients.weather import get_weather
from clients.rates import get_rate
from processing.preprocessing import apply_rules

def build_city_summary(city: str, currency: str = "USD") -> dict:
    """Собирает сводку по городу: погода и курс валюты."""
    weather_data = get_weather(city)
    rate_value = get_rate(currency)
    
    summary = {
        "city": weather_data["city"],
        "weather": {
            "temp_c": weather_data["temp_c"],
            "description": weather_data["description"],
        },
        "rates": {
            "currency": currency.upper(),
            "rate_to_rub": rate_value,
        }
    }
    
    return apply_rules(summary)