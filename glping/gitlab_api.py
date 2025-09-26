from datetime import datetime
from typing import Any, Dict, List, Optional

import gitlab


class GitLabAPI:
    """Класс для работы с GitLab API"""

    def __init__(self, url: str, token: str):
        """Инициализация подключения к GitLab"""
        self.gl = gitlab.Gitlab(url, private_token=token)
        self.gl.auth()

    def get_projects(
        self, membership: bool = True, project_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Получить список проектов"""
        if project_id:
            project = self.gl.projects.get(project_id)
            return [project.asdict()]

        projects = self.gl.projects.list(membership=membership, get_all=True)
        return [project.asdict() for project in projects]

    def get_project_events(
        self, project_id: int, after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить события проекта"""
        project = self.gl.projects.get(project_id)

        params = {}
        if after:
            params["after"] = after

        events = project.events.list(get_all=True, **params)
        return [event.asdict() for event in events]

    def get_recent_events(
        self, project_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Получить последние события проекта"""
        project = self.gl.projects.get(project_id)
        events = project.events.list(per_page=limit, page=1)
        return [event.asdict() for event in events]

    def get_project_name(self, project_id: int) -> str:
        """Получить название проекта"""
        project = self.gl.projects.get(project_id)
        return project.name_with_namespace or project.name

    def test_connection(self) -> bool:
        """Проверить подключение к GitLab"""
        try:
            user = self.gl.user
            print(f"Подключено как: {user.name} ({user.username})")
            return True
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
