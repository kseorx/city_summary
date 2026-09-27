import argparse
import sys
import logging
import json
import uuid
from processing.service import build_city_summary
from clients.http import ExternalServiceError
from clients.weather import CityNotFoundError
from clients.rates import CurrencyNotFoundError

# Бонус: logging с run_id
run_id = str(uuid.uuid4())[:8]
logging.basicConfig(level=logging.INFO, format=f"%(levelname)s [run_id:{run_id}]: %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Сводка по городу: погода и курс валюты")
    parser.add_argument("--city", type=str, required=True, help="Название города (например, Moscow)")
    parser.add_argument("--currency", type=str, default="USD", help="Код валюты ISO (по умолчанию USD)")
    parser.add_argument("--json", action="store_true", help="Вывод в формате JSON (дополнительный критерий)")
    
    args = parser.parse_args()
    
    city = args.city.strip()
    currency = args.currency.strip().upper()
    
    if not city:
        logger.error("Название города не может быть пустым")
        sys.exit(2)
        
    if not currency:
        logger.error("Код валюты не может быть пустым")
        sys.exit(2)

    try:
        summary = build_city_summary(city, currency)
        
        if args.json:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(f"Город: {summary['city']}")
            print(f"Погода: {summary['weather']['temp_c']}°C, {summary['weather']['description']}")
            print(f"Теплая одежда: {'да' if summary['weather']['warm_clothes'] else 'нет'}")
            print(f"{summary['rates']['currency']} -> RUB: {summary['rates']['rate_to_rub']}")
            print(f"Дорогой курс: {'да' if summary['rates']['expensive'] else 'нет'}")
            
        sys.exit(0)
        
    except (CurrencyNotFoundError, CityNotFoundError) as e:
        logger.error(str(e))
        sys.exit(3)  # Код 3: город или код валюты не найден
    except ExternalServiceError as e:
        logger.error(f"Внешний сервис недоступен: {e}")
        sys.exit(4)  # Код 4: внешний сервис недоступен после retry
    except ValueError as e:
        logger.error(f"Ошибка аргументов: {e}")
        sys.exit(2)  # Код 2: ошибка аргументов
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        sys.exit(4)

if __name__ == "__main__":
    main()