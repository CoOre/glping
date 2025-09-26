#!/usr/bin/env python3

import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.notifier import Notifier


def test_notification_with_url():
    """Тест уведомления с URL - должно открываться только по клику"""
    print("🧪 Тестирование уведомления с URL...")
    print("📝 Уведомление должно появиться, но URL НЕ должен открываться автоматически")
    print("🖱️ URL должен открываться только при клике на уведомление")

    notifier = Notifier()
    notifier.send_notification(
        title="Тест с URL",
        message="Нажмите на это уведомление чтобы открыть GitLab",
        url="https://gitlab.com",
    )

    print("✅ Тест завершен. Проверьте уведомление и кликните на него.")


if __name__ == "__main__":
    test_notification_with_url()
