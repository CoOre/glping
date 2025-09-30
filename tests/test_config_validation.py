#!/usr/bin/env python3
"""
Тесты валидации конфигурации
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from glping.config import Config


class TestConfigValidation(unittest.TestCase):
    """Тесты валидации конфигурации"""

    def setUp(self):
        """Подготовка тестового окружения"""
        self.temp_dir = tempfile.mkdtemp()
        self.env_file = os.path.join(self.temp_dir, ".env")

    def tearDown(self):
        """Очистка тестового окружения"""
        if os.path.exists(self.env_file):
            os.unlink(self.env_file)
        os.rmdir(self.temp_dir)

    def test_missing_token_error(self):
        """Тест ошибки отсутствия токена"""
        with patch('glping.config.load_dotenv') as mock_load_dotenv, \
             patch('glping.config.os.path.exists') as mock_exists, \
             patch('glping.config.os.makedirs') as mock_makedirs:
            
            # Эмулируем отсутствие .env файлов
            mock_exists.return_value = False
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(ValueError) as context:
                    Config()
                self.assertIn("GITLAB_TOKEN обязателен", str(context.exception))

    def test_invalid_url_error(self):
        """Тест ошибки невалидного URL"""
        env_content = """
GITLAB_URL=invalid-url
GITLAB_TOKEN=test_token_123456789
CHECK_INTERVAL=60
"""
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        with patch.dict(os.environ, {'GITLAB_URL': 'invalid-url', 'GITLAB_TOKEN': 'test_token_123456789'}):
            with self.assertRaises(ValueError) as context:
                Config()
            self.assertIn("должен начинаться с http:// или https://", str(context.exception))

    def test_short_token_error(self):
        """Тест ошибки короткого токена"""
        with patch.dict(os.environ, {'GITLAB_URL': 'https://gitlab.com', 'GITLAB_TOKEN': 'short'}):
            with self.assertRaises(ValueError) as context:
                Config()
            self.assertIn("слишком короткий", str(context.exception))

    def test_invalid_interval_error(self):
        """Тест ошибки невалидного интервала"""
        with patch.dict(os.environ, {
            'GITLAB_URL': 'https://gitlab.com', 
            'GITLAB_TOKEN': 'test_token_123456789',
            'CHECK_INTERVAL': '0'
        }):
            with self.assertRaises(ValueError) as context:
                Config()
            self.assertIn("положительным числом", str(context.exception))

    def test_large_interval_warning(self):
        """Тест предупреждения о большом интервале"""
        with patch.dict(os.environ, {
            'GITLAB_URL': 'https://gitlab.com', 
            'GITLAB_TOKEN': 'test_token_123456789',
            'CHECK_INTERVAL': '7200'
        }):
            with patch('builtins.print') as mock_print:
                Config()
                # Проверяем что было выведено предупреждение
                warning_calls = [call for call in mock_print.call_args_list 
                               if 'CHECK_INTERVAL' in str(call) and 'очень большой' in str(call)]
                self.assertTrue(len(warning_calls) > 0)

    def test_valid_config_success(self):
        """Тест успешной валидации корректной конфигурации"""
        with patch.dict(os.environ, {
            'GITLAB_URL': 'https://gitlab.example.com', 
            'GITLAB_TOKEN': 'glpat-1234567890abcdef',
            'CHECK_INTERVAL': '120'
        }):
            # Не должно быть исключений
            config = Config()
            self.assertEqual(config.gitlab_url, 'https://gitlab.example.com')
            self.assertEqual(config.gitlab_token, 'glpat-1234567890abcdef')
            self.assertEqual(config.check_interval, 120)

    def test_default_values(self):
        """Тест значений по умолчанию"""
        with patch.dict(os.environ, {
            'GITLAB_URL': 'https://gitlab.com', 
            'GITLAB_TOKEN': 'glpat-1234567890abcdef'
        }, clear=True):
            config = Config()
            self.assertEqual(config.check_interval, 60)  # значение по умолчанию


if __name__ == '__main__':
    unittest.main()