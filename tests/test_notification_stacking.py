#!/usr/bin/env python3

import os
import sys
import time

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.notifier import Notifier


def test_notification_stacking():
    """Тест стекирования уведомлений на macOS"""

    notifier = Notifier()

    print("🧪 Тест стекирования уведомлений")
    print("=" * 50)
    print("📱 Должны появиться 3 отдельных уведомления одновременно")
    print("⏱️ Уведомления отправляются быстро друг за другом")
    print("🔗 Проверьте, что все уведомления отображаются в стеке")

    # Быстрая отправка нескольких уведомлений
    notifications = [
        {
            "title": "GitLab Ping - Merge Request",
            "message": "Новый MR: Добавить функцию X",
            "url": "https://gitlab.com/example/project/-/merge_requests/1",
        },
        {
            "title": "GitLab Ping - Issue",
            "message": "Новая задача: Исправить баг Y",
            "url": "https://gitlab.com/example/project/-/issues/2",
        },
        {
            "title": "GitLab Ping - Pipeline",
            "message": "Pipeline #123 успешно завершен",
            "url": "https://gitlab.com/example/project/-/pipelines/123",
        },
    ]

    for i, notification in enumerate(notifications, 1):
        print(f"\n{i}. Отправка уведомления: {notification['title']}")

        notifier.send_notification(
            title=notification["title"],
            message=notification["message"],
            url=notification["url"],
        )

        # Минимальная задержка чтобы избежать конфликтов
        time.sleep(0.5)

    print("\n" + "=" * 50)
    print("✅ Тест завершен!")
    print("📱 Вы должны увидеть 3 отдельных уведомления в стеке")
    print("🖱️ Попробуйте кликнуть на разные уведомления")
    print("🔗 Каждое уведомление должно открывать свою ссылку")


if __name__ == "__main__":
    test_notification_stacking()