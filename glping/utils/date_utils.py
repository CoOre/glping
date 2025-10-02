"""Утилиты для работы с датами."""

from datetime import datetime
from typing import Optional


def parse_gitlab_date(date_string: str) -> Optional[datetime]:
    """
    Парсит дату в формате GitLab (ISO 8601).

    Args:
        date_string: Строка даты из GitLab API

    Returns:
        datetime объект или None при ошибке
    """
    if not date_string:
        return None

    try:
        # Обработка различных форматов ISO даты
        if date_string.endswith('Z'):
            return datetime.fromisoformat(date_string[:-1] + '+00:00')
        else:
            return datetime.fromisoformat(date_string)
    except (ValueError, AttributeError):
        return None


def format_event_date(date_string: str) -> str:
    """
    Форматирует дату события для отображения.

    Args:
        date_string: Строка даты из GitLab API

    Returns:
        Отформатированная дата в формате ДД.ММ.ЧЧ:ММ или пустая строка
    """
    date_obj = parse_gitlab_date(date_string)
    if date_obj:
        return date_obj.strftime("%d.%m.%H:%M")
    return ""