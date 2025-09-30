import os
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
        self.is_cron = self._detect_cron_environment()
        
    def _detect_cron_environment(self) -> bool:
        """Определяет, запущен ли скрипт в crontab"""
        # Проверяем признаки crontab окружения
        cron_indicators = []
        
        # Отсутствие интерактивного терминала (сильный индикатор)
        if not os.isatty(0):
            cron_indicators.append('no_tty')
        
        # Специфичные для crontab переменные (очень сильные индикаторы)
        if any(key in os.environ for key in ['CRON_TZ', 'MAILTO']):
            cron_indicators.append('cron_vars')
        
        # Минимальный набор переменных окружения (только для Linux)
        if self.system == "Linux" and len(os.environ) < 15:
            cron_indicators.append('minimal_env')
        
        # Отсутствие DISPLAY переменной (только для Linux, где она обычно есть)
        if self.system == "Linux" and not os.environ.get('DISPLAY'):
            cron_indicators.append('no_display')
        
        # macOS специфические проверки
        if self.system == "Darwin":
            # В macOS cron обычно имеет очень ограниченный набор переменных
            if len(os.environ) < 8:
                cron_indicators.append('macos_minimal_env')
            # Отсутствие типичных GUI переменных в macOS
            gui_vars = ['TERM_PROGRAM', 'TERM_PROGRAM_VERSION', 'VSCODE_PID', 'ITERM_SESSION_ID']
            if not any(var in os.environ for var in gui_vars):
                cron_indicators.append('no_gui_vars')
        
        # Если есть хотя бы один сильный индикатор или 2 слабых, считаем что это cron
        strong_indicators = ['cron_vars']
        weak_indicators = ['no_tty', 'minimal_env', 'no_display', 'macos_minimal_env', 'no_gui_vars']
        
        has_strong = any(ind in strong_indicators for ind in cron_indicators)
        weak_count = sum(1 for ind in cron_indicators if ind in weak_indicators)
        
        return has_strong or weak_count >= 2

    def send_notification(
        self,
        title: str,
        message: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
    ):
        """Отправить уведомление"""
        # Логируем информацию об окружении для отладки
        if self.is_cron:
            print(f"🔄 Обнаружено crontab окружение, используем оптимизированные уведомления")
        
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
                "-timeout",
                "10",  # Увеличиваем время отображения
            ]

            # В crontab окружении не активируем терминал при клике
            if not self.is_cron:
                cmd.extend(["-activate", "com.apple.Terminal"])
            else:
                # В cron используем Finder вместо терминала
                cmd.extend(["-activate", "com.apple.Finder"])

            # Убираем ID для чистых уведомлений
            # cmd.extend(["-subtitle", f"ID: {notification_id[:8]}"])

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

            # В crontab окружении добавляем DISPLAY переменную если отсутствует
            if self.is_cron and not os.environ.get('DISPLAY'):
                # Пытаемся определить DISPLAY автоматически
                possible_displays = [':0', ':1', ':0.0', ':1.0']
                for display in possible_displays:
                    try:
                        test_cmd = ['xset', 'q']
                        env = os.environ.copy()
                        env['DISPLAY'] = display
                        subprocess.run(test_cmd, env=env, capture_output=True, timeout=1)
                        cmd.extend(['--', f'DISPLAY={display}'])
                        break
                    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
                        continue

            # Добавляем иконку если указана
            if icon_url:
                cmd.extend(["-i", icon_url])

            if url:
                cmd.extend(["-h", f"string:x-dunst-stack-tag:{notification_id}"])

            # В crontab окружении устанавливаем переменные окружения
            env = os.environ.copy()
            if self.is_cron:
                # Устанавливаем базовые переменные для GUI приложений
                if not env.get('DBUS_SESSION_BUS_ADDRESS'):
                    # Пытаемся найти DBUS сессию
                    try:
                        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                        for line in result.stdout.split('\n'):
                            if 'dbus-daemon' in line and '--session' in line:
                                parts = line.split()
                                for i, part in enumerate(parts):
                                    if part.startswith('DBUS_SESSION_BUS_ADDRESS='):
                                        env['DBUS_SESSION_BUS_ADDRESS'] = part.split('=', 1)[1]
                                        break
                    except Exception:
                        pass

            subprocess.run(cmd, check=True, env=env)
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
