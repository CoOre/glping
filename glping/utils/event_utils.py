"""Утилиты для обработки событий GitLab."""

from typing import Any, Dict
from .date_utils import format_event_date


def get_pipeline_status_emoji(status: str) -> str:
    """
    Получить emoji для статуса pipeline.

    Args:
        status: Статус pipeline

    Returns:
        Emoji соответствующий статусу
    """
    status_emojis = {
        "success": "✅",
        "failed": "❌",
        "running": "🏃",
        "pending": "⏳",
        "canceled": "🚫",
        "skipped": "⏭️",
    }
    return status_emojis.get(status, "❓")


def get_job_status_emoji(status: str) -> str:
    """
    Получить emoji для статуса job.

    Args:
        status: Статус job

    Returns:
        Emoji соответствующий статусу
    """
    status_emojis = {
        "success": "✅",
        "failed": "❌",
        "running": "🔄",
        "pending": "⏳",
        "canceled": "🚫",
        "skipped": "⏭️",
        "manual": "⏸️",
    }
    return status_emojis.get(status, "❓")


def get_deployment_status_emoji(status: str) -> str:
    """
    Получить emoji для статуса deployment.

    Args:
        status: Статус deployment

    Returns:
        Emoji соответствующий статусу
    """
    status_emojis = {
        "created": "📝",
        "running": "🚀",
        "success": "✅",
        "failed": "❌",
        "canceled": "🚫",
        "skipped": "⏭️",
    }
    return status_emojis.get(status, "❓")


def get_release_action_emoji(action: str) -> str:
    """
    Получить emoji для действий с релизами.

    Args:
        action: Действие с релизом

    Returns:
        Emoji соответствующий действию
    """
    action_emojis = {
        "created": "🎉",
        "updated": "📝",
        "deleted": "🗑️",
    }
    return action_emojis.get(action, "📦")


def get_wiki_action_emoji(action: str) -> str:
    """
    Получить emoji для действий с wiki страницами.

    Args:
        action: Действие с wiki страницей

    Returns:
        Emoji соответствующий действию
    """
    action_emojis = {
        "created": "📄",
        "updated": "✏️",
        "deleted": "🗑️",
    }
    return action_emojis.get(action, "📖")


def get_member_action_emoji(action: str) -> str:
    """
    Получить emoji для действий с участниками.

    Args:
        action: Действие с участником

    Returns:
        Emoji соответствующий действию
    """
    action_emojis = {
        "added": "➕",
        "removed": "➖",
        "updated": "🔄",
    }
    return action_emojis.get(action, "👥")


