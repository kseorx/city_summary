import time
from clients.http import fetch_get, ExternalServiceError
from requests.exceptions import HTTPError

class CurrencyNotFoundError(Exception):
    pass

_cache = {}
_CACHE_TTL = 300  # 5 минут

def get_rate(currency: str) -> float:
    currency = currency.upper()
    now = time.time()
    
    if currency in _cache:
        cached_value, timestamp = _cache[currency]
        if now - timestamp < _CACHE_TTL:
            return cached_value
            
    url = f"https://api.frankfurter.dev/v2/rate/{currency}/RUB"
    
    try:
        data = fetch_get(url)
    except HTTPError as e:
        if hasattr(e, 'response') and e.response.status_code in (404, 422):
            raise CurrencyNotFoundError(f"Код валюты '{currency}' не найден")
        raise ExternalServiceError(str(e))
    except ExternalServiceError as e:
        raise ExternalServiceError(f"Ошибка сервиса курсов: {e}")
        
    rate_value = float(data.get("rate", 0))
    if rate_value == 0:
        raise CurrencyNotFoundError(f"Курс для валюты '{currency}' не найден")
        
    _cache[currency] = (rate_value, now)
    return rate_value