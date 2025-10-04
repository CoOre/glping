import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .async_gitlab_api import AsyncGitLabAPI
from .base_watcher import BaseWatcher
from .cache import Cache
from .config import Config
from .notifier import Notifier
from .utils.url_utils import get_event_url


class AsyncGitLabWatcher(BaseWatcher):
    """Асинхронный класс для отслеживания событий GitLab."""

    def __init__(self, config: Config):
        """Инициализация наблюдателя."""
        super().__init__(config)
        self.api = AsyncGitLabAPI(config.gitlab_url, config.gitlab_token)
        self.notifier = Notifier()
        self._semaphore = asyncio.Semaphore(10)  # Ограничение одновременных запросов

    async def check_projects(self, verbose: bool = False):
        """Проверить проекты на наличие новых событий с серверной фильтрацией по активности"""
        if verbose:
            print(f"[{datetime.now().isoformat()}] Проверка новых событий...")

        # Получаем дату последней проверки для фильтрации
        last_checked = self.cache.get_last_checked()
        
        # Если есть дата последней проверки, используем серверную фильтрацию
        if last_checked:
            if verbose:
                last_checked_dt = datetime.fromisoformat(
                    last_checked.replace("Z", "+00:00")
                ).strftime("%Y-%m-%d %H:%M:%S")
                print(f"🔍 Фильтрация проектов с активностью после: {last_checked_dt}")
            
            # Получаем только активные проекты с сервера
            projects = await self.api.get_projects(
                **self.config.get_project_filter(),
                fields=[
                    "id",
                    "name",
                    "name_with_namespace", 
                    "path_with_namespace",
                    "last_activity_at",
                ],
                last_activity_after=last_checked,
            )
            
            if verbose:
                print(f"📊 Найдено {len(projects)} активных проектов (серверная фильтрация)")
        else:
            # Первый запуск - получаем все проекты
            if verbose:
                print("🔍 Первый запуск, получаем все проекты")
            
            projects = await self.api.get_projects(
                **self.config.get_project_filter(),
                fields=[
                    "id",
                    "name",
                    "name_with_namespace",
                    "path_with_namespace", 
                    "last_activity_at",
                ],
            )
            
            if verbose:
                print(f"📊 Найдено {len(projects)} проектов для первоначальной проверки")

        # Обновляем кеш активности проектов и дополнительно фильтруем при необходимости
        filtered_projects = []
        for project in projects:
            project_id = project["id"]
            last_activity = project.get("last_activity_at")
            
            # Обновляем кеш активности
            if last_activity:
                await self.cache.set_project_activity_async(project_id, last_activity)
            
            # Дополнительная проверка на случай, если серверная фильтрация не сработала
            if last_checked and last_activity:
                try:
                    activity_dt = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
                    last_checked_dt = datetime.fromisoformat(last_checked.replace("Z", "+00:00"))
                    if activity_dt > last_checked_dt:
                        filtered_projects.append(project)
                except (ValueError, TypeError):
                    # Если проблемы с датами, включаем проект
                    filtered_projects.append(project)
            else:
                # Если нет даты последней проверки или активности, включаем проект
                filtered_projects.append(project)

        # Обновляем список проектов для проверки
        projects = filtered_projects
        
        if verbose and last_checked:
            print(f"✅ Отфильтровано {len(projects)} проектов для проверки событий")

        # Создаем задачи для параллельной проверки проектов
        tasks = []
        for project in projects:
            task = asyncio.create_task(self._check_project_events(project, verbose))
            tasks.append(task)

        # Ждем завершения всех задач
        await asyncio.gather(*tasks, return_exceptions=True)

        await self.cache.set_last_checked_async(datetime.now(timezone.utc).isoformat())

    async def _check_project_events(
        self, project: Dict[str, Any], verbose: bool = False
    ):
        """Проверить события конкретного проекта"""
        async with self._semaphore:  # Ограничиваем одновременные запросы
            project_id = project["id"]
            project_name = project.get(
                "name_with_namespace", project.get("name", f"Проект {project_id}")
            )

            if verbose:
                print(f"  Проверка проекта: {project_name}")

            last_event_id = self.cache.get_last_event_id(project_id)
            last_checked = self.cache.get_last_checked()

            try:
                if last_event_id is None:
                    # Всегда используем дату последней проверки как фильтр
                    events = await self.api.get_project_events(
                        project_id, after=last_checked
                    )
                    if verbose:
                        last_checked_dt = datetime.fromisoformat(
                            last_checked.replace("Z", "+00:00")
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        print(f"    Первый запуск, проверка событий с {last_checked_dt}")
                else:
                    events = await self.api.get_project_events(project_id)
                    if verbose:
                        print(
                            f"    Проверка всех событий (последний известный ID: {last_event_id})"
                        )

                # Фильтруем события по дате последней проверки
                last_checked_dt = datetime.fromisoformat(
                    last_checked.replace("Z", "+00:00")
                )
                filtered_events = []
                skipped_old_events = 0

                for event in events:
                    event_id = event.get("id")
                    created_at = event.get("created_at", "")

                    if created_at:
                        try:
                            event_dt = datetime.fromisoformat(
                                created_at.replace("Z", "+00:00")
                            )
                            if event_dt > last_checked_dt:
                                if event_id and (
                                    last_event_id is None or event_id > last_event_id
                                ):
                                    filtered_events.append(event)
                            else:
                                skipped_old_events += 1
                        except (ValueError, TypeError):
                            # Если не удалось распарсить дату, включаем событие
                            if event_id and (
                                last_event_id is None or event_id > last_event_id
                            ):
                                filtered_events.append(event)
                    else:
                        # Если нет даты, включаем событие
                        if event_id and (
                            last_event_id is None or event_id > last_event_id
                        ):
                            filtered_events.append(event)

                if verbose and skipped_old_events > 0:
                    print(
                        f"    Пропущено {skipped_old_events} старых событий (до последней проверки)"
                    )

                if filtered_events:
                    if verbose:
                        print(f"    Найдено {len(filtered_events)} новых событий")

                    # Обрабатываем события параллельно
                    tasks = []
                    for event in sorted(filtered_events, key=lambda x: x.get("id", 0)):
                        task = asyncio.create_task(
                            self._process_event_async(event, project_name, project_id)
                        )
                        tasks.append(task)

                    await asyncio.gather(*tasks, return_exceptions=True)

                    latest_event_id = max(
                        event.get("id", 0) for event in filtered_events
                    )
                    await self.cache.set_last_event_id_async(
                        project_id, latest_event_id
                    )
                else:
                    if verbose:
                        print(f"    Нет новых событий")

                # Проверяем pipeline события отдельно
                await self._check_pipeline_events(project, verbose, last_checked_dt)

            except Exception as e:
                print(f"Ошибка при проверке проекта {project_name}: {e}")

    async def _process_event_async(
        self, event: Dict[str, Any], project_name: str, project_id: int
    ):
        """Асинхронно обработать событие"""
        event_id = event.get("id")
        created_at = event.get("created_at", "")
        description = self.api.get_event_description(event)

        timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        console_message = f"[{timestamp}] ИНФО: [Проект: {project_name}] {description}"
        print(console_message)

        url = await self._get_event_url_async(event, project_id)

        # Получаем информацию об авторе для иконки
        author = event.get("author", {})
        author_avatar = author.get("avatar_url")

        # Определяем иконку: если есть аватар автора - используем его, иначе - логотип GitLab
        icon_url = (
            author_avatar
            if author_avatar
            else "https://gitlab.com/assets/favicon-72a2cad5025aa931d6ea56c3201d1f18e8951c71e3363e712a476bead75f0a83.png"
        )

        # Отправляем уведомление в отдельном потоке, чтобы не блокировать
        await asyncio.to_thread(
            self.notifier.send_notification,
            title=project_name,
            message=description,
            url=url,
            icon_url=icon_url,
        )

    async def _get_project_path_async(self, project_id: int) -> Optional[str]:
        """Асинхронно получить путь проекта по его ID"""
        # Проверяем кэш в памяти
        if project_id in self._project_paths_cache:
            return self._project_paths_cache[project_id]

        # Проверяем кэш в файле
        cached_path = self.cache.get_project_path(project_id)
        if cached_path:
            self._project_paths_cache[project_id] = cached_path
            return cached_path

        try:
            # Получаем данные проекта
            projects = await self.api.get_projects(project_id=project_id)
            if projects:
                project = projects[0]
                path_with_namespace = project.get("path_with_namespace")
                if path_with_namespace:
                    # Сохраняем в оба кэша
                    self._project_paths_cache[project_id] = path_with_namespace
                    await self.cache.set_project_path_async(
                        project_id, path_with_namespace
                    )
                    return path_with_namespace
        except Exception as e:
            print(f"Ошибка получения пути проекта {project_id}: {e}")

        return None

    async def _get_event_url_async(self, event: Dict[str, Any], project_id: int) -> str:
        """Асинхронно получить URL для события"""
        target_type = event.get("target_type")
        target_id = event.get("target_id")
        target_iid = event.get("target_iid")
        action_name = event.get("action_name")
        push_data = event.get("push_data", {})

        # Получаем путь проекта вместо ID
        project_path = await self._get_project_path_async(project_id)
        if not project_path:
            # Запасной вариант с ID если путь не найден
            project_path = str(project_id)

        # Обработка push событий
        if action_name in ["pushed", "pushed new", "pushed to"] and push_data:
            commit_from = push_data.get("commit_from")
            commit_to = push_data.get("commit_to")
            ref = push_data.get("ref")

            if commit_to:
                return f"{self.config.gitlab_url}/{project_path}/-/commit/{commit_to}"
            elif ref and ref.startswith("refs/heads/"):
                branch = ref.replace("refs/heads/", "")
                return f"{self.config.gitlab_url}/{project_path}/-/tree/{branch}"

        # Обработка стандартных событий
        if target_type == "MergeRequest":
            if target_iid:
                return f"{self.config.gitlab_url}/{project_path}/-/merge_requests/{target_iid}"
            elif target_id:
                return f"{self.config.gitlab_url}/{project_path}/-/merge_requests/{target_id}"
        elif target_type == "Issue":
            if target_iid:
                return f"{self.config.gitlab_url}/{project_path}/-/issues/{target_iid}"
            elif target_id:
                return f"{self.config.gitlab_url}/{project_path}/-/issues/{target_id}"
        elif target_type in ["Note", "DiffNote"] and target_id:
            # Получаем данные о комментируемом объекте
            # Сначала проверяем в note, потом в data (разные версии API)
            note_data = event.get("note", {})
            noteable_type = note_data.get("noteable_type") or event.get("data", {}).get("noteable_type")
            noteable_iid = note_data.get("noteable_iid") or event.get("data", {}).get("noteable_iid")

            # DiffNote и Note к MergeRequest
            if noteable_type == "MergeRequest" and noteable_iid:
                if target_type == "DiffNote":
                    # Для DiffNote используем discussion_id если есть
                    discussion_id = note_data.get("discussion_id")
                    if discussion_id:
                        return f"{self.config.gitlab_url}/{project_path}/-/merge_requests/{noteable_iid}#note_{target_id}"
                    else:
                        return f"{self.config.gitlab_url}/{project_path}/-/merge_requests/{noteable_iid}#note_{target_id}"
                else:
                    return f"{self.config.gitlab_url}/{project_path}/-/merge_requests/{noteable_iid}#note_{target_id}"
            elif noteable_type == "Issue" and noteable_iid:
                return f"{self.config.gitlab_url}/{project_path}/-/issues/{noteable_iid}#note_{target_id}"
            elif noteable_type == "Commit":
                # Для комментариев к коммиту нужен commit_id
                commit_id = note_data.get("commit_id")
                if commit_id:
                    return f"{self.config.gitlab_url}/{project_path}/-/commit/{commit_id}#note_{target_id}"
        elif target_type == "Commit" and target_id:
            return f"{self.config.gitlab_url}/{project_path}/-/commit/{target_id}"
        elif target_type == "Pipeline" and target_id:
            return f"{self.config.gitlab_url}/{project_path}/-/pipelines/{target_id}"

        return f"{self.config.gitlab_url}/{project_path}"

    async def run_once(self, verbose: bool = False):
        """Запустить однократную проверку"""
        async with self.api:
            if not await self.api.test_connection():
                return False

            print(
                f"[{datetime.now().isoformat()}] Запуск GitLab watcher (однократный запуск)..."
            )
            await self.check_projects(verbose)
            print(f"[{datetime.now().isoformat()}] Проверка завершена")
            return True

    async def run_daemon(self, verbose: bool = False):
        """Запустить в режиме демона"""
        async with self.api:
            if not await self.api.test_connection():
                return False

            print(
                f"[{datetime.now().isoformat()}] Запуск GitLab watcher (режим демона)..."
            )
            print(f"Интервал проверки: {self.config.check_interval} секунд")
            print("Нажмите Ctrl+C для остановки")

            try:
                while True:
                    await self.check_projects(verbose)
                    await asyncio.sleep(self.config.check_interval)
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().isoformat()}] Остановка GitLab watcher...")
                return True

    def reset_cache(self):
        """Сбросить кеш"""
        self.cache.reset()
        print("Кеш успешно сброшен")

    async def _check_pipeline_events(
        self, project: Dict[str, Any], verbose: bool = False, last_checked_dt: Optional[datetime] = None
    ):
        """Отдельная проверка pipeline событий"""
        from .utils.event_utils import pipeline_to_event, is_new_pipeline_event, save_pipeline_event_to_cache
        
        project_id = project["id"]
        project_name = project.get("name_with_namespace", project.get("name", f"Проект {project_id}"))
        
        try:
            # Получаем pipelines, обновленные после последней проверки
            updated_after = last_checked_dt.isoformat() if last_checked_dt else None
            pipelines = await self.api.get_project_pipelines(project_id, updated_after=updated_after)
            
            if verbose:
                print(f"    Найдено pipelines: {len(pipelines)}")
            
            if not pipelines:
                return
            
            # Фильтруем и обрабатываем pipelines
            new_pipeline_events = []
            for pipeline in pipelines:
                # Проверяем, что pipeline новый
                if is_new_pipeline_event(pipeline, project_id, self.cache):
                    # Конвертируем pipeline в событие
                    event = pipeline_to_event(pipeline, project)
                    
                    # Дополнительная фильтрация по дате
                    if last_checked_dt:
                        try:
                            pipeline_dt = datetime.fromisoformat(
                                pipeline["created_at"].replace("Z", "+00:00")
                            )
                            if pipeline_dt > last_checked_dt:
                                new_pipeline_events.append(event)
                        except (ValueError, TypeError):
                            # Если не удалось распарсить дату, включаем событие
                            new_pipeline_events.append(event)
                    else:
                        new_pipeline_events.append(event)
            
            if new_pipeline_events:
                if verbose:
                    print(f"    Найдено {len(new_pipeline_events)} новых pipeline событий")
                
                # Обрабатываем pipeline события
                tasks = []
                for event in sorted(new_pipeline_events, key=lambda x: x.get("created_at", "")):
                    task = asyncio.create_task(
                        self._process_event_async(event, project_name, project_id)
                    )
                    tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Сохраняем pipeline события в кеш
                for pipeline in pipelines:
                    save_pipeline_event_to_cache(pipeline, project_id, self.cache)
                
                if verbose:
                    print(f"    Pipeline события обработаны и сохранены в кеш")
            
        except Exception as e:
            if verbose:
                print(f"    Ошибка при проверке pipelines: {e}")
            else:
                print(f"Ошибка при проверке pipelines для проекта {project_name}: {e}")

    def test_notification(self):
        """Отправить тестовое уведомление"""
        self.notifier.test_notification()
