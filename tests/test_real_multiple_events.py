#!/usr/bin/env python3

import os
import sys
import time
import pytest

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.config import Config
from glping.gitlab_api import GitLabAPI
from glping.notifier import Notifier
from glping.watcher import GitLabWatcher


@pytest.mark.skipif(
    not os.getenv("GITLAB_TOKEN") or os.getenv("CI"),
    reason="Требуется GITLAB_TOKEN для реальных тестов, пропускается в CI"
)
def test_real_multiple_events():
    """Тест множественных реальных событий GitLab"""

    config = Config()
    api = GitLabAPI(config.gitlab_url, config.gitlab_token)
    watcher = GitLabWatcher(config)
    notifier = Notifier()

    print("🧪 Тест множественных реальных событий GitLab")
    print("=" * 60)
    print("📱 Будут показаны уведомления по всем последним событиям")
    print("🔗 Каждое уведомление будет иметь правильный URL")

    # Получаем проекты
    projects = api.get_projects()

    # Берем первые 3 проекта
    test_projects = projects[:3]

    notification_count = 0

    for project in test_projects:
        project_id = project["id"]
        project_name = project.get(
            "name_with_namespace", project.get("name", "Unknown")
        )

        print(f"\n📂 Обработка проекта: {project_name}")

        # Получаем последние события
        events = api.get_recent_events(project_id, limit=3)

        for event in events:
            # Пропускаем события без описания
            description = api.get_event_description(event)
            if "None" in description or "неизвестно" in description:
                continue

            # Генерируем URL
            url = watcher._get_event_url(event, project_id)

            # Отправляем уведомление
            notification_count += 1
            print(f"{notification_count}. Отправка: {description}")

            notifier.send_notification(
                title=f"🔔 {project_name}", message=description, url=url
            )

            # Небольшая задержка между уведомлениями
            time.sleep(1.5)

            # Ограничиваем количество уведомлений
            if notification_count >= 8:
                break

        if notification_count >= 8:
            break

    print("\n" + "=" * 60)
    print(f"✅ Тест завершен! Отправлено {notification_count} уведомлений")
    print("📱 Вы должны увидеть несколько отдельных уведомлений")
    print("🖱️ Попробуйте кликнуть на разные уведомления для проверки URL")


if __name__ == "__main__":
    test_real_multiple_events()
