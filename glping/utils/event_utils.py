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
    }
    return status_emojis.get(status, "❓")


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

        if ref.startswith("refs/heads/"):
            branch = ref.replace("refs/heads/", "")
            if action == "removed":
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
        elif action_name == "approved":
            description = f"Merge Request одобрен {author_name}"
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
        elif action_name == "closed":
            description = f"Задача закрыта {author_name}"
        elif action_name == "reopened":
            description = f"Задача переоткрыта {author_name}"
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

    else:
        return f"{event_type} {action_name} от {author_name} {event_date}".strip()