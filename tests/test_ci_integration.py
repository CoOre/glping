#!/usr/bin/env python3

import os
import sys
import unittest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.async_watcher import AsyncGitLabWatcher
from glping.watcher import GitLabWatcher
from glping.config import Config
from glping.utils.event_utils import pipeline_to_event


class TestCIIntegration(unittest.TestCase):
    """Интеграционные тесты для CI/CD функциональности"""

    def setUp(self):
        """Настройка тестового окружения"""
        # Создаем mock конфигурацию
        self.mock_config = Mock(spec=Config)
        self.mock_config.gitlab_url = "https://gitlab.example.com"
        self.mock_config.gitlab_token = "test_token"
        self.mock_config.check_interval = 60
        self.mock_config.cache_file = "/tmp/test_cache.json"
        self.mock_config.get_project_filter.return_value = {"membership": True}

    def test_ci_notification_flow_success(self):
        """Тест полного цикла уведомления для успешного pipeline"""
        # Создаем mock объекты
        mock_api = Mock()
        mock_cache = Mock()
        mock_notifier = Mock()
        
        # Настраиваем mock API
        mock_api.get_projects.return_value = [
            {
                "id": 123,
                "name_with_namespace": "test-group/ci-project",
                "last_activity_at": "2025-10-03T19:30:00Z"
            }
        ]
        
        mock_api.get_project_events.return_value = []
        
        # Настраиваем mock pipelines
        success_pipeline = {
            "id": 456,
            "status": "success",
            "ref": "main",
            "sha": "abc123def456",
            "created_at": "2025-10-03T19:25:00Z",
            "updated_at": "2025-10-03T19:30:00Z",
            "duration": 300,
            "user": {
                "name": "John Doe",
                "username": "johndoe"
            }
        }
        
        mock_api.get_project_pipelines.return_value = [success_pipeline]
        
        # Настраиваем mock cache
        mock_cache.get_last_checked.return_value = "2025-10-03T19:00:00Z"
        mock_cache.get_last_event_id.return_value = None
        mock_cache.get_project_events.return_value = set()
        
        # Создаем watcher
        with patch('glping.watcher.GitLabAPI', return_value=mock_api), \
             patch('glping.watcher.Cache', return_value=mock_cache), \
             patch('glping.watcher.Notifier', return_value=mock_notifier):
            
            watcher = GitLabWatcher(self.mock_config)
            watcher.api = mock_api
            watcher.cache = mock_cache
            watcher.notifier = mock_notifier
            
            # Запускаем проверку
            watcher.check_projects(verbose=True)
            
            # Проверяем, что был вызван метод получения pipelines
            mock_api.get_project_pipelines.assert_called()
            
            # Проверяем, что было отправлено уведомление
            mock_notifier.send_notification.assert_called()
            
            # Проверяем параметры уведомления
            mock_notifier.send_notification.assert_called()
            call_args = mock_notifier.send_notification.call_args
            message = call_args[1]["message"] if call_args[1] else str(call_args)
            title = call_args[1]["title"] if call_args[1] and "title" in call_args[1] else ""
            
            self.assertIn("Pipeline #456", message)
            self.assertIn("успешно", message)
            self.assertIn("test-group/ci-project", title)

    def test_ci_notification_flow_failure(self):
        """Тест полного цикла уведомления для упавшего pipeline"""
        mock_api = Mock()
        mock_cache = Mock()
        mock_notifier = Mock()
        
        # Настраиваем mock API
        mock_api.get_projects.return_value = [
            {
                "id": 123,
                "name_with_namespace": "test-group/ci-project",
                "last_activity_at": "2025-10-03T19:30:00Z"
            }
        ]
        
        mock_api.get_project_events.return_value = []
        
        # Настраиваем mock pipelines
        failed_pipeline = {
            "id": 789,
            "status": "failed",
            "ref": "feature/new-feature",
            "sha": "def456abc123",
            "created_at": "2025-10-03T19:25:00Z",
            "updated_at": "2025-10-03T19:28:00Z",
            "duration": 180,
            "user": {
                "name": "Jane Smith",
                "username": "janesmith"
            }
        }
        
        mock_api.get_project_pipelines.return_value = [failed_pipeline]
        
        # Настраиваем mock cache
        mock_cache.get_last_checked.return_value = "2025-10-03T19:00:00Z"
        mock_cache.get_last_event_id.return_value = None
        mock_cache.get_project_events.return_value = set()
        mock_cache.set_last_event_id = Mock()
        mock_cache.save_project_event = Mock()
        
        # Создаем watcher
        with patch('glping.watcher.GitLabAPI', return_value=mock_api), \
             patch('glping.watcher.Cache', return_value=mock_cache), \
             patch('glping.watcher.Notifier', return_value=mock_notifier):
            
            watcher = GitLabWatcher(self.mock_config)
            watcher.api = mock_api
            watcher.cache = mock_cache
            watcher.notifier = mock_notifier
            
            # Запускаем проверку
            watcher.check_projects(verbose=True)
            
            # Проверяем, что было отправлено уведомление
            mock_notifier.send_notification.assert_called()
            
            # Проверяем параметры уведомления
            mock_notifier.send_notification.assert_called()
            call_args = mock_notifier.send_notification.call_args
            message = call_args[1]["message"] if call_args[1] else str(call_args)
            
            self.assertIn("Pipeline #789", message)
            self.assertIn("с ошибкой", message)
            self.assertIn("feature/new-feature", message)

    def test_multiple_pipeline_statuses(self):
        """Тест обработки различных статусов pipelines"""
        mock_api = Mock()
        mock_cache = Mock()
        mock_notifier = Mock()
        
        # Настраиваем mock API
        mock_api.get_projects.return_value = [
            {
                "id": 123,
                "name_with_namespace": "test-group/multi-status-project",
                "last_activity_at": "2025-10-03T19:30:00Z"
            }
        ]
        
        mock_api.get_project_events.return_value = []
        
        # Настраиваем mock pipelines с разными статусами
        pipelines = [
            {
                "id": 100,
                "status": "success",
                "ref": "main",
                "created_at": "2025-10-03T19:10:00Z",
                "user": {"name": "User1", "username": "user1"}
            },
            {
                "id": 101,
                "status": "failed",
                "ref": "develop",
                "created_at": "2025-10-03T19:15:00Z",
                "user": {"name": "User2", "username": "user2"}
            },
            {
                "id": 102,
                "status": "running",
                "ref": "feature/test",
                "created_at": "2025-10-03T19:20:00Z",
                "user": {"name": "User3", "username": "user3"}
            }
        ]
        
        mock_api.get_project_pipelines.return_value = pipelines
        
        # Настраиваем mock cache
        mock_cache.get_last_checked.return_value = "2025-10-03T19:00:00Z"
        mock_cache.get_last_event_id.return_value = None
        mock_cache.get_project_events.return_value = set()
        
        # Создаем watcher
        with patch('glping.watcher.GitLabAPI', return_value=mock_api), \
             patch('glping.watcher.Cache', return_value=mock_cache), \
             patch('glping.watcher.Notifier', return_value=mock_notifier):
            
            watcher = GitLabWatcher(self.mock_config)
            watcher.api = mock_api
            watcher.cache = mock_cache
            watcher.notifier = mock_notifier
            
            # Запускаем проверку
            watcher.check_projects(verbose=True)
            
            # Проверяем, что было отправлено 3 уведомления
            self.assertEqual(mock_notifier.send_notification.call_count, 3)
            
            # Проверяем содержимое уведомлений
            calls = mock_notifier.send_notification.call_args_list
            messages = []
            for call in calls:
                if call[1] and "message" in call[1]:
                    messages.append(call[1]["message"])
                else:
                    messages.append(str(call))
            
            # Проверяем наличие всех статусов
            success_found = any("успешно" in msg and "Pipeline #100" in msg for msg in messages)
            failed_found = any("с ошибкой" in msg and "Pipeline #101" in msg for msg in messages)
            running_found = any("выполняется" in msg and "Pipeline #102" in msg for msg in messages)
            
            self.assertTrue(success_found, "Не найдено уведомление об успешном pipeline")
            self.assertTrue(failed_found, "Не найдено уведомление об упавшем pipeline")
            self.assertTrue(running_found, "Не найдено уведомление о выполняющемся pipeline")

    def test_pipeline_duplicate_prevention(self):
        """Тест предотвращения дублирования pipeline уведомлений"""
        mock_api = Mock()
        mock_cache = Mock()
        mock_notifier = Mock()
        
        # Настраиваем mock API
        mock_api.get_projects.return_value = [
            {
                "id": 123,
                "name_with_namespace": "test-group/duplicate-test",
                "last_activity_at": "2025-10-03T19:30:00Z"
            }
        ]
        
        mock_api.get_project_events.return_value = []
        
        # Настраиваем mock pipeline
        pipeline = {
            "id": 456,
            "status": "success",
            "ref": "main",
            "created_at": "2025-10-03T19:25:00Z",
            "user": {"name": "John Doe", "username": "johndoe"}
        }
        
        mock_api.get_project_pipelines.return_value = [pipeline]
        
        # Настраиваем mock cache - pipeline уже в кеше
        mock_cache.get_last_checked.return_value = "2025-10-03T19:00:00Z"
        mock_cache.get_last_event_id.return_value = None
        mock_cache.get_project_events.return_value = {"pipeline_456"}
        mock_cache.set_last_event_id = Mock()
        mock_cache.save_project_event = Mock()
        
        # Создаем watcher
        with patch('glping.watcher.GitLabAPI', return_value=mock_api), \
             patch('glping.watcher.Cache', return_value=mock_cache), \
             patch('glping.watcher.Notifier', return_value=mock_notifier):
            
            watcher = GitLabWatcher(self.mock_config)
            watcher.api = mock_api
            watcher.cache = mock_cache
            watcher.notifier = mock_notifier
            
            # Запускаем проверку
            watcher.check_projects(verbose=True)
            
            # Проверяем, что уведомление НЕ было отправлено (дубликат)
            mock_notifier.send_notification.assert_not_called()

    def test_pipeline_date_filtering(self):
        """Тест фильтрации pipeline по дате"""
        mock_api = Mock()
        mock_cache = Mock()
        mock_notifier = Mock()
        
        # Настраиваем mock API
        mock_api.get_projects.return_value = [
            {
                "id": 123,
                "name_with_namespace": "test-group/date-filter-test",
                "last_activity_at": "2025-10-03T19:30:00Z"
            }
        ]
        
        mock_api.get_project_events.return_value = []
        
        # Настраиваем mock pipelines - один старый, один новый
        old_pipeline = {
            "id": 100,
            "status": "success",
            "ref": "main",
            "created_at": "2025-10-02T19:00:00Z",  # Старый
            "user": {"name": "Old User", "username": "olduser"}
        }
        
        new_pipeline = {
            "id": 101,
            "status": "failed",
            "ref": "main",
            "created_at": "2025-10-03T19:25:00Z",  # Новый
            "user": {"name": "New User", "username": "newuser"}
        }
        
