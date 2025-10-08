import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .base_watcher import BaseWatcher
from .cache import Cache
from .config import Config
from .gitlab_api import GitLabAPI
from .notifier import Notifier
from .utils.url_utils import get_event_url


class GitLabWatcher(BaseWatcher):
    """Синхронный класс для отслеживания событий GitLab."""

    def __init__(self, config: Config):
        """Инициализация наблюдателя."""
        super().__init__(config)
        self.api = GitLabAPI(config.gitlab_url, config.gitlab_token)
        self.notifier = Notifier()
        # _project_paths уже инициализирован в базовом классе

    def check_projects(self, verbose: bool = False):
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
            projects = self.api.get_projects(
                **self.config.get_project_filter(),
                last_activity_after=last_checked,
            )
            
            if verbose:
                print(f"📊 Найдено {len(projects)} активных проектов (серверная фильтрация)")
        else:
            # Первый запуск - получаем все проекты
            if verbose:
                print("🔍 Первый запуск, получаем все проекты")
            
            projects = self.api.get_projects(**self.config.get_project_filter())
            
            if verbose:
                print(f"📊 Найдено {len(projects)} проектов для первоначальной проверки")

        # Проверяем события для отфильтрованных проектов
        for project in projects:
            self._check_project_events(project, verbose)

        self.cache.set_last_checked(datetime.now(timezone.utc).isoformat())

    def _check_project_events(self, project: Dict[str, Any], verbose: bool = False):
        """Проверить события конкретного проекта"""
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
                # Для первого запуска проекта всегда используем дату последней проверки
                # Пробуем использовать after параметр с правильным форматом
                try:
                    # Правильно парсим ISO дату с учетом различных форматов
                    if last_checked.endswith('Z'):
                        last_checked_dt = datetime.fromisoformat(last_checked[:-1] + '+00:00')
                    else:
                        last_checked_dt = datetime.fromisoformat(last_checked)
                    
                    # Убеждаемся что дата в UTC
                    if last_checked_dt.tzinfo is None:
                        last_checked_dt = last_checked_dt.replace(tzinfo=timezone.utc)
                    
                    after_date = last_checked_dt.strftime("%Y-%m-%d")
                    events = self.api.get_project_events(project_id, after=after_date)
                    if verbose:
                        print(
                            f"    Первый запуск для проекта, проверка событий с {after_date}"
                        )
                        print(f"    Получено событий от API: {len(events)}")
                except Exception as e:
                    # Если не сработало, получаем все события
                    if verbose:
                        print(
                            f"    Ошибка с after параметром: {e}, получаем все события"
                        )
                    events = self.api.get_project_events(project_id)
                    if verbose:
                        print(f"    Получено событий от API (без after): {len(events)}")
            else:
                events = self.api.get_project_events(project_id)
                if verbose:
                    print(
                        f"    Проверка всех событий (последний известный ID: {last_event_id})"
                    )

            # Фильтруем события по дате последней проверки
            try:
                if last_checked.endswith('Z'):
                    last_checked_dt = datetime.fromisoformat(last_checked[:-1] + '+00:00')
                else:
                    last_checked_dt = datetime.fromisoformat(last_checked)
                
                if last_checked_dt.tzinfo is None:
                    last_checked_dt = last_checked_dt.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                # Если не удалось распарсить дату проверки, используем начало текущих суток
                last_checked_dt = datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
            
            filtered_events = []
            skipped_old_events = 0

            for event in events:
                event_id = event.get("id")
                created_at = event.get("created_at", "")

                # Сначала проверяем дату события
                event_dt = None
                if created_at:
                    try:
                        if created_at.endswith('Z'):
                            event_dt = datetime.fromisoformat(created_at[:-1] + '+00:00')
                        else:
                            event_dt = datetime.fromisoformat(created_at)
                        
                        if event_dt.tzinfo is None:
                            event_dt = event_dt.replace(tzinfo=timezone.utc)
                    except (ValueError, TypeError):
                        event_dt = None

                # Проверяем что событие новее даты последней проверки
                is_recent = event_dt is None or event_dt > last_checked_dt
                
                if is_recent:
                    # Для недавних событий проверяем ID
                    if event_id and (last_event_id is None or event_id > last_event_id):
                        filtered_events.append(event)
                else:
                    skipped_old_events += 1

            if verbose and skipped_old_events > 0:
                print(
                    f"    Пропущено {skipped_old_events} старых событий (до последней проверки)"
                )

            if filtered_events:
                if verbose:
                    print(f"    Найдено {len(filtered_events)} новых событий")

                for event in sorted(filtered_events, key=lambda x: x.get("id", 0)):
                    self._process_event(event, project_name, project_id, verbose)

                latest_event_id = max(event.get("id", 0) for event in filtered_events)
                self.cache.set_last_event_id(project_id, latest_event_id)
            else:
                if verbose:
                    print(f"    Нет новых событий")

            # Проверяем CI/CD события отдельно
            self._check_pipeline_events(project, verbose, last_checked_dt)
            self._check_job_events(project, verbose, last_checked_dt)
            self._check_deployment_events(project, verbose, last_checked_dt)

        except Exception as e:
            print(f"Ошибка при проверке проекта {project_name}: {e}")

    def _process_event(
        self,
        event: Dict[str, Any],
        project_name: str,
        project_id: int,
        verbose: bool = False,
    ):
        """Обработать событие"""
        event_id = event.get("id")
        created_at = event.get("created_at", "")
        description = self.api.get_event_description(event)

        timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        console_message = f"[{timestamp}] ИНФО: [Проект: {project_name}] {description}"
        print(console_message)

        url = self.get_event_url(event, project_id)

        # Отладочная информация для URL
        target_type = event.get("target_type")
        target_iid = event.get("target_iid")
        target_id = event.get("target_id")
        print(
            f"    DEBUG: target_type={target_type}, target_iid={target_iid}, target_id={target_id}"
        )
        print(f"    DEBUG: URL={url}")

        # Получаем информацию об авторе для иконки
        author = event.get("author", {})
        author_avatar = author.get("avatar_url")

        # Определяем иконку: если есть аватар автора - используем его, иначе - логотип GitLab
        icon_url = (
            author_avatar
            if author_avatar
            else "https://gitlab.com/assets/favicon-72a2cad5025aa931d6ea56c3201d1f18e8951c71e3363e712a476bead75f0a83.png"
        )

        self.notifier.send_notification(
            title=project_name,
            message=description,
            url=url,
            icon_url=icon_url,
        )

    def _get_project_path(self, project_id: int) -> str:
        """Получить путь проекта по его ID."""
        # Сначала используем базовый метод
        path = super()._get_project_path(project_id)
        if path:
            return path

        try:
            # Получаем данные проекта из API
            projects = self.api.get_projects(project_id=project_id)
            if projects:
                project = projects[0]
                path_with_namespace = project.get("path_with_namespace")
                if path_with_namespace:
                    # Сохраняем в кэш
                    self._cache_project_path(project_id, path_with_namespace)
                    return path_with_namespace
        except Exception as e:
            print(f"Ошибка получения пути проекта {project_id}: {e}")

        return ""

    # Метод _get_event_url удален, используем get_event_url из базового класса

    def run_once(self, verbose: bool = False):
        """Запустить однократную проверку"""
        if not self.api.test_connection():
            return False

        print(
            f"[{datetime.now().isoformat()}] Запуск GitLab watcher (однократный запуск)..."
        )
        self.check_projects(verbose)
        print(f"[{datetime.now().isoformat()}] Проверка завершена")
        return True

    def run_daemon(self, verbose: bool = False):
        """Запустить в режиме демона"""
        if not self.api.test_connection():
            return False

        print(f"[{datetime.now().isoformat()}] Запуск GitLab watcher (режим демона)...")
        print(f"Интервал проверки: {self.config.check_interval} секунд")
        print("Нажмите Ctrl+C для остановки")

        try:
            while True:
                self.check_projects(verbose)
                time.sleep(self.config.check_interval)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().isoformat()}] Остановка GitLab watcher...")
            return True

    def reset_cache(self):
        """Сбросить кеш"""
        self.cache.reset()
        print("Кеш успешно сброшен")

    def _check_pipeline_events(
        self, project: Dict[str, Any], verbose: bool = False, last_checked_dt: Optional[datetime] = None
    ):
        """Отдельная проверка pipeline событий"""
        from .utils.event_utils import pipeline_to_event, is_new_pipeline_event, save_pipeline_event_to_cache
        
        project_id = project["id"]
        project_name = project.get("name_with_namespace", project.get("name", f"Проект {project_id}"))
        
        try:
            # Получаем pipelines, обновленные после последней проверки
            updated_after = last_checked_dt.isoformat() if last_checked_dt else None
            pipelines = self.api.get_project_pipelines(project_id, updated_after=updated_after)
            
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
                for event in sorted(new_pipeline_events, key=lambda x: x.get("created_at", "")):
                    self._process_event(event, project_name, project_id, verbose)
                
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

    def _check_job_events(
        self, project: Dict[str, Any], verbose: bool = False, last_checked_dt: Optional[datetime] = None
    ):
        """Отдельная проверка job событий"""
        from .utils.event_utils import job_to_event, is_new_job_event, save_job_event_to_cache
        
        project_id = project["id"]
        project_name = project.get("name_with_namespace", project.get("name", f"Проект {project_id}"))
        
        try:
            # Получаем jobs, обновленные после последней проверки
            updated_after = last_checked_dt.isoformat() if last_checked_dt else None
            jobs = self.api.get_project_jobs(project_id, updated_after=updated_after)
            
            if verbose:
                print(f"    Найдено jobs: {len(jobs)}")
            
            if not jobs:
                return
            
            # Фильтруем и обрабатываем jobs
            new_job_events = []
            for job in jobs:
                # Проверяем, что job новый или изменился статус
                if is_new_job_event(job, project_id, self.cache):
                    # Конвертируем job в событие
                    event = job_to_event(job, project)
                    
                    # Дополнительная фильтрация по дате
                    if last_checked_dt:
                        try:
                            job_dt = datetime.fromisoformat(
                                job["created_at"].replace("Z", "+00:00")
                            )
                            if job_dt > last_checked_dt:
                                new_job_events.append(event)
                        except (ValueError, TypeError):
                            # Если не удалось распарсить дату, включаем событие
                            new_job_events.append(event)
                    else:
                        new_job_events.append(event)
            
            if new_job_events:
                if verbose:
                    print(f"    Найдено {len(new_job_events)} новых job событий")
                
                # Обрабатываем job события
                for event in sorted(new_job_events, key=lambda x: x.get("created_at", "")):
                    self._process_event(event, project_name, project_id, verbose)
                
                # Сохраняем job события в кеш
                for job in jobs:
                    save_job_event_to_cache(job, project_id, self.cache)
                
                if verbose:
                    print(f"    Job события обработаны и сохранены в кеш")
            
        except Exception as e:
            if verbose:
                print(f"    Ошибка при проверке jobs: {e}")
            else:
                print(f"Ошибка при проверке jobs для проекта {project_name}: {e}")

    def _check_deployment_events(
        self, project: Dict[str, Any], verbose: bool = False, last_checked_dt: Optional[datetime] = None
    ):
        """Отдельная проверка deployment событий"""
        from .utils.event_utils import deployment_to_event, is_new_deployment_event, save_deployment_event_to_cache
        
        project_id = project["id"]
        project_name = project.get("name_with_namespace", project.get("name", f"Проект {project_id}"))
        
        try:
            # Получаем deployments, обновленные после последней проверки
            updated_after = last_checked_dt.isoformat() if last_checked_dt else None
            deployments = self.api.get_project_deployments(project_id, updated_after=updated_after)
            
            if verbose:
                print(f"    Найдено deployments: {len(deployments)}")
            
            if not deployments:
                return
            
            # Фильтруем и обрабатываем deployments
            new_deployment_events = []
            for deployment in deployments:
                # Проверяем, что deployment новый или изменился статус
                if is_new_deployment_event(deployment, project_id, self.cache):
                    # Конвертируем deployment в событие
                    event = deployment_to_event(deployment, project)
                    
                    # Дополнительная фильтрация по дате
                    if last_checked_dt:
                        try:
                            deployment_dt = datetime.fromisoformat(
                                deployment["created_at"].replace("Z", "+00:00")
                            )
                            if deployment_dt > last_checked_dt:
                                new_deployment_events.append(event)
                        except (ValueError, TypeError):
                            # Если не удалось распарсить дату, включаем событие
                            new_deployment_events.append(event)
                    else:
                        new_deployment_events.append(event)
            
            if new_deployment_events:
                if verbose:
                    print(f"    Найдено {len(new_deployment_events)} новых deployment событий")
                
                # Обрабатываем deployment события
                for event in sorted(new_deployment_events, key=lambda x: x.get("created_at", "")):
                    self._process_event(event, project_name, project_id, verbose)
                
                # Сохраняем deployment события в кеш
                for deployment in deployments:
                    save_deployment_event_to_cache(deployment, project_id, self.cache)
                
                if verbose:
                    print(f"    Deployment события обработаны и сохранены в кеш")
            
        except Exception as e:
            if verbose:
                print(f"    Ошибка при проверке deployments: {e}")
            else:
                print(f"Ошибка при проверке deployments для проекта {project_name}: {e}")

    def test_notification(self):
        """Отправить тестовое уведомление"""
        self.notifier.test_notification()
