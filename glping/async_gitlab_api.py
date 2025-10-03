import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from .base_gitlab_api import BaseGitLabAPI
from .config import Config


class AsyncGitLabAPI(BaseGitLabAPI):
    """Асинхронный класс для работы с GitLab API."""

    def __init__(self, url: str, token: str):
        """Инициализация подключения к GitLab."""
        # Создаем временную конфигурацию для обратной совместимости
        config = type('Config', (), {'gitlab_url': url, 'private_token': token})()
        super().__init__(config)
        self.url = url.rstrip("/")
        self.token = token
        self.session = None
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def __aenter__(self):
        """Асинхронный контекстный менеджер"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()

    async def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Выполнить запрос к API"""
        if not self.session:
            raise RuntimeError(
                "Session not initialized. Use async with or call init_session()"
            )

        url = f"{self.url}/api/v4/{endpoint}"

        try:
            async with self.session.request(method, url, params=params) as response:
                response.raise_for_status()

                # Обработка пагинации
                data = await response.json()
                if isinstance(data, list):
                    return data

                # Если ответ - объект с пагинацией
                if isinstance(data, dict) and "data" in data:
                    return data["data"]

                return [data] if data else []

        except aiohttp.ClientError as e:
            print(f"API request error: {e}")
            return []

    async def get_projects(
        self,
        membership: bool = True,
        project_id: Optional[int] = None,
        fields: Optional[List[str]] = None,
        last_activity_after: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Получить список проектов с оптимизацией полей и фильтрацией по активности"""
        if project_id:
            endpoint = f"projects/{project_id}"
            projects = await self._make_request("GET", endpoint)
            return projects if projects else []

        if fields is None:
            fields = [
                "id",
                "name",
                "name_with_namespace",
                "path_with_namespace",
                "last_activity_at",
            ]

        params = {"membership": str(membership).lower(), "per_page": "100", "page": "1"}

        if fields:
            params["fields"] = ",".join(fields)
            
        if last_activity_after:
            params["last_activity_after"] = last_activity_after

        projects = []
        page = 1

        while True:
            params["page"] = str(page)
            page_projects = await self._make_request("GET", "projects", params)

            if not page_projects:
                break

            projects.extend(page_projects)

            # Проверяем, есть ли следующая страница
            if len(page_projects) < 100:
                break

            page += 1

        return projects

    async def get_project_events(
        self,
        project_id: int,
        after: Optional[str] = None,
        fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Получить события проекта с оптимизацией"""
        if fields is None:
            fields = [
                "id",
                "created_at",
                "target_type",
                "target_id",
                "target_iid",
                "action_name",
                "author",
                "push_data",
                "data",
            ]

        params = {"per_page": "100", "page": "1"}

        if after:
            params["after"] = after

        if fields:
            params["fields"] = ",".join(fields)

        events = []
        page = 1

        while True:
            params["page"] = str(page)
            page_events = await self._make_request(
                "GET", f"projects/{project_id}/events", params
            )

            if not page_events:
                break

            events.extend(page_events)

            # Проверяем, есть ли следующая страница
            if len(page_events) < 100:
                break

            page += 1

        return events

    async def get_recent_events(
        self, project_id: int, limit: int = 10, fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Получить последние события проекта"""
        if fields is None:
            fields = [
                "id",
                "created_at",
                "target_type",
                "target_id",
                "target_iid",
                "action_name",
                "author",
                "push_data",
                "data",
            ]

        params = {"per_page": str(min(limit, 100)), "page": "1"}

        if fields:
            params["fields"] = ",".join(fields)

        return await self._make_request("GET", f"projects/{project_id}/events", params)

    async def get_project_name(self, project_id: int) -> str:
        """Получить название проекта"""
        projects = await self.get_projects(project_id=project_id)
        if projects:
            project = projects[0]
            return project.get("name_with_namespace") or project.get(
                "name", f"Проект {project_id}"
            )
        return f"Проект {project_id}"

    async def test_connection(self) -> bool:
        """Проверить подключение к GitLab"""
        try:
            user_data = await self._make_request("GET", "user")
            if user_data:
                user = user_data[0]
                print(
                    f"Подключено как: {user.get('name', 'Unknown')} ({user.get('username', 'unknown')})"
                )
                return True
            return False
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    # Методы форматирования дат и событий теперь наследуются от базового класса

    def get_project(self, project_id: int) -> Dict[str, Any]:
        """Получить информацию о проекте."""
        return asyncio.run(self._async_get_project(project_id))

    async def _async_get_project(self, project_id: int) -> Dict[str, Any]:
        """Асинхронный метод получения информации о проекте."""
        endpoint = f"projects/{project_id}"
        projects = await self._make_request("GET", endpoint)
        return projects[0] if projects else {}

    def get_project_merge_requests(
        self, project_id: int, state: str = "opened", updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить merge requests проекта."""
        return asyncio.run(self._async_get_project_merge_requests(project_id, state, updated_after))

    async def _async_get_project_merge_requests(
        self, project_id: int, state: str = "opened", updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Асинхронный метод получения merge requests."""
        params = {"state": state}
        if updated_after:
            params["updated_after"] = updated_after
        endpoint = f"projects/{project_id}/merge_requests"
        return await self._make_request("GET", endpoint, params)

    def get_project_issues(
        self, project_id: int, state: str = "opened", updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить задачи проекта."""
        return asyncio.run(self._async_get_project_issues(project_id, state, updated_after))

    async def _async_get_project_issues(
        self, project_id: int, state: str = "opened", updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Асинхронный метод получения задач."""
        params = {"state": state}
        if updated_after:
            params["updated_after"] = updated_after
        endpoint = f"projects/{project_id}/issues"
        return await self._make_request("GET", endpoint, params)

    def get_project_pipelines(
        self, project_id: int, updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить pipelines проекта."""
        return asyncio.run(self._async_get_project_pipelines(project_id, updated_after))

    async def _async_get_project_pipelines(
        self, project_id: int, updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Асинхронный метод получения pipelines."""
        params = {}
        if updated_after:
            params["updated_after"] = updated_after
        endpoint = f"projects/{project_id}/pipelines"
        return await self._make_request("GET", endpoint, params)
