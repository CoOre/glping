"""Базовый класс для работы с GitLab API."""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from .config import Config
from .utils.event_utils import get_event_description, get_pipeline_status_emoji
from .utils.date_utils import format_event_date


class BaseGitLabAPI(ABC):
    """Базовый класс для синхронных и асинхронных версий GitLab API."""

    def __init__(self, config: Config):
        """
        Инициализация базового API.

        Args:
            config: Конфигурация приложения
        """
        self.config = config
        self.gitlab_url = config.gitlab_url
        self.private_token = config.private_token
        self.headers = {"PRIVATE-TOKEN": self.private_token}

    def format_event_date(self, event: Dict[str, Any]) -> str:
        """
        Форматирует дату события.

        Args:
            event: Словарь с данными события

        Returns:
            Отформатированная дата
        """
        return format_event_date(event.get("created_at", ""))

    def get_event_description(self, event: Dict[str, Any]) -> str:
        """
        Получить описание события на русском языке.

        Args:
            event: Словарь с данными события

        Returns:
            Строка с описанием события
        """
        return get_event_description(event)

    def get_pipeline_status_emoji(self, status: str) -> str:
        """
        Получить emoji для статуса pipeline.

        Args:
            status: Статус pipeline

        Returns:
            Emoji соответствующий статусу
        """
        return get_pipeline_status_emoji(status)

    @abstractmethod
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Получить список проектов.

        Returns:
            Список проектов
        """
        pass

    @abstractmethod
    def get_project(self, project_id: int) -> Dict[str, Any]:
        """
        Получить информацию о проекте.

        Args:
            project_id: ID проекта

        Returns:
            Информация о проекте
        """
        pass

    @abstractmethod
    def get_project_events(
        self,
        project_id: int,
        after: Optional[str] = None,
        sort: str = "desc",
        action: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получить события проекта.

        Args:
            project_id: ID проекта
            after: Фильтр по дате (события после этой даты)
            sort: Направление сортировки ('asc' или 'desc')
            action: Фильтр по типу действия

        Returns:
            Список событий проекта
        """
        pass

    @abstractmethod
    def get_project_merge_requests(
        self, project_id: int, state: str = "opened", updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить merge requests проекта.

        Args:
            project_id: ID проекта
            state: Состояние MR ('opened', 'closed', 'merged', 'all')
            updated_after: Фильтр по дате обновления

        Returns:
            Список merge requests
        """
        pass

    @abstractmethod
    def get_project_issues(
        self, project_id: int, state: str = "opened", updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить задачи проекта.

        Args:
            project_id: ID проекта
            state: Состояние задачи ('opened', 'closed', 'all')
            updated_after: Фильтр по дате обновления

        Returns:
            Список задач
        """
        pass

    @abstractmethod
    def get_project_pipelines(
        self, project_id: int, updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить pipelines проекта.

        Args:
            project_id: ID проекта
            updated_after: Фильтр по дате обновления

        Returns:
            Список pipelines
        """
        pass

    def get_project_jobs(
        self, project_id: int, updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить jobs проекта.

        Args:
            project_id: ID проекта
            updated_after: Фильтр по дате обновления

        Returns:
            Список jobs
        """
        pass

    def get_project_deployments(
        self, project_id: int, updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить deployments проекта.

        Args:
            project_id: ID проекта
            updated_after: Фильтр по дате обновления

        Returns:
            Список deployments
        """
        pass