mock_api.get_project_pipelines.return_value = [old_pipeline, new_pipeline]
        
        # Настраиваем mock cache
        mock_cache.get_last_checked.return_value = "2025-10-03T19:00:00Z"  # Проверка после старого pipeline
        mock_cache.get_last_event_id.return_value = None
        mock_cache.get_project_events.return_value = set()
        mock_cache.set_last_event_id = Mock()
        mock_cache.save_project_event = Mock()
        mock_cache.set_last_event_id = Mock()
        mock_cache.save_project_event = Mock()
        
        # Создаем watcher
        with patch('glping.watcher.GitLabAPI', return_value=mock_api), \
             patch('glping.watcher.Cache', return_value=mock_cache), \
             patch('glping.watcher.Notifier', return_value=mock_notifier):
            
            watcher = GitLabWatcher(self.mock_config)
            watcher.api = mock_api
            watcher.cache = mock_cache
            watcher.notifier = mock_notifier
            
            # Запускаем проверку
            watcher.check_projects(verbose=True)
            
            # Проверяем, что было отправлено только одно уведомление (новый pipeline)
            mock_notifier.send_notification.assert_called_once()
            
            # Проверяем, что уведомление о новом pipeline
            mock_notifier.send_notification.assert_called_once()
            call_args = mock_notifier.send_notification.call_args
            message = call_args[1]["message"] if call_args[1] else str(call_args)
            self.assertIn("Pipeline #101", message)