def get_event_description(event: Dict[str, Any]) -> str:
    """
    Получить описание события на русском языке.

    Args:
        event: Словарь с данными события из GitLab API

    Returns:
        Строка с описанием события
    """
    event_type = event.get("target_type", "Неизвестно")
    action_name = event.get("action_name", "неизвестно")
    author_name = event.get("author", {}).get("name", "Неизвестный")
    push_data = event.get("push_data", {})

    # Получаем отформатированную дату
    event_date = format_event_date(event.get("created_at", ""))

    # Обработка push событий
    if action_name in ["pushed", "pushed new", "pushed to"] and push_data:
        ref = push_data.get("ref", "")
        commit_count = push_data.get("commit_count", 0)
        action = push_data.get("action", "")
        commit_title = push_data.get("commit_title", "")

        # Обработка тегов
        if ref.startswith("refs/tags/"):
            tag_name = ref.replace("refs/tags/", "")
            if action == "created":
                description = f"Создан тег {tag_name} {author_name}"
            elif action == "removed":
                description = f"Удален тег {tag_name} {author_name}"
            else:
                description = f"Обновлен тег {tag_name} {author_name}"
            if commit_title:
                description += f": {commit_title}"
        # Обработка веток
        elif ref.startswith("refs/heads/"):
            branch = ref.replace("refs/heads/", "")
            if action == "created":
                description = f"Создана новая ветка {branch} {author_name}"
            elif action == "removed":
                description = f"Ветка {branch} удалена {author_name}"
            elif commit_count > 0:
                if commit_count == 1:
                    # Для одного коммита показываем полное сообщение
                    description = f"Push в {branch} от {author_name}"
                    if commit_title:
                        description += f": {commit_title}"
                else:
                    # Для нескольких коммитов показываем количество и первый
                    description = f"Push в {branch} от {author_name} ({commit_count} коммитов)"
                    if commit_title:
                        description += f": {commit_title}"
            else:
                description = f"Push в ветку {branch} от {author_name}"
        else:
            description = f"Новые коммиты от {author_name}"
            if commit_title:
                description += f": {commit_title}"

        return f"{description} {event_date}".strip()

    if event_type == "MergeRequest":
        # Получаем заголовок MR если доступен
        target_title = event.get("target_title", "")

        if action_name == "opened":
            description = f"Новый Merge Request от {author_name}"
        elif action_name == "updated":
            description = f"Merge Request обновлен {author_name}"
        elif action_name == "closed":
            description = f"Merge Request закрыт {author_name}"
        elif action_name == "merged":
            description = f"Merge Request смержен {author_name}"
        elif action_name == "reopened":
            description = f"Merge Request переоткрыт {author_name}"
        elif action_name == "approved":
            description = f"Merge Request одобрен {author_name}"
        elif action_name == "unapproved":
            description = f"Одобрение Merge Request отозвано {author_name}"
        elif action_name == "review_requested":
            description = f"Запрошено ревью Merge Request {author_name}"
        elif action_name == "ready":
            description = f"Merge Request переведен в статус Ready {author_name}"
        elif action_name == "draft":
            description = f"Merge Request переведен в статус Draft {author_name}"
        else:
            description = f"Merge Request {action_name} от {author_name}"

        # Добавляем заголовок MR если есть
        if target_title:
            description += f": {target_title}"

        return f"{description} {event_date}".strip()

    elif event_type == "Issue":
        # Получаем заголовок задачи если доступен
        target_title = event.get("target_title", "")

        if action_name == "opened":
            description = f"Новая задача от {author_name}"
        elif action_name == "updated":
            description = f"Задача обновлена {author_name}"
        elif action_name == "closed":
            description = f"Задача закрыта {author_name}"
        elif action_name == "reopened":
            description = f"Задача переоткрыта {author_name}"
        elif action_name == "moved":
            description = f"Задача перемещена {author_name}"
        else:
            description = f"Задача {action_name} от {author_name}"

        # Добавляем заголовок задачи если есть
        if target_title:
            description += f": {target_title}"

        return f"{description} {event_date}".strip()

    elif event_type in ["Note", "DiffNote"]:
        # Получаем текст комментария и информацию о том, к чему он относится
        note_data = event.get("note", {})
        note_body = note_data.get("body", "")
        noteable_type = note_data.get("noteable_type", "")
        noteable_iid = note_data.get("noteable_iid", "")

        # DiffNote - это комментарий к коду в MR
        if event_type == "DiffNote":
            # Для DiffNote всегда указываем что это комментарий к коду
            if noteable_type == "MergeRequest" and noteable_iid:
                context = f" к коду в MR #{noteable_iid}"
            else:
                context = " к коду"
            description = f"Комментарий{context} от {author_name}"
        else:
            # Обычный Note
            context = ""
            if noteable_type == "MergeRequest" and noteable_iid:
                context = f" к MR #{noteable_iid}"
            elif noteable_type == "Issue" and noteable_iid:
                context = f" к задаче #{noteable_iid}"
            elif noteable_type == "Commit":
                context = " к коммиту"
            description = f"Комментарий{context} от {author_name}"

        if note_body:
            # Увеличиваем лимит до 150 символов
            if len(note_body) > 150:
                note_body = note_body[:150] + "..."
            description += f": {note_body}"

        return f"{description} {event_date}".strip()

    elif event_type == "Commit":
        description = f"Новый коммит от {author_name}"
        return f"{description} {event_date}".strip()

    elif event_type == "Pipeline":
        # Получаем данные о pipeline
        pipeline_data = event.get("data", {})
        status = pipeline_data.get("status", "неизвестно")
        pipeline_id = event.get("target_id", "")
        ref = pipeline_data.get("ref", "")

        status_map = {
            "success": "успешно",
            "failed": "с ошибкой",
            "running": "выполняется",
            "pending": "ожидает",
            "canceled": "отменен",
            "skipped": "пропущен",
        }
        status_ru = status_map.get(status, status)

        # Формируем описание с номером pipeline
        if pipeline_id:
            description = f"Pipeline #{pipeline_id} {status_ru}"
        else:
            description = f"Pipeline {status_ru}"

        # Добавляем ветку если есть
        if ref:
            description += f" для {ref}"

        description += f" от {author_name}"

        return f"{description} {event_date}".strip()

    elif event_type == "Job":
        # Получаем данные о job
        job_data = event.get("data", {})
        status = job_data.get("status", "неизвестно")
        job_name = job_data.get("name", "")
        job_id = event.get("target_id", "")
        stage = job_data.get("stage", "")

        status_map = {
            "success": "успешно",
            "failed": "с ошибкой",
            "running": "выполняется",
            "pending": "ожидает",
            "canceled": "отменен",
            "skipped": "пропущен",
            "manual": "вручную",
        }
        status_ru = status_map.get(status, status)

        # Формируем описание с названием job
        if job_name:
            description = f"Job '{job_name}' {status_ru}"
        elif job_id:
            description = f"Job #{job_id} {status_ru}"
        else:
            description = f"Job {status_ru}"

        # Добавляем stage если есть
        if stage:
            description += f" (stage: {stage})"

        description += f" от {author_name}"

        return f"{description} {event_date}".strip()

    elif event_type == "Deployment":
        # Получаем данные о deployment
        deployment_data = event.get("data", {})
        status = deployment_data.get("status", "неизвестно")
        environment = deployment_data.get("environment", "")
        deployment_id = event.get("target_id", "")

        status_map = {
            "created": "создано",
            "running": "выполняется",
            "success": "успешно",
            "failed": "с ошибкой",
            "canceled": "отменено",
            "skipped": "пропущено",
        }
        status_ru = status_map.get(status, status)

        # Формируем описание
        if deployment_id:
            description = f"Развертывание #{deployment_id} {status_ru}"
        else:
            description = f"Развертывание {status_ru}"

        # Добавляем environment если есть
        if environment:
            description += f" в {environment}"

        description += f" от {author_name}"

        return f"{description} {event_date}".strip()

    elif event_type == "Release":
        # Получаем данные о релизе
        release_data = event.get("data", {})
        tag = release_data.get("tag", "")
        release_name = release_data.get("name", "")
        
        # Формируем описание
        if action_name == "created":
            description = f"Создан релиз от {author_name}"
        elif action_name == "updated":
            description = f"Релиз обновлен {author_name}"
        elif action_name == "deleted":
            description = f"Релиз удален {author_name}"
        else:
            description = f"Релиз {action_name} {author_name}"
        
        # Добавляем тег если есть
        if tag:
            description += f" ({tag})"
        elif release_name:
            description += f" ({release_name})"

        return f"{description} {event_date}".strip()

    elif event_type == "WikiPage":
        # Получаем данные о wiki странице
        wiki_data = event.get("data", {})
        page_title = wiki_data.get("title", "")
        page_slug = wiki_data.get("slug", "")
        
        # Формируем описание
        if action_name == "created":
            description = f"Создана wiki страница от {author_name}"
        elif action_name == "updated":
            description = f"Wiki страница обновлена {author_name}"
        elif action_name == "deleted":
            description = f"Wiki страница удалена {author_name}"
        else:
            description = f"Wiki страница {action_name} {author_name}"
        
        # Добавляем название страницы если есть
        if page_title:
            description += f": {page_title}"
        elif page_slug:
            description += f": {page_slug}"

        return f"{description} {event_date}".strip()

    elif event_type == "TagPush":
        # Получаем данные о теге
        push_data = event.get("push_data", {})
        ref = push_data.get("ref", "")
        action = push_data.get("action", "")
        
        if ref and ref.startswith("refs/tags/"):
            tag_name = ref.replace("refs/tags/", "")
            if action == "created":
                description = f"Создан тег {tag_name} {author_name}"
            elif action == "removed":
                description = f"Удален тег {tag_name} {author_name}"
            else:
                description = f"Тег {tag_name} {action} {author_name}"
        else:
            description = f"Операция с тегами от {author_name}"

        return f"{description} {event_date}".strip()

    elif event_type == "Member":
        # Получаем данные об участнике
        member_data = event.get("data", {})
        member_name = member_data.get("user_name", "")
        access_level = member_data.get("access_level", "")
        
        # Формируем описание
        if action_name == "added":
            description = f"Добавлен участник от {author_name}"
        elif action_name == "removed":
            description = f"Удален участник {author_name}"
        elif action_name == "updated":
            description = f"Изменены права участника {author_name}"
        else:
            description = f"Участник {action_name} {author_name}"
        
        # Добавляем имя участника если есть
        if member_name:
            description += f": {member_name}"
        
        # Добавляем уровень доступа если есть
        if access_level:
            description += f" ({access_level})"

        return f"{description} {event_date}".strip()

    else:
        return f"{event_type} {action_name} от {author_name} {event_date}".strip()


