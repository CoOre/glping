#!/usr/bin/env python3

import os
import platform
import subprocess
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_macos_notification():
    """Тестирование различных методов уведомлений на macOS"""

    print(f"Тестирование уведомлений на {platform.system()}")
    print("=" * 50)

    # Метод 1: osascript (нативный macOS)
    print("\n1. Тестирование osascript:")
    try:
        cmd = [
            "osascript",
            "-e",
            'display notification "Тестовое уведомление" with title "GitLab Ping"',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ osascript работает!")
    except Exception as e:
        print(f"❌ osascript ошибка: {e}")

    # Метод 2: terminal-notifier (если установлен)
    print("\n2. Тестирование terminal-notifier:")
    try:
        cmd = [
            "terminal-notifier",
            "-title",
            "GitLab Ping",
            "-message",
            "Тестовое уведомление",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ terminal-notifier работает!")
        else:
            print("❌ terminal-notifier не установлен или не работает")
    except FileNotFoundError:
        print("❌ terminal-notifier не установлен")
    except Exception as e:
        print(f"❌ terminal-notifier ошибка: {e}")

    # Метод 3: Проверка прав доступа
    print("\n3. Проверка прав доступа к уведомлениям:")
    try:
        # Проверим, есть ли у приложения права на отправку уведомлений
        cmd = [
            "osascript",
            "-e",
            'tell application "System Events" to display notification "Test"',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Права доступа к уведомлениям есть")
        else:
            print("❌ Проблема с правами доступа")
            print("   Проверьте: Системные настройки → Уведомления → Terminal")
    except Exception as e:
        print(f"❌ Ошибка проверки прав: {e}")

    # Метод 4: Тест plyer
    print("\n4. Тестирование plyer:")
    try:
        from plyer import notification

        notification.notify(
            title="Тест plyer", message="Тестовое уведомление через plyer", timeout=10
        )
        print("✅ plyer работает!")
    except Exception as e:
        print(f"❌ plyer ошибка: {e}")

    print("\n" + "=" * 50)
    print("Рекомендации:")
    print("1. Если osascript работает - используем его")
    print("2. Если terminal-notifier не установлен: brew install terminal-notifier")
    print("3. Проверьте права доступа в Системных настройках")


if __name__ == "__main__":
    test_macos_notification()
