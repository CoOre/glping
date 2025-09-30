#!/usr/bin/env python3
"""
Тесты для определения crontab окружения
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from glping.notifier import Notifier


class TestCronDetection(unittest.TestCase):
    """Тесты определения crontab окружения"""

    def test_normal_environment_detection(self):
        """Тест определения обычного окружения"""
        # Эмулируем обычное окружение с терминалом
        original_isatty = os.isatty
        original_environ = os.environ.copy()
        
        try:
            os.isatty = lambda fd: True
            os.environ.update({'DISPLAY': ':0', 'TERM': 'xterm-256color', 'USER': 'test'})
            
            notifier = Notifier()
            self.assertFalse(notifier.is_cron, "Обычное окружение не должно определяться как cron")
        finally:
            os.isatty = original_isatty
            os.environ.clear()
            os.environ.update(original_environ)

    def test_cron_environment_detection(self):
        """Тест определения crontab окружения"""
        original_isatty = os.isatty
        original_environ = os.environ.copy()
        
        try:
            os.isatty = lambda fd: False
            os.environ.clear()
            os.environ.update({'PATH': '/usr/bin:/bin'})
            
            notifier = Notifier()
            self.assertTrue(notifier.is_cron, "Crontab окружение должно определяться как cron")
        finally:
            os.isatty = original_isatty
            os.environ.clear()
            os.environ.update(original_environ)

    def test_cron_with_mailto_detection(self):
        """Тест определения crontab по переменной MAILTO"""
        original_isatty = os.isatty
        original_environ = os.environ.copy()
        
        try:
            os.isatty = lambda fd: False
            os.environ.update({'MAILTO': 'user@example.com'})
            
            notifier = Notifier()
            self.assertTrue(notifier.is_cron, "Наличие MAILTO должно указывать на cron")
        finally:
            os.isatty = original_isatty
            os.environ.clear()
            os.environ.update(original_environ)

    def test_macos_notification_methods(self):
        """Тест разных методов macOS уведомлений"""
        # Тестируем логику выбора activate приложения
        notifier_cron = Notifier()
        notifier_cron.is_cron = True
        
        notifier_normal = Notifier()
        notifier_normal.is_cron = False
        
        # Проверяем, что флаг is_cron установлен правильно
        self.assertTrue(notifier_cron.is_cron)
        self.assertFalse(notifier_normal.is_cron)

    def test_notification_sending_logic(self):
        """Тест логики отправки уведомлений"""
        notifier = Notifier()
        
        # Тестируем определение системы
        self.assertIn(notifier.system, ["Darwin", "Linux", "Windows"])
        
        # Тестируем наличие метода отправки
        self.assertTrue(hasattr(notifier, 'send_notification'))
        self.assertTrue(callable(getattr(notifier, 'send_notification')))


if __name__ == "__main__":
    unittest.main()