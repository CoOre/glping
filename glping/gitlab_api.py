from datetime import datetime
from typing import Any, Dict, List, Optional

import gitlab
from .base_gitlab_api import BaseGitLabAPI
from .config import Config


class GitLabAPI(BaseGitLabAPI):
    """Синхронный класс для работы с GitLab API."""

    def __init__(self, url: str, token: str):
        """Инициализация подключения к GitLab."""
        # Создаем временную конфигурацию для обратной совместимости
        config = type('Config', (), {'gitlab_url': url, 'private_token': token})()
        super().__init__(config)
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
        self,
        project_id: int,
        after: Optional[str] = None,
        sort: str = "desc",
        action: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Получить события проекта."""
        project = self.gl.projects.get(project_id)

        params = {}
        if after:
            params["after"] = after
        if sort:
            params["sort"] = sort
        if action:
            params["action"] = action

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
        """Проверить подключение к GitLab."""
        try:
            user = self.gl.user
            print(f"Подключено как: {user.name} ({user.username})")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    def get_project(self, project_id: int) -> Dict[str, Any]:
        """Получить информацию о проекте."""
        project = self.gl.projects.get(project_id)
        return project.asdict()

    def get_project_merge_requests(
        self, project_id: int, state: str = "opened", updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить merge requests проекта."""
        project = self.gl.projects.get(project_id)
        params = {"state": state}
        if updated_after:
            params["updated_after"] = updated_after
        mrs = project.mergerequests.list(get_all=True, **params)
        return [mr.asdict() for mr in mrs]

    def get_project_issues(
        self, project_id: int, state: str = "opened", updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить задачи проекта."""
        project = self.gl.projects.get(project_id)
        params = {"state": state}
        if updated_after:
            params["updated_after"] = updated_after
        issues = project.issues.list(get_all=True, **params)
        return [issue.asdict() for issue in issues]

    def get_project_pipelines(
        self, project_id: int, updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить pipelines проекта."""
        project = self.gl.projects.get(project_id)
        params = {}
        if updated_after:
            params["updated_after"] = updated_after
        pipelines = project.pipelines.list(get_all=True, **params)
        return [pipeline.asdict() for pipeline in pipelines]

    def get_project_jobs(
        self, project_id: int, updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить jobs проекта."""
        project = self.gl.projects.get(project_id)
        params = {}
        if updated_after:
            params["updated_after"] = updated_after
        jobs = project.jobs.list(get_all=True, **params)
        return [job.asdict() for job in jobs]

    def get_project_deployments(
        self, project_id: int, updated_after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Получить deployments проекта."""
        project = self.gl.projects.get(project_id)
        params = {}
        if updated_after:
            params["updated_after"] = updated_after
        deployments = project.deployments.list(get_all=True, **params)
        return [deployment.asdict() for deployment in deployments]

    # Методы форматирования дат и событий теперь наследуются от базового класса
