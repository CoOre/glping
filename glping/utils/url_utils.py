"""Утилиты для генерации URL в GitLab."""

from typing import Any, Dict, Optional


def get_event_url(
    event: Dict[str, Any],
    gitlab_url: str,
    project_path: str,
    project_id: Optional[int] = None
) -> str:
    """
    Получить URL для события GitLab.

    Args:
        event: Словарь с данными события
        gitlab_url: Базовый URL GitLab инстанса
        project_path: Путь проекта (namespace/project)
        project_id: ID проекта (используется как fallback)

    Returns:
        URL события в GitLab
    """
    target_type = event.get("target_type")
    target_id = event.get("target_id")
    target_iid = event.get("target_iid")  # Используем публичный IID вместо внутреннего ID
    action_name = event.get("action_name")
    push_data = event.get("push_data", {})

    # Если нет пути проекта, используем ID как запасной вариант
    if not project_path and project_id:
        project_path = str(project_id)
    elif not project_path:
        project_path = "unknown"

    # Обработка push событий
    if action_name in ["pushed", "pushed new", "pushed to"] and push_data:
        commit_to = push_data.get("commit_to")
        ref = push_data.get("ref")

        if commit_to:
            return f"{gitlab_url}/{project_path}/-/commit/{commit_to}"
        elif ref and ref.startswith("refs/heads/"):
            branch = ref.replace("refs/heads/", "")
            return f"{gitlab_url}/{project_path}/-/tree/{branch}"

    # Обработка стандартных событий
    if target_type == "MergeRequest":
        if target_iid:
            return f"{gitlab_url}/{project_path}/-/merge_requests/{target_iid}"
        else:
            # Если нет публичного IID, не генерируем URL для внутреннего ID
            return f"{gitlab_url}/{project_path}/-/merge_requests"

    elif target_type == "Issue":
        if target_iid:
            return f"{gitlab_url}/{project_path}/-/issues/{target_iid}"
        else:
            return f"{gitlab_url}/{project_path}/-/issues"

    elif target_type in ["Note", "DiffNote"] and target_id:
        # Получаем данные о комментируемом объекте из поля note
        note_data = event.get("note", {})
        noteable_type = note_data.get("noteable_type")
        noteable_iid = note_data.get("noteable_iid")

        # DiffNote и Note к MergeRequest
        if noteable_type == "MergeRequest" and noteable_iid:
            return f"{gitlab_url}/{project_path}/-/merge_requests/{noteable_iid}#note_{target_id}"
        elif noteable_type == "Issue" and noteable_iid:
            return f"{gitlab_url}/{project_path}/-/issues/{noteable_iid}#note_{target_id}"
        elif noteable_type == "Commit":
            # Для комментариев к коммиту нужен commit_id
            commit_id = note_data.get("commit_id")
            if commit_id:
                return f"{gitlab_url}/{project_path}/-/commit/{commit_id}#note_{target_id}"

    elif target_type == "Commit" and target_id:
        return f"{gitlab_url}/{project_path}/-/commit/{target_id}"

    elif target_type == "Pipeline" and target_id:
        return f"{gitlab_url}/{project_path}/-/pipelines/{target_id}"

    return f"{gitlab_url}/{project_path}"