def pipeline_to_event(pipeline: Dict[str, Any], project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертировать pipeline в формат события для унифицированной обработки.
    
    Args:
        pipeline: Данные pipeline из GitLab API
        project: Данные проекта
        
    Returns:
        Словарь в формате события
    """
    # Создаем уникальный ID для pipeline события
    event_id = f"pipeline_{pipeline['id']}"
    
    # Определяем автора pipeline
    user = pipeline.get("user") or {}
    author_name = user.get("name", "Система CI/CD")
    author_username = user.get("username", "system")
    
    return {
        "id": event_id,
        "target_type": "Pipeline",
        "action_name": "updated",
        "created_at": pipeline["created_at"],
        "updated_at": pipeline.get("updated_at", pipeline["created_at"]),
        "author": {
            "name": author_name,
            "username": author_username,
            "avatar_url": user.get("avatar_url", "")
        },
        "target_id": pipeline["id"],
        "target_iid": pipeline["id"],
        "project_id": project["id"],
        "data": {
            "status": pipeline["status"],
            "ref": pipeline.get("ref", ""),
            "sha": pipeline.get("sha", ""),
            "source": pipeline.get("source", ""),
            "duration": pipeline.get("duration"),
            "web_url": pipeline.get("web_url", "")
        },
        # Дополнительные поля для совместимости
        "push_data": {},
        "note": {}
    }


def is_new_pipeline_event(pipeline: Dict[str, Any], project_id: int, cache) -> bool:
    """
    Проверить, является ли pipeline событие новым.
    
    Args:
        pipeline: Данные pipeline
        project_id: ID проекта
        cache: Объект кеша
        
    Returns:
        True если pipeline новый, False если уже обработан
    """
    pipeline_id = pipeline["id"]
    event_id = f"pipeline_{pipeline_id}"
    
    # Проверяем кеш событий
    cached_events = cache.get_project_events(project_id)
    if cached_events and event_id in cached_events:
        return False
    
    return True


def save_pipeline_event_to_cache(pipeline: Dict[str, Any], project_id: int, cache):
    """
    Сохранить pipeline событие в кеш.
    
    Args:
        pipeline: Данные pipeline
        project_id: ID проекта
        cache: Объект кеша
    """
    pipeline_id = pipeline["id"]
    event_id = f"pipeline_{pipeline_id}"
    
    # Проверяем наличие метода
    if hasattr(cache, 'save_project_event'):
        cache.save_project_event(project_id, event_id)
    else:
        # Альтернативный способ сохранения для совместимости
        cached_events = cache.get_project_events(project_id) or set()
        cached_events.add(event_id)
        if hasattr(cache, 'data'):
            if 'project_events' not in cache.data:
                cache.data['project_events'] = {}
            cache.data['project_events'][str(project_id)] = list(cached_events)


def job_to_event(job: Dict[str, Any], project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертировать job в формат события для унифицированной обработки.
    
    Args:
        job: Данные job из GitLab API
        project: Данные проекта
        
    Returns:
        Словарь в формате события
    """
    # Создаем уникальный ID для job события
    event_id = f"job_{job['id']}"
    
    # Определяем автора job
    user = job.get("user") or {}
    author_name = user.get("name", "Система CI/CD")
    author_username = user.get("username", "system")
    
    return {
        "id": event_id,
        "target_type": "Job",
        "action_name": "updated",
        "created_at": job["created_at"],
        "updated_at": job.get("updated_at", job["created_at"]),
        "author": {
            "name": author_name,
            "username": author_username,
            "avatar_url": user.get("avatar_url", "")
        },
        "target_id": job["id"],
        "target_iid": job["id"],
        "project_id": project["id"],
        "data": {
            "status": job["status"],
            "name": job.get("name", ""),
            "stage": job.get("stage", ""),
            "ref": job.get("ref", ""),
            "tag": job.get("tag", False),
            "duration": job.get("duration"),
            "web_url": job.get("web_url", "")
        },
        # Дополнительные поля для совместимости
        "push_data": {},
        "note": {}
    }


def deployment_to_event(deployment: Dict[str, Any], project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертировать deployment в формат события для унифицированной обработки.
    
    Args:
        deployment: Данные deployment из GitLab API
        project: Данные проекта
        
    Returns:
        Словарь в формате события
    """
    # Создаем уникальный ID для deployment события
    event_id = f"deployment_{deployment['id']}"
    
    # Определяем автора deployment
    user = deployment.get("user") or {}
    author_name = user.get("name", "Система CI/CD")
    author_username = user.get("username", "system")
    
    return {
        "id": event_id,
        "target_type": "Deployment",
        "action_name": "updated",
        "created_at": deployment["created_at"],
        "updated_at": deployment.get("updated_at", deployment["created_at"]),
        "author": {
            "name": author_name,
            "username": author_username,
            "avatar_url": user.get("avatar_url", "")
        },
        "target_id": deployment["id"],
        "target_iid": deployment["id"],
        "project_id": project["id"],
        "data": {
            "status": deployment["status"],
            "environment": deployment.get("environment", ""),
            "ref": deployment.get("ref", ""),
            "tag": deployment.get("tag", False),
            "deployable": deployment.get("deployable", {}),
            "created_at": deployment.get("created_at"),
            "updated_at": deployment.get("updated_at"),
        },
        # Дополнительные поля для совместимости
        "push_data": {},
        "note": {}
    }


def release_to_event(release: Dict[str, Any], project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертировать release в формат события для унифицированной обработки.
    
    Args:
        release: Данные release из GitLab API
        project: Данные проекта
        
    Returns:
        Словарь в формате события
    """
    # Создаем уникальный ID для release события
    event_id = f"release_{release['tag']}"
    
    # Определяем автора release
    user = release.get("author") or {}
    author_name = user.get("name", "Система")
    author_username = user.get("username", "system")
    
    return {
        "id": event_id,
        "target_type": "Release",
        "action_name": "created",  # По умолчанию при создании
        "created_at": release["created_at"],
        "updated_at": release.get("updated_at", release["created_at"]),
        "author": {
            "name": author_name,
            "username": author_username,
            "avatar_url": user.get("avatar_url", "")
        },
        "target_id": release.get("id", release["tag"]),
        "target_iid": release.get("id", release["tag"]),
        "project_id": project["id"],
        "data": {
            "tag": release["tag"],
            "name": release.get("name", ""),
            "description": release.get("description", ""),
            "released_at": release.get("released_at"),
            "web_url": release.get("web_url", "")
        },
        # Дополнительные поля для совместимости
        "push_data": {},
        "note": {}
    }


def wiki_page_to_event(wiki_page: Dict[str, Any], project: Dict[str, Any], action: str = "created") -> Dict[str, Any]:
    """
    Конвертировать wiki страницу в формат события для унифицированной обработки.
    
    Args:
        wiki_page: Данные wiki страницы из GitLab API
        project: Данные проекта
        action: Действие (created, updated, deleted)
        
    Returns:
        Словарь в формате события
    """
    # Создаем уникальный ID для wiki события
    event_id = f"wiki_{wiki_page['slug']}_{action}"
    
    # Определяем автора wiki страницы
    user = wiki_page.get("author") or {}
    author_name = user.get("name", "Система")
    author_username = user.get("username", "system")
    
    return {
        "id": event_id,
        "target_type": "WikiPage",
        "action_name": action,
        "created_at": wiki_page["created_at"],
        "updated_at": wiki_page.get("updated_at", wiki_page["created_at"]),
        "author": {
            "name": author_name,
            "username": author_username,
            "avatar_url": user.get("avatar_url", "")
        },
        "target_id": wiki_page.get("id", wiki_page["slug"]),
        "target_iid": wiki_page.get("id", wiki_page["slug"]),
        "project_id": project["id"],
        "data": {
            "title": wiki_page.get("title", ""),
            "slug": wiki_page["slug"],
            "format": wiki_page.get("format", ""),
            "web_url": wiki_page.get("web_url", "")
        },
        # Дополнительные поля для совместимости
        "push_data": {},
        "note": {}
    }


def tag_push_to_event(tag_push: Dict[str, Any], project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертировать tag push в формат события для унифицированной обработки.
    
    Args:
        tag_push: Данные tag push из GitLab API
        project: Данные проекта
        
    Returns:
        Словарь в формате события
    """
    # Получаем данные из push_data
    push_data = tag_push.get("push_data", {})
    ref = push_data.get("ref", "")
    action = push_data.get("action", "created")
    
    # Создаем уникальный ID для tag push события
    if ref and ref.startswith("refs/tags/"):
        tag_name = ref.replace("refs/tags/", "")
        event_id = f"tagpush_{tag_name}_{action}"
    else:
        event_id = f"tagpush_{tag_push.get('id', 'unknown')}_{action}"
    
    # Определяем автора
    author_name = tag_push.get("author", {}).get("name", "Система")
    author_username = tag_push.get("author", {}).get("username", "system")
    
    return {
        "id": event_id,
        "target_type": "TagPush",
        "action_name": action,
        "created_at": tag_push["created_at"],
        "updated_at": tag_push.get("updated_at", tag_push["created_at"]),
        "author": {
            "name": author_name,
            "username": author_username,
            "avatar_url": tag_push.get("author", {}).get("avatar_url", "")
        },
        "target_id": tag_push.get("id", ""),
        "target_iid": tag_push.get("id", ""),
        "project_id": project["id"],
        "data": {
            "ref": ref,
            "action": action,
            "commit_from": push_data.get("commit_from"),
            "commit_to": push_data.get("commit_to"),
        },
        # Дополнительные поля для совместимости
        "push_data": push_data,
        "note": {}
    }


def member_to_event(member: Dict[str, Any], project: Dict[str, Any], action: str = "added") -> Dict[str, Any]:
    """
    Конвертировать member в формат события для унифицированной обработки.
    
    Args:
        member: Данные member из GitLab API
        project: Данные проекта
        action: Действие (added, removed, updated)
        
    Returns:
        Словарь в формате события
    """
    # Создаем уникальный ID для member события
    user_id = member.get("id", "unknown")
    event_id = f"member_{user_id}_{action}"
    
    # Определяем автора (кто выполнил действие)
    # В реальном webhook это может быть другой пользователь
    author_name = member.get("created_by_name", "Система")
    author_username = member.get("created_by_username", "system")
    
    return {
        "id": event_id,
        "target_type": "Member",
        "action_name": action,
        "created_at": member.get("created_at", ""),
        "updated_at": member.get("updated_at", member.get("created_at", "")),
        "author": {
            "name": author_name,
            "username": author_username,
            "avatar_url": ""
        },
        "target_id": user_id,
        "target_iid": user_id,
        "project_id": project["id"],
        "data": {
            "user_name": member.get("name", ""),
            "username": member.get("username", ""),
            "email": member.get("email", ""),
            "access_level": member.get("access_level", ""),
            "expires_at": member.get("expires_at"),
        },
        # Дополнительные поля для совместимости
        "push_data": {},
        "note": {}
    }