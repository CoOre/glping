"""Базовый класс для синхронных и асинхронных Watcher'ов."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .config import Config
from .cache import Cache
from .utils.url_utils import get_event_url
from .utils.date_utils import parse_gitlab_date


class BaseWatcher(ABC):
    """Базовый класс для наблюдателей за событиями GitLab."""

    def __init__(self, config: Config):
        """
        Инициализация базового наблюдателя.

        Args:
            config: Конфигурация приложения
        """
        self.config = config
        self.cache = Cache(config.cache_file)
        self._project_paths = {}  # Кэш путей проектов в памяти

    def _get_project_path(self, project_id: int) -> str:
        """
        Получить путь проекта из кэша или API.

        Args:
            project_id: ID проекта

        Returns:
            Путь проекта в формате namespace/project
        """
        # Проверяем кэш в памяти
        if project_id in self._project_paths:
            return self._project_paths[project_id]

        # Проверяем кэш на диске
        cached_path = self.cache.get_project_path(project_id)
        if cached_path:
            self._project_paths[project_id] = cached_path
            return cached_path

        return ""

    def _cache_project_path(self, project_id: int, path: str):
        """
        Сохранить путь проекта в кэш.

        Args:
            project_id: ID проекта
            path: Путь проекта
        """
        self._project_paths[project_id] = path
        self.cache.save_project_path(project_id, path)

    def get_event_url(
        self, event: Dict[str, Any], project_id: int
    ) -> str:
        """
        Получить URL для события.

        Args:
            event: Данные события
            project_id: ID проекта

        Returns:
            URL события
        """
        project_path = self._get_project_path(project_id)
        return get_event_url(
            event,
            self.config.gitlab_url,
            project_path,
            project_id
        )

    def _is_new_event(self, event: Dict[str, Any], project_id: int) -> bool:
        """
        Проверить, является ли событие новым.

        Args:
            event: Данные события
            project_id: ID проекта

        Returns:
            True если событие новое, False если уже было обработано
        """
        event_id = event.get("id")
        if not event_id:
            return True

        # Проверяем кэш событий
        cached_events = self.cache.get_project_events(project_id)
        if cached_events and event_id in cached_events:
            return False

        return True

    def _save_event_to_cache(self, event: Dict[str, Any], project_id: int):
        """
        Сохранить событие в кэш.

        Args:
            event: Данные события
            project_id: ID проекта
        """
        event_id = event.get("id")
        if event_id:
            self.cache.save_project_event(project_id, event_id)

    def _filter_events_by_date(
        self, events: List[Dict[str, Any]], last_check: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Фильтровать события по дате последней проверки.

        Args:
            events: Список событий
            last_check: Дата последней проверки в ISO формате

        Returns:
            Отфильтрованный список событий
        """
        if not last_check:
            return events

        last_check_dt = parse_gitlab_date(last_check)
        if not last_check_dt:
            return events

        filtered = []
        for event in events:
            event_date = parse_gitlab_date(event.get("created_at", ""))
            if event_date and event_date > last_check_dt:
                filtered.append(event)

        return filtered

    @abstractmethod
    def run_once(self, verbose: bool = False):
        """
        Выполнить однократную проверку событий.

        Args:
            verbose: Выводить подробную информацию
        """
        pass

    @abstractmethod
    def run_daemon(self, interval: int, verbose: bool = False):
        """
        Запустить в режиме демона.

        Args:
            interval: Интервал проверки в секундах
            verbose: Выводить подробную информацию
        """
        pass