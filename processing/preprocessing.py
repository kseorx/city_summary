def apply_rules(summary: dict) -> dict:
    """
    Применяет бизнес-правила к собранным данным.
    """
    # Правило 1: Если температура < 0, добавляем флаг warm_clothes: true
    temp = summary.get("weather", {}).get("temp_c")
    summary["weather"]["warm_clothes"] = temp is not None and temp < 0
        
    # Правило 2: Если курс > 100, добавляем флаг expensive: true
    rate = summary.get("rates", {}).get("rate_to_rub")
    summary["rates"]["expensive"] = rate is not None and rate > 100
        
    return summary