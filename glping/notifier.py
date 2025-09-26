import platform
import subprocess
import uuid
import webbrowser
from typing import Optional


class Notifier:
    """Класс для отправки уведомлений"""

    def __init__(self):
        """Инициализация системы уведомлений"""
        self.system = platform.system()

    def send_notification(
        self,
        title: str,
        message: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
    ):
        """Отправить уведомление"""
        success = False

        # Пробуем разные методы в зависимости от ОС
        if self.system == "Darwin":  # macOS
            success = self._send_macos_notification(title, message, url, icon_url)
        elif self.system == "Linux":
            success = self._send_linux_notification(title, message, url, icon_url)
        elif self.system == "Windows":
            success = self._send_windows_notification(title, message, url, icon_url)

        if not success:
            print(f"Ошибка отправки уведомления")
            self._console_notification(title, message, url)
        else:
            print(f"✅ Уведомление отправлено: [{title}] {message}")

    def _send_macos_notification(
        self,
        title: str,
        message: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
    ) -> bool:
        """Отправить уведомление на macOS"""
        # Генерируем уникальный идентификатор для каждого уведомления
        notification_id = str(uuid.uuid4())

        # Метод 1: terminal-notifier (предпочтительный) - используем разные группы для стекирования
        try:
            cmd = [
                "terminal-notifier",
                "-title",
                title,
                "-message",
                message,
                "-sound",
                "default",
                # Используем уникальную группу для каждого уведомления чтобы избежать замены
                "-group",
                f"glping-{notification_id[:8]}",  # Уникальная группа для каждого уведомления
                "-activate",
                "com.apple.Terminal",  # Активировать терминал при клике
                "-timeout",
                "10",  # Увеличиваем время отображения
            ]

            # Добавляем уникальный идентификатор
            cmd.extend(["-subtitle", f"ID: {notification_id[:8]}"])

            # Добавляем иконку если указана
            if icon_url:
                cmd.extend(["-appIcon", icon_url])

            if url:
                cmd.extend(["-open", url])

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except FileNotFoundError:
            pass  # terminal-notifier не установлен
        except Exception as e:
            print(f"Ошибка terminal-notifier: {e}")

        # Метод 2: osascript (резервный) - всегда показывает отдельные уведомления
        try:
            # Экранируем кавычки в сообщении
            safe_title = title.replace('"', '\\"')
            safe_message = message.replace('"', '\\"')
            cmd = [
                "osascript",
                "-e",
                f'display notification "{safe_message}" with title "{safe_title}" subtitle "{notification_id[:8]}"',
            ]
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            print(f"Ошибка osascript: {e}")

        return False

    def _send_linux_notification(
        self,
        title: str,
        message: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
    ) -> bool:
        """Отправить уведомление на Linux"""
        try:
            # Генерируем уникальный идентификатор
            notification_id = str(uuid.uuid4())[:8]

            cmd = [
                "notify-send",
                title,
                message,
                "-a",
                "GitLab Ping",
                "-u",
                "normal",
                "-t",
                "10000",  # 10 секунд
                "-h",
                "string:x-canonical-private-synchronous:glping",
                "-h",
                f"string:desktop-entry:{notification_id}",
            ]

            # Добавляем иконку если указана
            if icon_url:
                cmd.extend(["-i", icon_url])

            if url:
                cmd.extend(["-h", f"string:x-dunst-stack-tag:{notification_id}"])

            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            print(f"Ошибка notify-send: {e}")
            return False

    def _send_windows_notification(
        self,
        title: str,
        message: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
    ) -> bool:
        """Отправить уведомление на Windows"""
        try:
            from win10toast import ToastNotifier

            toaster = ToastNotifier()

            # Добавляем уникальный ID чтобы избежать замены
            unique_title = f"{title} [{str(uuid.uuid4())[:8]}]"

            # Для Windows URL откроется при клике на уведомление через callback
            # Иконка в Windows может быть установлена через icon_path, но требует локальный файл
            if url:
                toaster.show_toast(
                    unique_title,
                    message,
                    duration=10,
                    callback_on_click=lambda: webbrowser.open(url),
                )
            else:
                toaster.show_toast(unique_title, message, duration=10)
            return True
        except Exception as e:
            print(f"Ошибка Windows уведомления: {e}")
            return False

    def _console_notification(
        self, title: str, message: str, url: Optional[str] = None
    ):
        """Консольное уведомление как запасной вариант"""
        print(f"\n🔔 [{title}] {message}")
        if url:
            print(f"🔗 Ссылка: {url}")
        print()

    def _open_url(self, url: str):
        """Открыть URL в браузере"""
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Не удалось открыть URL: {e}")

    def test_notification(self):
        """Отправить тестовое уведомление"""
        print("🧪 Тестирование системы уведомлений...")
        self.send_notification(
            title="Тест GitLab Ping",
            message="✅ Уведомления работают!",
            url="https://gitlab.com",
            icon_url="https://gitlab.com/assets/favicon-72a2cad5025aa931d6ea56c3201d1f18e8951c71e3363e712a476bead75f0a83.png",
        )
