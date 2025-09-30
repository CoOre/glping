import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp


class AsyncGitLabAPI:
    """Асинхронный класс для работы с GitLab API"""

    def __init__(self, url: str, token: str):
        """Инициализация подключения к GitLab"""
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

    def get_event_description(self, event: Dict[str, Any]) -> str:
        """Получить описание события на русском языке"""
        event_type = event.get("target_type", "Неизвестно")
        action_name = event.get("action_name", "неизвестно")
        author_name = event.get("author", {}).get("name", "Неизвестный")
        push_data = event.get("push_data", {})

        # Обработка push событий
        if action_name in ["pushed", "pushed new", "pushed to"] and push_data:
            ref = push_data.get("ref", "")
            commit_count = push_data.get("commit_count", 0)
            action = push_data.get("action", "")

            if ref.startswith("refs/heads/"):
                branch = ref.replace("refs/heads/", "")
                if action == "removed":
                    return f"Ветка {branch} удалена {author_name}"
                elif commit_count > 0:
                    return f"Новые коммиты в ветку {branch} от {author_name} ({commit_count} коммитов)"
                else:
                    return f"Push в ветку {branch} от {author_name}"
            else:
                return f"Новые коммиты от {author_name}"

        if event_type == "MergeRequest":
            if action_name == "opened":
                return f"Новый Merge Request от {author_name}"
            elif action_name == "updated":
                return f"Merge Request обновлен {author_name}"
            elif action_name == "closed":
                return f"Merge Request закрыт {author_name}"
            elif action_name == "merged":
                return f"Merge Request смержен {author_name}"
            elif action_name == "approved":
                return f"Merge Request одобрен {author_name}"

        elif event_type == "Issue":
            if action_name == "opened":
                return f"Новая задача от {author_name}"
            elif action_name == "closed":
                return f"Задача закрыта {author_name}"
            elif action_name == "reopened":
                return f"Задача переоткрыта {author_name}"

        elif event_type == "Note":
            return f"Новый комментарий от {author_name}"

        elif event_type == "Commit":
            return f"Новый коммит от {author_name}"

        elif event_type == "Pipeline":
            status = event.get("data", {}).get("status", "неизвестно")
            status_map = {
                "success": "успешно",
                "failed": "с ошибкой",
                "running": "выполняется",
                "pending": "ожидает",
                "canceled": "отменен",
            }
            status_ru = status_map.get(status, status)
            return f"Pipeline {status_ru} от {author_name}"

        return f"{event_type} {action_name} от {author_name}"
