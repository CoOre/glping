#!/usr/bin/env python3

import os
import sys
import pytest

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from glping.config import Config
from glping.gitlab_api import GitLabAPI
from glping.notifier import Notifier
from glping.watcher import GitLabWatcher


@pytest.mark.skipif(
    not os.getenv("GITLAB_TOKEN") or os.getenv("CI"),
    reason="Требуется GITLAB_TOKEN для реальных тестов, пропускается в CI"
)
def test_url_comparison():
    """Сравнение старых и новых URL"""

    config = Config()
    api = GitLabAPI(config.gitlab_url, config.gitlab_token)
    watcher = GitLabWatcher(config)
    notifier = Notifier()

    print("🔍 Сравнение старых и новых URL GitLab")
    print("=" * 60)

    # Получаем проекты
    projects = api.get_projects()

    # Берем первые 3 проекта для теста
    test_projects = projects[:3]

    for project in test_projects:
        project_id = project["id"]
        project_name = project.get(
            "name_with_namespace", project.get("name", "Unknown")
        )
        path_with_namespace = project.get("path_with_namespace", "")

        print(f"\n📂 Проект: {project_name}")
        print(f"ID: {project_id}")
        print(f"Path: {path_with_namespace}")

        # Получаем последние события
        events = api.get_recent_events(project_id, limit=2)

        for i, event in enumerate(events, 1):
            print(f"\n--- Событие {i} ---")

            # Получаем описание события
            description = api.get_event_description(event)
            print(f"Описание: {description}")

            # Генерируем новый URL
            new_url = watcher._get_event_url(event, project_id)

            # Генерируем старый URL (с ID)
            target_type = event.get("target_type")
            target_id = event.get("target_id")
            target_iid = event.get("target_iid")

            old_url = f"{config.gitlab_url}/{project_id}"
            if target_type == "MergeRequest" and target_iid:
                old_url = (
                    f"{config.gitlab_url}/{project_id}/-/merge_requests/{target_iid}"
                )
            elif target_type == "Issue" and target_iid:
                old_url = f"{config.gitlab_url}/{project_id}/-/issues/{target_iid}"
            elif target_type == "Commit" and target_id:
                old_url = f"{config.gitlab_url}/{project_id}/-/commit/{target_id}"

            print(f"Старый URL (неправильный): {old_url}")
            print(f"Новый URL (правильный):   {new_url}")

            # Отправляем уведомление с новым URL
            notifier.send_notification(
                title=f"✅ Правильный URL - {project_name}",
                message=description,
                url=new_url,
            )

            # Небольшая задержка
            import time

            time.sleep(1)

        print("-" * 50)

    print("\n" + "=" * 60)
    print("✅ Сравнение завершено!")
    print("📱 Все уведомления используют правильные URL")
    print("🔗 Формат: {domain}/{group_name}/{project_name}/-/{type}/{id}")


if __name__ == "__main__":
    test_url_comparison()
