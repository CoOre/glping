#!/usr/bin/env python3

import os
import sys
import time

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.notifier import Notifier


def test_multiple_notifications():
    """Тест множественных уведомлений"""

    notifier = Notifier()

    print("🧪 Тест множественных уведомлений")
    print("=" * 50)
    print("📱 Должны появиться 5 отдельных уведомлений")
    print("⏱️ Каждое уведомление будет появляться с задержкой 2 секунды")
    print("🔗 Проверьте, что все уведомления отображаются одновременно")

    # Тестовые уведомления
    notifications = [
        {
            "title": "GitLab Ping #1",
            "message": "Новый Merge Request от Иванова",
            "url": "https://msk-git-dev01.ntcees.ru/gridcore/eris-emulator/-/merge_requests/1",
        },
        {
            "title": "GitLab Ping #2",
            "message": "Задача закрыта Петровым",
            "url": "https://msk-git-dev01.ntcees.ru/gridcore/eris-emulator/-/issues/2",
        },
        {
            "title": "GitLab Ping #3",
            "message": "Pipeline успешно завершен",
            "url": "https://msk-git-dev01.ntcees.ru/gridcore/eris-emulator/-/pipelines/3",
        },
        {
            "title": "GitLab Ping #4",
            "message": "Новый комментарий от Сидорова",
            "url": "https://msk-git-dev01.ntcees.ru/gridcore/eris-emulator/-/merge_requests/1#note_4",
        },
        {
            "title": "GitLab Ping #5",
            "message": "Новые коммиты в ветке main",
            "url": "https://msk-git-dev01.ntcees.ru/gridcore/eris-emulator/-/commit/abc123",
        },
    ]

    for i, notification in enumerate(notifications, 1):
        print(f"\n{i}. Отправка уведомления: {notification['title']}")

        notifier.send_notification(
            title=notification["title"],
            message=notification["message"],
            url=notification["url"],
        )

        # Небольшая задержка между уведомлениями
        time.sleep(2)

    print("\n" + "=" * 50)
    print("✅ Тест завершен!")
    print("📱 Вы должны увидеть 5 отдельных уведомлений")
    print("🖱️ Попробуйте кликнуть на разные уведомления")


if __name__ == "__main__":
    test_multiple_notifications()
