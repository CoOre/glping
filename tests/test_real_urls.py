#!/usr/bin/env python3

import os
import sys
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
def test_real_urls():
    """Тестирование реальных URL из событий GitLab"""

    config = Config()
    api = GitLabAPI(config.gitlab_url, config.gitlab_token)
    watcher = GitLabWatcher(config)
    notifier = Notifier()

    print("🔍 Тестирование реальных URL из GitLab")
    print("=" * 50)

    # Получаем проекты
    projects = api.get_projects()

    # Берем первые 3 проекта для теста
    test_projects = projects[:3]

    for project in test_projects:
        project_id = project["id"]
        project_name = project.get(
            "name_with_namespace", project.get("name", "Unknown")
        )

        print(f"\n📂 Тест проекта: {project_name}")

        # Получаем последние события
        events = api.get_recent_events(project_id, limit=3)

        for i, event in enumerate(events, 1):
            print(f"\n--- Событие {i} ---")

            # Получаем описание события
            description = api.get_event_description(event)
            print(f"Описание: {description}")

            # Генерируем URL
            url = watcher._get_event_url(event, project_id)
            print(f"Сгенерированный URL: {url}")

            # Проверяем, что URL не пустой и выглядит правильно
            if url and url != f"{config.gitlab_url}/{project_id}":
                print("✅ URL выглядит корректно")

                # Отправляем тестовое уведомление
                notifier.send_notification(
                    title=f"Тест URL - {project_name}", message=description, url=url
                )

                # Небольшая задержка
                import time

                time.sleep(1)
            else:
                print("❌ URL пустой или некорректный")

            print("-" * 30)

    print("\n" + "=" * 50)
    print("✅ Тестирование URL завершено!")
    print("📱 Проверьте уведомления и кликните на них для проверки ссылок")


if __name__ == "__main__":
    test_real_urls()
