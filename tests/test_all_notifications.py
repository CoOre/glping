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
        title="my-project",
        message="Новый Merge Request от Иван Иванов",
        url="https://gitlab.example.com/123/-/merge_requests/456",
    )
    time.sleep(2)

    # Тест 2: Новая задача
    print("\n2. Тест: Новая задача")
    notifier.send_notification(
        title="my-project",
        message="Новая задача от Петр Петров",
        url="https://gitlab.example.com/123/-/issues/789",
    )
    time.sleep(2)

    # Тест 3: Комментарий
    print("\n3. Тест: Новый комментарий")
    notifier.send_notification(
        title="my-project",
        message="Новый комментарий от Мария Сидорова:\n\"Пожалуйста, проверьте эти изменения\"",
        url="https://gitlab.example.com/123/-/merge_requests/456#note_101",
    )
    time.sleep(2)

    # Тест 4: Pipeline успешно
    print("\n4. Тест: Pipeline успешно")
    notifier.send_notification(
        title="my-project",
        message="Pipeline успешно от Алексей Кузнецов",
        url="https://gitlab.example.com/123/-/pipelines/202",
    )
    time.sleep(2)

    # Тест 5: Pipeline с ошибкой
    print("\n5. Тест: Pipeline с ошибкой")
    notifier.send_notification(
        title="my-project",
        message="Pipeline с ошибкой от Елена Смирнова",
        url="https://gitlab.example.com/123/-/pipelines/203",
    )
    time.sleep(2)

    # Тест 6: Новый коммит
    print("\n6. Тест: Новый коммит")
    notifier.send_notification(
        title="my-project",
        message="Новый коммит от Дмитрий Волков",
        url="https://gitlab.example.com/123/-/commit/abc123def456",
    )
    time.sleep(2)

    # Тест 7: Pipeline выполняется
    print("\n7. Тест: Pipeline выполняется")
    notifier.send_notification(
        title="my-project",
        message="Pipeline #204 выполняется от Система CI/CD для feature/test-branch",
        url="https://gitlab.example.com/123/-/pipelines/204",
    )
    time.sleep(2)

    # Тест 8: Pipeline ожидает
    print("\n8. Тест: Pipeline ожидает")
    notifier.send_notification(
        title="my-project",
        message="Pipeline #205 ожидает от Система CI/CD для develop",
        url="https://gitlab.example.com/123/-/pipelines/205",
    )
    time.sleep(2)

    # Тест 9: Pipeline отменен
    print("\n9. Тест: Pipeline отменен")
    notifier.send_notification(
        title="my-project",
        message="Pipeline #206 отменен от Система CI/CD для hotfix/urgent-fix",
        url="https://gitlab.example.com/123/-/pipelines/206",
    )
    time.sleep(2)

    # Тест 10: Pipeline с указанием ветки
    print("\n10. Тест: Pipeline с указанием ветки")
    notifier.send_notification(
        title="my-project",
        message="Pipeline #207 успешно от Иван Петров для feature/new-api",
        url="https://gitlab.example.com/123/-/pipelines/207",
    )

    print("\n" + "=" * 60)
    print("✅ Все тесты уведомлений завершены!")
    print("📱 Проверьте всплывающие уведомления на вашем устройстве")
    print("🔗 При клике на уведомление должна открываться соответствующая страница")
    print("🔄 Проверены все статусы Pipeline: успешно, с ошибкой, выполняется, ожидает, отменен")


if __name__ == "__main__":
    test_all_notification_types()
