import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class Cache:
    """Класс для управления кешем событий GitLab"""

    def __init__(self, cache_file: str = "glping_cache.json"):
        """Инициализация кеша"""
        self.cache_file = cache_file
        self.data: Dict[str, Any] = self._load_cache()
        self._migrate_old_cache_files()

    def _load_cache(self) -> Dict[str, Any]:
        """Загрузка кеша из файла"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Проверяем, что это новый формат кеша
                    if "metadata" in data and "projects" in data:
                        return data
                    else:
                        # Старый формат, конвертируем
                        return self._convert_old_format(data)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Возвращаем структуру нового формата
        return {
            "metadata": {
                "installation_date": datetime.now(timezone.utc).isoformat(),
                "last_checked": None
            },
            "projects": {},
            "project_activity": {}
        }

    def _convert_old_format(self, old_data: Dict[str, Any]) -> Dict[str, Any]:
        """Конвертация старого формата кеша в новый"""
        return {
            "metadata": {
                "installation_date": datetime.now(timezone.utc).isoformat(),
                "last_checked": old_data.get("last_checked")
            },
            "projects": old_data.get("projects", {}),
            "project_activity": {}
        }

    def _migrate_old_cache_files(self):
        """Миграция данных из старых файлов в новый формат"""
        migrated = False
        
        # Миграция installation_date.json
        if os.path.exists("installation_date.json"):
            try:
                with open("installation_date.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "installation_date" in data:
                        self.data["metadata"]["installation_date"] = data["installation_date"]
                        migrated = True
            except (json.JSONDecodeError, IOError):
                pass

        # Миграция cache.json
        if os.path.exists("cache.json"):
            try:
                with open("cache.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "last_checked" in data:
                        self.data["metadata"]["last_checked"] = data["last_checked"]
                    if "projects" in data:
                        self.data["projects"] = data["projects"]
                        migrated = True
            except (json.JSONDecodeError, IOError):
                pass

        # Миграция project_activity_cache.json
        if os.path.exists("project_activity_cache.json"):
            try:
                with open("project_activity_cache.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.data["project_activity"] = {int(k): v for k, v in data.items()}
                    migrated = True
            except (json.JSONDecodeError, IOError):
                pass

        # Если были мигрированы данные, сохраняем новый формат
        if migrated:
            self._save_cache()
            print("✅ Данные успешно мигрированы в новый формат кеша")

    def _save_cache(self):
        """Сохранение кеша в файл"""
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Предупреждение: Не удалось сохранить кеш: {e}")

    async def _save_cache_async(self):
        """Асинхронное сохранение кеша"""
        await asyncio.to_thread(self._save_cache)

    

    def get_last_event_id(self, project_id: int) -> Optional[int]:
        """Получить ID последнего события для проекта"""
        return self.data["projects"].get(str(project_id), {}).get("last_event_id")

    def set_last_event_id(self, project_id: int, event_id: int):
        """Установить ID последнего события для проекта"""
        if str(project_id) not in self.data["projects"]:
            self.data["projects"][str(project_id)] = {}
        self.data["projects"][str(project_id)]["last_event_id"] = event_id
        self._save_cache()

    async def set_last_event_id_async(self, project_id: int, event_id: int):
        """Асинхронно установить ID последнего события для проекта"""
        if str(project_id) not in self.data["projects"]:
            self.data["projects"][str(project_id)] = {}
        self.data["projects"][str(project_id)]["last_event_id"] = event_id
        await self._save_cache_async()

    def get_last_checked(self) -> Optional[str]:
        """Получить время последней проверки"""
        return self.data["metadata"].get("last_checked")

    def set_last_checked(self, timestamp: str):
        """Установить время последней проверки"""
        self.data["metadata"]["last_checked"] = timestamp
        self._save_cache()

    async def set_last_checked_async(self, timestamp: str):
        """Асинхронно установить время последней проверки"""
        self.data["metadata"]["last_checked"] = timestamp
        await self._save_cache_async()

    def reset(self):
        """Сбросить кеш"""
        self.data = {
            "metadata": {
                "installation_date": datetime.now(timezone.utc).isoformat(),
                "last_checked": None
            },
            "projects": {},
            "project_activity": {}
        }
        self._save_cache()

    def is_empty(self) -> bool:
        """Проверить, пуст ли кеш"""
        return not self.data["projects"] and self.data["metadata"]["last_checked"] is None

    

    def get_project_activity(self, project_id: int) -> Optional[str]:
        """Получить время последней активности проекта из кеша"""
        return self.data["project_activity"].get(project_id)

    def set_project_activity(self, project_id: int, activity_time: str):
        """Установить время последней активности проекта в кеш"""
        self.data["project_activity"][project_id] = activity_time
        self._save_cache()

    async def set_project_activity_async(self, project_id: int, activity_time: str):
        """Асинхронно установить время последней активности проекта в кеш"""
        self.data["project_activity"][project_id] = activity_time
        await self._save_cache_async()

    

    def get_installation_date(self) -> str:
        """Получить дату установки"""
        return self.data["metadata"]["installation_date"]

    def reset_installation_date(self):
        """Сбросить дату установки (для тестирования)"""
        self.data["metadata"]["installation_date"] = datetime.now(timezone.utc).isoformat()
        self._save_cache()
        print("Дата установки сброшена")
