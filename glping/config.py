import os
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Класс для управления конфигурацией GitLab Ping"""

    def __init__(self):
        """Инициализация конфигурации из переменных окружения"""
        load_dotenv()

        self.gitlab_url: str = os.getenv("GITLAB_URL", "https://gitlab.com")
        self.gitlab_token: str = os.getenv("GITLAB_TOKEN", "")
        self.check_interval: int = int(os.getenv("CHECK_INTERVAL", "60"))
        self.cache_file: str = os.getenv("CACHE_FILE", "cache.json")
        self.project_id: Optional[int] = None

        if not self.gitlab_token:
            raise ValueError("GITLAB_TOKEN обязателен")

    def set_project_id(self, project_id: Optional[int]):
        """Установить ID проекта для отслеживания"""
        self.project_id = project_id

    def get_project_filter(self) -> dict:
        """Получить фильтр для проектов"""
        if self.project_id:
            return {"project_id": self.project_id}
        return {"membership": True}
