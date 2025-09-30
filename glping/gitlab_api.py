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
        self, membership: bool = True, project_id: Optional[int] = None, last_activity_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить список проектов с опциональной фильтрацией по активности"""
        if project_id:
            project = self.gl.projects.get(project_id)
            return [project.asdict()]

        # Добавляем фильтрацию по дате последней активности если указана
        kwargs = {"membership": membership, "get_all": True}
        if last_activity_after:
            kwargs["last_activity_after"] = last_activity_after
            
        projects = self.gl.projects.list(**kwargs)
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

    def _format_event_date(self, event: Dict[str, Any]) -> str:
        """Форматирует дату события"""
        from datetime import datetime
        
        created_at = event.get("created_at", "")
        if created_at:
            try:
                # Преобразуем ISO дату в читаемый формат
                if created_at.endswith('Z'):
                    event_dt = datetime.fromisoformat(created_at[:-1] + '+00:00')
                else:
                    event_dt = datetime.fromisoformat(created_at)
                # Форматируем как ДД.ММ.ЧЧ:ММ
                return event_dt.strftime("%d.%m.%H:%M")
            except:
                pass
        return ""

    def get_event_description(self, event: Dict[str, Any]) -> str:
        """Получить описание события на русском языке"""
        event_type = event.get("target_type", "Неизвестно")
        action_name = event.get("action_name", "неизвестно")
        author_name = event.get("author", {}).get("name", "Неизвестный")
        push_data = event.get("push_data", {})
        
        # Получаем отформатированную дату
        event_date = self._format_event_date(event)

        # Обработка push событий
        if action_name in ["pushed", "pushed new", "pushed to"] and push_data:
            ref = push_data.get("ref", "")
            commit_count = push_data.get("commit_count", 0)
            action = push_data.get("action", "")

            if ref.startswith("refs/heads/"):
                branch = ref.replace("refs/heads/", "")
                if action == "removed":
                    description = f"Ветка {branch} удалена {author_name}"
                elif commit_count > 0:
                    description = f"Новые коммиты в ветку {branch} от {author_name} ({commit_count} коммитов)"
                else:
                    description = f"Push в ветку {branch} от {author_name}"
            else:
                description = f"Новые коммиты от {author_name}"
            
            return f"{description} {event_date}".strip()

        if event_type == "MergeRequest":
            if action_name == "opened":
                description = f"Новый Merge Request от {author_name}"
            elif action_name == "updated":
                description = f"Merge Request обновлен {author_name}"
            elif action_name == "closed":
                description = f"Merge Request закрыт {author_name}"
            elif action_name == "merged":
                description = f"Merge Request смержен {author_name}"
            elif action_name == "approved":
                description = f"Merge Request одобрен {author_name}"
            else:
                description = f"Merge Request {action_name} от {author_name}"
            
            return f"{description} {event_date}".strip()

        elif event_type == "Issue":
            if action_name == "opened":
                description = f"Новая задача от {author_name}"
            elif action_name == "closed":
                description = f"Задача закрыта {author_name}"
            elif action_name == "reopened":
                description = f"Задача переоткрыта {author_name}"
            else:
                description = f"Задача {action_name} от {author_name}"
            
            return f"{description} {event_date}".strip()

        elif event_type == "Note":
            # Получаем текст комментария
            note_body = event.get("note", {}).get("body", "")
            if note_body:
                # Обрезаем длинные комментарии
                if len(note_body) > 100:
                    note_body = note_body[:100] + "..."
                description = f"Новый комментарий от {author_name}:\n\"{note_body}\""
            else:
                description = f"Новый комментарий от {author_name}"
            
            return f"{description} {event_date}".strip()

        elif event_type == "Commit":
            description = f"Новый коммит от {author_name}"
            return f"{description} {event_date}".strip()

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
            description = f"Pipeline {status_ru} от {author_name}"
            return f"{description} {event_date}".strip()

        description = f"{event_type} {action_name} от {author_name}"
        return f"{description} {event_date}".strip()
