import time
import random
import logging
import requests
from requests.exceptions import Timeout, ConnectionError, HTTPError, RequestException, JSONDecodeError

logger = logging.getLogger(__name__)

class ExternalServiceError(Exception):
    """Ошибка внешнего сервиса после исчерпания попыток."""
    pass

def fetch_get(url: str, params: dict = None, timeout: tuple = (3, 10), max_retries: int = 3) -> dict:
    """
    Выполняет GET-запрос с timeout и retry.
    timeout=(3, 10): 3 сек на connect, 10 сек на read (Слайд 17).
    max_retries=3: 1 первичная попытка + 2 повтора.
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            
            # Обработка 429 Too Many Requests (Слайд 15, 24)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 2))
                logger.warning(f"Получен 429. Ожидание {retry_after} сек.")
                time.sleep(retry_after)
                continue
                
            # Обработка 5xx ошибок (Слайд 25: повторяем только временные сбои)
            if response.status_code >= 500:
                logger.warning(f"Получен код {response.status_code}. Попытка {attempt}/{max_retries}")
                if attempt == max_retries:
                    response.raise_for_status()
                # Exponential backoff + jitter (Слайд 25)
                delay = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                logger.warning(f"Retry {attempt}/{max_retries}, задержка {delay:.1f}s")
                time.sleep(delay)
                continue
                
            # Обработка штатных 404/422 до raise_for_status (Слайд 18, 31)
            if response.status_code in (404, 422):
                raise HTTPError(f"HTTP {response.status_code}", response=response)
                
            # Проверка остальных кодов состояния
            response.raise_for_status()
            
            # Валидация Content-Type и парсинг JSON (Слайд 28, 32)
            if "application/json" not in response.headers.get("Content-Type", ""):
                raise ValueError("Ответ не является JSON (неверный Content-Type)")
                
            return response.json()
            
        except (Timeout, ConnectionError) as e:
            logger.warning(f"Сетевая ошибка ({type(e).__name__}). Попытка {attempt}/{max_retries}")
            if attempt == max_retries:
                raise ExternalServiceError("Внешний сервис недоступен после повторных попыток") from e
            delay = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            time.sleep(delay)
            
        except HTTPError as e:
            if hasattr(e, 'response') and e.response.status_code in (404, 422):
                raise e  # Пробрасываем для специальной обработки (город/валюта не найдены)
            logger.error(f"HTTP ошибка: {e}")
            if attempt == max_retries:
                raise ExternalServiceError(f"Ошибка HTTP: {e}") from e
            # 4xx (кроме 429, 404, 422) не повторяем, так как запрос не исправится (Слайд 24)
            if 400 <= e.response.status_code < 500:
                raise ExternalServiceError(f"Ошибка клиента: {e.response.status_code}")
            delay = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            time.sleep(delay)
            
        except (ValueError, JSONDecodeError) as e:
            logger.error(f"Ошибка парсинга JSON или валидации: {e}")
            raise ExternalServiceError("Неверный формат ответа от сервиса") from e
            
        except RequestException as e:
            logger.error(f"Неизвестная ошибка запроса: {e}")
            if attempt == max_retries:
                raise ExternalServiceError("Внешний сервис недоступен после повторных попыток") from e
            delay = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
            time.sleep(delay)
            
    raise ExternalServiceError("Внешний сервис недоступен после повторных попыток")