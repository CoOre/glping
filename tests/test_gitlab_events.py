#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timezone

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.notifier import Notifier


def simulate_gitlab_events():
    """Симуляция реальных событий GitLab для тестирования уведомлений"""

    notifier = Notifier()

    print("🔄 Симуляция событий GitLab")
    print("=" * 50)

    # Симулируем различные события GitLab
    events = [
        {
            "type": "Merge Request",
            "action": "opened",
            "author": "Иван Иванов",
            "project": "frontend/my-awesome-app",
            "url": "https://msk-git-dev01.ntcees.ru/123/-/merge_requests/456",
        },
        {
            "type": "Issue",
            "action": "opened",
            "author": "Петр Петров",
            "project": "backend/api-service",
            "url": "https://msk-git-dev01.ntcees.ru/456/-/issues/789",
        },
        {
            "type": "Pipeline",
            "action": "success",
            "author": "Система CI/CD",
            "project": "devops/deployment",
            "url": "https://msk-git-dev01.ntcees.ru/789/-/pipelines/1234",
        },
        {
            "type": "Pipeline",
            "action": "failed",
            "author": "Система CI/CD",
            "project": "devops/deployment",
            "url": "https://msk-git-dev01.ntcees.ru/789/-/pipelines/1235",
        },
        {
            "type": "Note",
            "action": "commented",
            "author": "Мария Сидорова",
            "project": "frontend/my-awesome-app",
            "url": "https://msk-git-dev01.ntcees.ru/123/-/merge_requests/456#note_1001",
        },
        {
            "type": "Commit",
            "action": "pushed",
            "author": "Дмитрий Волков",
            "project": "backend/api-service",
            "url": "https://msk-git-dev01.ntcees.ru/456/-/commit/abc123def456",
        },
    ]

    for i, event in enumerate(events, 1):
        print(f"\n{i}. Симуляция: {event['type']} - {event['action']}")

        # Формируем сообщение в зависимости от типа события
        if event["type"] == "Merge Request":
            if event["action"] == "opened":
                message = f"Новый Merge Request от {event['author']}"
            elif event["action"] == "merged":
                message = f"Merge Request смержен {event['author']}"
            else:
                message = f"Merge Request {event['action']} {event['author']}"

        elif event["type"] == "Issue":
            if event["action"] == "opened":
                message = f"Новая задача от {event['author']}"
            elif event["action"] == "closed":
                message = f"Задача закрыта {event['author']}"
            else:
                message = f"Задача {event['action']} {event['author']}"

        elif event["type"] == "Pipeline":
            if event["action"] == "success":
                message = f"Pipeline успешно от {event['author']}"
            elif event["action"] == "failed":
                message = f"Pipeline с ошибкой от {event['author']}"
            else:
                message = f"Pipeline {event['action']} от {event['author']}"

        elif event["type"] == "Note":
            message = f"Новый комментарий от {event['author']}"

        elif event["type"] == "Commit":
            message = f"Новый коммит от {event['author']}"

        else:
            message = f"{event['type']} {event['action']} от {event['author']}"

        # Отправляем уведомление
        notifier.send_notification(
            title=f"Событие GitLab - {event['project']}",
            message=message,
            url=event["url"],
        )

        # Небольшая задержка между уведомлениями
        import time

        time.sleep(2)

    print("\n" + "=" * 50)
    print("✅ Симуляция событий GitLab завершена!")
    print("📱 Вы должны были увидеть 6 всплывающих уведомлений")
    print("🔗 Проверьте, что при клике на уведомления открываются правильные страницы")


if __name__ == "__main__":
    simulate_gitlab_events()
