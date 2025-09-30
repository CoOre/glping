import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .cache import Cache
from .config import Config
from .gitlab_api import GitLabAPI
from .notifier import Notifier


class GitLabWatcher:
    """Основной класс для отслеживания событий GitLab"""

    def __init__(self, config: Config):
        """Инициализация наблюдателя"""
        self.config = config
        self.cache = Cache(config.cache_file)
        self.api = GitLabAPI(config.gitlab_url, config.gitlab_token)
        self.notifier = Notifier()
        self._project_paths_cache = {}  # Кэш путей проектов

    def check_projects(self, verbose: bool = False):
        """Проверить все проекты на наличие новых событий"""
        if verbose:
            print(f"[{datetime.now().isoformat()}] Проверка новых событий...")

        projects = self.api.get_projects(**self.config.get_project_filter())

        if verbose:
            print(f"Найдено {len(projects)} проектов для проверки")

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

        url = self._get_event_url(event, project_id, verbose)

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
            title=f"Событие GitLab - {project_name}",
            message=description,
            url=url,
            icon_url=icon_url,
        )

    def _get_project_path(self, project_id: int) -> Optional[str]:
        """Получить путь проекта по его ID"""
        # Проверяем кэш
        if project_id in self._project_paths_cache:
            return self._project_paths_cache[project_id]

        try:
            # Получаем данные проекта
            projects = self.api.get_projects(project_id=project_id)
            if projects:
                project = projects[0]
                path_with_namespace = project.get("path_with_namespace")
                if path_with_namespace:
                    # Сохраняем в кэш
                    self._project_paths_cache[project_id] = path_with_namespace
                    return path_with_namespace
        except Exception as e:
            print(f"Ошибка получения пути проекта {project_id}: {e}")

        return None

    def _get_event_url(
        self, event: Dict[str, Any], project_id: int, verbose: bool = False
    ) -> str:
        """Получить URL для события"""
        target_type = event.get("target_type")
        target_id = event.get("target_id")
        target_iid = event.get(
            "target_iid"
        )  # Используем публичный IID вместо внутреннего ID
        action_name = event.get("action_name")
        push_data = event.get("push_data", {})

        # Получаем путь проекта вместо ID
        project_path = self._get_project_path(project_id)
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
            else:
                # Если нет публичного IID, не генерируем URL для внутреннего ID
                return f"{self.config.gitlab_url}/{project_path}/-/merge_requests"
        elif target_type == "Issue":
            if target_iid:
                return f"{self.config.gitlab_url}/{project_path}/-/issues/{target_iid}"
            else:
                # Если нет публичного IID, не генерируем URL для внутреннего ID
                return f"{self.config.gitlab_url}/{project_path}/-/issues"
        elif target_type == "Note" and target_id:
            # Получаем данные о комментируемом объекте из поля note
            note_data = event.get("note", {})
            noteable_type = note_data.get("noteable_type")
            noteable_iid = note_data.get("noteable_iid")

            if noteable_type == "MergeRequest" and noteable_iid:
                return f"{self.config.gitlab_url}/{project_path}/-/merge_requests/{noteable_iid}#note_{target_id}"
            elif noteable_type == "Issue" and noteable_iid:
                return f"{self.config.gitlab_url}/{project_path}/-/issues/{noteable_iid}#note_{target_id}"
        elif target_type == "Commit" and target_id:
            return f"{self.config.gitlab_url}/{project_path}/-/commit/{target_id}"
        elif target_type == "Pipeline" and target_id:
            return f"{self.config.gitlab_url}/{project_path}/-/pipelines/{target_id}"

        return f"{self.config.gitlab_url}/{project_path}"

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

    def test_notification(self):
        """Отправить тестовое уведомление"""
        self.notifier.test_notification()