class TestAsyncCIIntegration(unittest.IsolatedAsyncioTestCase):
    """Асинхронные интеграционные тесты для CI/CD"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.mock_config = Mock(spec=Config)
        self.mock_config.gitlab_url = "https://gitlab.example.com"
        self.mock_config.gitlab_token = "test_token"
        self.mock_config.check_interval = 60
        self.mock_config.cache_file = "/tmp/test_cache.json"
        self.mock_config.get_project_filter.return_value = {"membership": True}

    async def test_async_ci_notification_flow(self):
        """Тест асинхронного цикла уведомлений для CI"""
        # Создаем mock объекты
        mock_api = AsyncMock()
        mock_cache = AsyncMock()
        mock_notifier = Mock()
        
        # Настраиваем mock API
        mock_api.get_projects.return_value = [
            {
                "id": 123,
                "name_with_namespace": "test-group/async-ci-project",
                "last_activity_at": "2025-10-03T19:30:00Z"
            }
        ]
        
        mock_api.get_project_events.return_value = []
        
        # Настраиваем mock pipelines
        pipeline = {
            "id": 456,
            "status": "success",
            "ref": "main",
            "created_at": "2025-10-03T19:25:00Z",
            "user": {"name": "Async User", "username": "asyncuser"}
        }
        
        mock_api.get_project_pipelines.return_value = [pipeline]
        
        # Настраиваем mock cache
        mock_cache.get_last_checked.return_value = "2025-10-03T19:00:00Z"
        mock_cache.get_last_event_id.return_value = None
        mock_cache.get_project_events.return_value = set()
        mock_cache.set_last_checked_async = AsyncMock()
        mock_cache.set_last_event_id_async = AsyncMock()
        mock_cache.save_project_event = Mock()
        
        # Создаем async watcher
        with patch('glping.async_watcher.AsyncGitLabAPI', return_value=mock_api), \
             patch('glping.async_watcher.Cache', return_value=mock_cache), \
             patch('glping.async_watcher.Notifier', return_value=mock_notifier):
            
            watcher = AsyncGitLabWatcher(self.mock_config)
            watcher.api = mock_api
            watcher.cache = mock_cache
            watcher.notifier = mock_notifier
            
            # Запускаем проверку
            await watcher.check_projects(verbose=True)
            
            # Проверяем, что был вызван метод получения pipelines
            mock_api.get_project_pipelines.assert_called()
            
            # Проверяем, что было отправлено уведомление
            mock_notifier.send_notification.assert_called()

    # Удаляем обертку, так как используем IsolatedAsyncioTestCase


def run_ci_integration_tests():
    """Запустить все интеграционные тесты CI/CD"""
    print("🔄 Запуск интеграционных тестов CI/CD")
    print("=" * 50)
    
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestCIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAsyncCIIntegration))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результат
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ Все интеграционные тесты CI/CD пройдены!")
    else:
        print(f"❌ Тесты не пройдены: {len(result.failures)} ошибок, {len(result.errors)} сбоев")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_ci_integration_tests()