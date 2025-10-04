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
            "type": "MergeRequest",
            "action": "opened",
            "author": "Иван Иванов",
            "project": "frontend/my-awesome-app",
            "url": "https://msk-git-dev01.ntcees.ru/123/-/merge_requests/456",
            "created_at": "2025-09-30T13:15:20Z",
        },
        {
            "type": "Issue",
            "action": "opened",
            "author": "Петр Петров",
            "project": "backend/api-service",
            "url": "https://msk-git-dev01.ntcees.ru/456/-/issues/789",
            "created_at": "2025-09-30T13:45:10Z",
        },
        {
            "type": "Pipeline",
            "action": "success",
            "author": "Система CI/CD",
            "project": "devops/deployment",
            "url": "https://msk-git-dev01.ntcees.ru/789/-/pipelines/1234",
            "created_at": "2025-09-30T14:00:00Z",
        },
        {
            "type": "Pipeline",
            "action": "failed",
            "author": "Система CI/CD",
            "project": "devops/deployment",
            "url": "https://msk-git-dev01.ntcees.ru/789/-/pipelines/1235",
            "created_at": "2025-09-30T14:30:45Z",
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
            "comment": "Пожалуйста, проверьте эти изменения",
            "created_at": "2025-09-30T14:20:30Z",
        },
        {
            "type": "Commit",
            "action": "pushed",
            "author": "Дмитрий Волков",
            "project": "backend/api-service",
            "url": "https://msk-git-dev01.ntcees.ru/456/-/commit/abc123def456",
            "created_at": "2025-09-30T15:10:15Z",
        },
        {
            "type": "Pipeline",
            "action": "running",
            "author": "Система CI/CD",
            "project": "frontend/react-app",
            "url": "https://msk-git-dev01.ntcees.ru/321/-/pipelines/888",
            "created_at": "2025-09-30T15:20:00Z",
        },
        {
            "type": "Pipeline",
            "action": "pending",
            "author": "Система CI/CD",
            "project": "backend/node-service",
            "url": "https://msk-git-dev01.ntcees.ru/654/-/pipelines/999",
            "created_at": "2025-09-30T15:25:00Z",
        },
        {
            "type": "Pipeline",
            "action": "canceled",
            "author": "Система CI/CD",
            "project": "devops/infrastructure",
            "url": "https://msk-git-dev01.ntcees.ru/987/-/pipelines/1111",
            "created_at": "2025-09-30T15:30:00Z",
        },
    ]

    def format_test_date(created_at):
        """Форматирует дату для теста"""
        from datetime import datetime
        if created_at:
            try:
                if created_at.endswith('Z'):
                    event_dt = datetime.fromisoformat(created_at[:-1] + '+00:00')
                else:
                    event_dt = datetime.fromisoformat(created_at)
                return event_dt.strftime("%d.%m.%H:%M")
            except:
                pass
        return ""

    for i, event in enumerate(events, 1):
        print(f"\n{i}. Симуляция: {event['type']} - {event['action']}")
        
        # Форматируем дату
        event_date = format_test_date(event.get("created_at", ""))

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
            elif event["action"] == "running":
                message = f"Pipeline выполняется от {event['author']}"
            elif event["action"] == "pending":
                message = f"Pipeline ожидает от {event['author']}"
            elif event["action"] == "canceled":
                message = f"Pipeline отменен от {event['author']}"
            else:
                message = f"Pipeline {event['action']} от {event['author']}"

        elif event["type"] == "Note":
            comment_text = event.get("comment", "Текст комментария")
            message = f"Новый комментарий от {event['author']}:\n\"{comment_text}\""

        elif event["type"] == "Commit":
            message = f"Новый коммит от {event['author']}"
        
        else:
            message = f"{event['type']} {event['action']} от {event['author']}"
        
        # Добавляем дату ко всем сообщениям
        if event_date:
            message = f"{message} {event_date}"

        else:
            message = f"{event['type']} {event['action']} от {event['author']}"

        # Отправляем уведомление
        notifier.send_notification(
            title=event['project'],
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
