import os
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Класс для управления конфигурацией GitLab Ping"""

    def __init__(self):
        """Инициализация конфигурации из переменных окружения"""
        # Определяем директорию для хранения настроек и кеша в домашней директории пользователя
        self.glping_dir = os.path.expanduser("~/glping")
        
        # Создаем директорию, если она не существует
        os.makedirs(self.glping_dir, exist_ok=True)
        
        # Определяем пути к файлам
        default_cache_file = os.path.join(self.glping_dir, "cache.json")
        env_file = os.path.join(self.glping_dir, ".env")
        
        # Загружаем .env файл из домашней директории, если он существует
        if os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            # Если нет в домашней директории, пробуем загрузить из директории установки
            try:
                import glping
                install_dir = os.path.dirname(os.path.abspath(glping.__file__))
                install_env_path = os.path.join(install_dir, '..', '.env')
                if os.path.exists(install_env_path):
                    load_dotenv(install_env_path)
                    # Копируем .env в домашнюю директорию для будущего использования
                    import shutil
                    shutil.copy2(install_env_path, env_file)
                    print(f"Конфигурация скопирована в {env_file}")
                else:
                    # Если нет нигде, ищем в текущей директории
                    load_dotenv()
            except ImportError:
                # Если не можем импортировать glping, ищем в текущей директории
                load_dotenv()

        self.gitlab_url: str = os.getenv("GITLAB_URL", "https://gitlab.com")
        self.gitlab_token: str = os.getenv("GITLAB_TOKEN", "")
        self.check_interval: int = int(os.getenv("CHECK_INTERVAL", "60"))
        # Всегда используем полный путь к файлу кеша в домашней директории
        cache_file_name = os.getenv("CACHE_FILE", "cache.json")
        self.cache_file: str = os.path.join(self.glping_dir, cache_file_name)
        self.project_id: Optional[int] = None

        if not self.gitlab_token:
            raise ValueError("GITLAB_TOKEN обязателен")
        
        # Валидация конфигурации
        self._validate_config()
        
        # Выводим информацию о загруженных настройках
        print(f"📁 Конфигурация загружена из: {env_file if os.path.exists(env_file) else 'текущей директории'}")
        print(f"🔗 GitLab URL: {self.gitlab_url}")
        print(f"⏱️  Интервал проверки: {self.check_interval} секунд")
        print(f"💾 Файл кеша: {self.cache_file}")
        if self.project_id:
            print(f"🎯 Отслеживаемый проект ID: {self.project_id}")

    def set_project_id(self, project_id: Optional[int]):
        """Установить ID проекта для отслеживания"""
        self.project_id = project_id

    def _validate_config(self):
        """Валидация конфигурации"""
        # Проверка URL
        if not self.gitlab_url.startswith(('http://', 'https://')):
            raise ValueError("GITLAB_URL должен начинаться с http:// или https://")
        
        # Проверка токена
        if len(self.gitlab_token) < 10:
            raise ValueError("GITLAB_TOKEN слишком короткий, проверьте правильность токена")
        
        # Проверка интервала
        if self.check_interval < 1:
            raise ValueError("CHECK_INTERVAL должен быть положительным числом")
        if self.check_interval > 3600:
            print(f"⚠️  CHECK_INTERVAL={self.check_interval}с очень большой, рекомендуется не более 3600с (1 час)")
    
    def get_project_filter(self) -> dict:
        """Получить фильтр для проектов"""
        if self.project_id:
            return {"project_id": self.project_id}
        return {"membership": True}
