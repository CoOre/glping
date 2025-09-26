#!/usr/bin/env python3

import os
import sys
import time

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.notifier import Notifier


def test_all_notification_types():
    """Тестирование всех типов уведомлений GitLab"""

    notifier = Notifier()

    print("🧪 Тестирование всех типов уведомлений GitLab")
    print("=" * 60)

    # Тест 1: Новый Merge Request
    print("\n1. Тест: Новый Merge Request")
    notifier.send_notification(
        title="Событие GitLab - my-project",
        message="Новый Merge Request от Иван Иванов",
        url="https://gitlab.example.com/123/-/merge_requests/456",
    )
    time.sleep(2)

    # Тест 2: Новая задача
    print("\n2. Тест: Новая задача")
    notifier.send_notification(
        title="Событие GitLab - my-project",
        message="Новая задача от Петр Петров",
        url="https://gitlab.example.com/123/-/issues/789",
    )
    time.sleep(2)

    # Тест 3: Комментарий
    print("\n3. Тест: Новый комментарий")
    notifier.send_notification(
        title="Событие GitLab - my-project",
        message="Новый комментарий от Мария Сидорова",
        url="https://gitlab.example.com/123/-/merge_requests/456#note_101",
    )
    time.sleep(2)

    # Тест 4: Pipeline успешно
    print("\n4. Тест: Pipeline успешно")
    notifier.send_notification(
        title="Событие GitLab - my-project",
        message="Pipeline успешно от Алексей Кузнецов",
        url="https://gitlab.example.com/123/-/pipelines/202",
    )
    time.sleep(2)

    # Тест 5: Pipeline с ошибкой
    print("\n5. Тест: Pipeline с ошибкой")
    notifier.send_notification(
        title="Событие GitLab - my-project",
        message="Pipeline с ошибкой от Елена Смирнова",
        url="https://gitlab.example.com/123/-/pipelines/203",
    )
    time.sleep(2)

    # Тест 6: Новый коммит
    print("\n6. Тест: Новый коммит")
    notifier.send_notification(
        title="Событие GitLab - my-project",
        message="Новый коммит от Дмитрий Волков",
        url="https://gitlab.example.com/123/-/commit/abc123def456",
    )

    print("\n" + "=" * 60)
    print("✅ Все тесты уведомлений завершены!")
    print("📱 Проверьте всплывающие уведомления на вашем устройстве")
    print("🔗 При клике на уведомление должна открываться соответствующая страница")


if __name__ == "__main__":
    test_all_notification_types()
