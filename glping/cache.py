import asyncio
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import fcntl
import tempfile


class Cache:
    """Класс для управления кешем событий GitLab"""

    def __init__(self, cache_file: str = "cache.json"):
        """Инициализация кеша"""
        # Если путь относительный, делаем его абсолютным относительно домашней директории
        if not os.path.isabs(cache_file):
            glping_dir = os.path.expanduser("~/glping")
            os.makedirs(glping_dir, exist_ok=True)
            self.cache_file = os.path.join(glping_dir, cache_file)
        else:
            self.cache_file = cache_file
        self.data: Dict[str, Any] = self._load_cache()
        self._migrate_old_cache_files()
        
        # Выводим информацию о кеше
        print(f"📂 Файл кеша: {self.cache_file}")
        if os.path.exists(self.cache_file):
            last_checked = self.data.get("metadata", {}).get("last_checked")
            if last_checked:
                print(f"🕐 Последняя проверка: {last_checked}")
            projects_with_events = len(self.data.get("projects", {}))
            projects_with_activity = len(self.data.get("project_activity", {}))
            print(f"📊 Проектов с событиями: {projects_with_events}")
            print(f"📈 Проектов с активностью: {projects_with_activity}")
        else:
            print("📂 Файл кеша не найден, будет создан новый")

    def _load_cache(self) -> Dict[str, Any]:
        """Загрузка кеша из файла"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Проверяем, что это новый формат кеша
                    if "metadata" in data and "projects" in data:
                        # Если нет даты последней проверки, устанавливаем дату 24 часа назад
                        if data["metadata"].get("last_checked") is None:
                            day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
                            data["metadata"]["last_checked"] = day_ago.isoformat()
                        return data
                    else:
                        # Старый формат, конвертируем
                        converted_data = self._convert_old_format(data)
                        # Если в конвертированных данных нет даты последней проверки, устанавливаем дату 24 часа назад
                        if converted_data["metadata"].get("last_checked") is None:
                            day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
                            converted_data["metadata"]["last_checked"] = day_ago.isoformat()
                        return converted_data
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Ошибка при чтении кеша {self.cache_file}: {e}")
                print("🔄 Будет создан новый файл кеша")
        
        # Возвращаем структуру нового формата с датой 24 часа назад для первого запуска
        day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        return {
            "metadata": {
                "last_checked": day_ago.isoformat()
            },
            "projects": {},
            "project_activity": {}
        }

    def _convert_old_format(self, old_data: Dict[str, Any]) -> Dict[str, Any]:
        """Конвертация старого формата кеша в новый"""
        last_checked = old_data.get("last_checked")
        # Если нет даты последней проверки, устанавливаем дату 24 часа назад
        if last_checked is None:
            day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
            last_checked = day_ago.isoformat()
        
        return {
            "metadata": {
                "last_checked": last_checked
            },
            "projects": old_data.get("projects", {}),
            "project_activity": {}
        }

    def _migrate_old_cache_files(self):
        """Миграция данных из старых файлов в новый формат"""
        migrated = False
        glping_dir = os.path.expanduser("~/glping")

        # Миграция только если текущий кеш пустой и это файл в домашней директории
        if (not self.data.get("projects") and 
            not self.data.get("project_activity") and 
            self.cache_file.startswith(glping_dir)):
            
            # Миграция cache.json из домашней директории
            old_cache_file = os.path.join(glping_dir, "cache.json")
            if os.path.exists(old_cache_file):
                try:
                    with open(old_cache_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if "last_checked" in data:
                            self.data["metadata"]["last_checked"] = data["last_checked"]
                        if "projects" in data:
                            self.data["projects"] = data["projects"]
                            migrated = True
                            print(f"🔄 Миграция данных из {old_cache_file}")
                except (json.JSONDecodeError, IOError) as e:
                    print(f"⚠️  Ошибка при чтении {old_cache_file}: {e}")

            # Миграция project_activity_cache.json из домашней директории
            old_activity_file = os.path.join(glping_dir, "project_activity_cache.json")
            if os.path.exists(old_activity_file):
                try:
                    with open(old_activity_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.data["project_activity"] = {int(k): v for k, v in data.items()}
                        migrated = True
                        print(f"🔄 Миграция данных из {old_activity_file}")
                except (json.JSONDecodeError, IOError) as e:
                    print(f"⚠️  Ошибка при чтении {old_activity_file}: {e}")

        # Если были мигрированы данные, сохраняем новый формат
        if migrated:
            self._save_cache()
            print("✅ Данные успешно мигрированы в новый формат кеша")

    def _save_cache(self):
        """Сохранение кеша в файл с блокировкой для предотвращения состояний гонки"""
        try:
            # Атомарная запись через временный файл
            temp_file = None
            try:
                # Создаем временный файл в той же директории
                temp_fd, temp_file = tempfile.mkstemp(
                    prefix=f"glping_cache_{os.getpid()}_", 
                    dir=os.path.dirname(self.cache_file)
                )
                
                with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                    # Блокируем файл на время записи
                    fcntl.flock(f, fcntl.LOCK_EX)
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                    f.flush()  # Принудительно записываем на диск
                    os.fsync(f.fileno())  # Синхронизация с файловой системой
                
                # Атомарно перемещаем временный файл на место основного
                os.replace(temp_file, self.cache_file)
                temp_file = None  # Файл уже перемещен
                
            except (ImportError, AttributeError):
                # Если fcntl недоступен (Windows), используем обычную запись
                with open(self.cache_file, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            finally:
                # Удаляем временный файл если остался
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except OSError:
                        pass
                        
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
        day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        self.data = {
            "metadata": {
                "last_checked": day_ago.isoformat()
            },
            "projects": {},
            "project_activity": {}
        }
        self._save_cache()

    def is_empty(self) -> bool:
        """Проверить, пуст ли кеш"""
        return not self.data["projects"]

    

    def get_project_path(self, project_id: int) -> Optional[str]:
        """Получить путь проекта из кеша"""
        project_paths = self.data.get("project_paths", {})
        return project_paths.get(str(project_id))

    def save_project_path(self, project_id: int, path: str):
        """Сохранить путь проекта в кеш"""
        if "project_paths" not in self.data:
            self.data["project_paths"] = {}
        self.data["project_paths"][str(project_id)] = path
        self._save_cache()

    def save_project_event(self, project_id: int, event_id: Any):
        """Сохранить событие проекта в кеш"""
        if "projects" not in self.data:
            self.data["projects"] = {}

        project_id_str = str(project_id)
        if project_id_str not in self.data["projects"]:
            self.data["projects"][project_id_str] = {"events": []}

        events = self.data["projects"][project_id_str]["events"]
        if event_id not in events:
            events.append(event_id)
            # Ограничиваем количество сохраняемых событий
            if len(events) > 100:
                events[:] = events[-100:]
            self._save_cache()

    def get_project_events(self, project_id: int) -> Optional[List]:
        """Получить список событий проекта из кеша"""
        projects = self.data.get("projects", {})
        project_data = projects.get(str(project_id), {})
        return project_data.get("events", [])

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
        """Получить дату установки (устаревший метод, использует last_checked)"""
        return self.data["metadata"]["last_checked"]

    def reset_installation_date(self):
        """Сбросить дату установки (устаревший метод, использует last_checked)"""
        day_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        self.data["metadata"]["last_checked"] = day_ago.isoformat()
        print("Дата последней проверки сброшена на 24 часа назад")
