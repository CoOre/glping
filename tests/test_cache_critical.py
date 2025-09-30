#!/usr/bin/env python3
"""
Тесты для критических путей кеширования
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from glping.cache import Cache


class TestCacheCritical(unittest.TestCase):
    """Тесты критических функций кеширования"""

    def setUp(self):
        """Подготовка тестового окружения"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, "test_cache.json")

    def tearDown(self):
        """Очистка тестового окружения"""
        if os.path.exists(self.cache_file):
            os.unlink(self.cache_file)
        os.rmdir(self.temp_dir)

    def test_cache_initialization(self):
        """Тест инициализации кеша"""
        cache = Cache(self.cache_file)
        
        # Проверяем начальную структуру
        self.assertIn("metadata", cache.data)
        self.assertIn("projects", cache.data)
        self.assertIn("project_activity", cache.data)
        self.assertIn("last_checked", cache.data["metadata"])

    def test_cache_file_creation(self):
        """Тест создания файла кеша"""
        cache = Cache(self.cache_file)
        cache.set_last_event_id(123, 456)
        
        # Проверяем что файл создан
        self.assertTrue(os.path.exists(self.cache_file))
        
        # Проверяем содержимое
        with open(self.cache_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data["projects"]["123"]["last_event_id"], 456)

    def test_last_event_id_operations(self):
        """Тест операций с ID последнего события"""
        cache = Cache(self.cache_file)
        
        # Проверяем начальное состояние
        self.assertIsNone(cache.get_last_event_id(123))
        
        # Устанавливаем и проверяем
        cache.set_last_event_id(123, 456)
        self.assertEqual(cache.get_last_event_id(123), 456)
        
        # Перезагружаем и проверяем сохранение
        cache2 = Cache(self.cache_file)
        self.assertEqual(cache2.get_last_event_id(123), 456)

    def test_last_checked_operations(self):
        """Тест операций с временем последней проверки"""
        cache = Cache(self.cache_file)
        test_time = "2025-09-30T15:30:00+00:00"
        
        # Устанавливаем и проверяем
        cache.set_last_checked(test_time)
        self.assertEqual(cache.get_last_checked(), test_time)
        
        # Перезагружаем и проверяем сохранение
        cache2 = Cache(self.cache_file)
        self.assertEqual(cache2.get_last_checked(), test_time)

    def test_cache_reset(self):
        """Тест сброса кеша"""
        cache = Cache(self.cache_file)
        
        # Добавляем данные
        cache.set_last_event_id(123, 456)
        cache.set_project_activity(123, "2025-09-30T15:30:00Z")
        
        # Сбрасываем
        cache.reset()
        
        # Проверяем что данные очищены
        self.assertIsNone(cache.get_last_event_id(123))
        self.assertIsNone(cache.get_project_activity(123))
        self.assertIsNotNone(cache.get_last_checked())

    def test_corrupted_cache_handling(self):
        """Тест обработки поврежденного файла кеша"""
        # Создаем поврежденный файл
        with open(self.cache_file, 'w') as f:
            f.write("invalid json content")
        
        # Должен создаться новый кеш без ошибки
        cache = Cache(self.cache_file)
        self.assertIn("metadata", cache.data)

    def test_old_format_migration(self):
        """Тест миграции старого формата кеша"""
        # Создаем файл старого формата
        old_data = {
            "last_checked": "2025-09-30T15:30:00+00:00",
            "projects": {
                "123": {"last_event_id": 456}
            }
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(old_data, f)
        
        # Создаем кеш, должна произойти миграция
        cache = Cache(self.cache_file)
        
        # Проверяем новый формат
        self.assertIn("metadata", cache.data)
        self.assertIn("projects", cache.data)
        self.assertIn("project_activity", cache.data)
        self.assertEqual(cache.get_last_event_id(123), 456)

    def test_concurrent_access_simulation(self):
        """Тест симуляции конкурентного доступа"""
        cache1 = Cache(self.cache_file)
        cache2 = Cache(self.cache_file)
        
        # Оба кеша устанавливают разные значения
        cache1.set_last_event_id(123, 456)
        cache2.set_last_event_id(123, 789)
        
        # Последнее значение должно сохраниться
        cache3 = Cache(self.cache_file)
        self.assertEqual(cache3.get_last_event_id(123), 789)


if __name__ == '__main__':
    unittest.main()