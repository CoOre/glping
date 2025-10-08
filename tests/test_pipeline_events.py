#!/usr/bin/env python3

import os
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.utils.event_utils import (
    pipeline_to_event, 
    is_new_pipeline_event, 
    save_pipeline_event_to_cache,
    get_event_description,
    get_pipeline_status_emoji
)


class TestPipelineEvents(unittest.TestCase):
    """Тестирование обработки pipeline событий"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.sample_project = {
            "id": 123,
            "name_with_namespace": "test-group/test-project",
            "name": "test-project"
        }
        
        self.sample_pipeline = {
            "id": 456,
            "status": "success",
            "ref": "main",
            "sha": "abc123def456",
            "source": "push",
            "created_at": "2025-10-03T19:30:00Z",
            "updated_at": "2025-10-03T19:35:00Z",
            "duration": 300,
            "web_url": "https://gitlab.example.com/test-group/test-project/-/pipelines/456",
            "user": {
                "name": "John Doe",
                "username": "johndoe",
                "avatar_url": "https://gitlab.example.com/uploads/-/system/user/avatar/1/avatar.png"
            }
        }

    def test_pipeline_to_event_conversion(self):
        """Тест конвертации pipeline в формат события"""
        event = pipeline_to_event(self.sample_pipeline, self.sample_project)
        
        # Проверяем основные поля
        self.assertEqual(event["id"], "pipeline_456_success")
        self.assertEqual(event["target_type"], "Pipeline")
        self.assertEqual(event["action_name"], "updated")
        self.assertEqual(event["target_id"], 456)
        self.assertEqual(event["target_iid"], 456)
        self.assertEqual(event["project_id"], 123)
        
        # Проверяем данные автора
        self.assertEqual(event["author"]["name"], "John Doe")
        self.assertEqual(event["author"]["username"], "johndoe")
        
        # Проверяем данные pipeline
        self.assertEqual(event["data"]["status"], "success")
        self.assertEqual(event["data"]["ref"], "main")
        self.assertEqual(event["data"]["sha"], "abc123def456")
        self.assertEqual(event["data"]["source"], "push")
        self.assertEqual(event["data"]["duration"], 300)
        
        # Проверяем даты
        self.assertEqual(event["created_at"], "2025-10-03T19:30:00Z")
        self.assertEqual(event["updated_at"], "2025-10-03T19:35:00Z")

    def test_pipeline_to_event_without_user(self):
        """Тест конвертации pipeline без пользователя"""
        pipeline_no_user = {
            **self.sample_pipeline,
            "user": None
        }
        
        event = pipeline_to_event(pipeline_no_user, self.sample_project)
        
        self.assertEqual(event["author"]["name"], "Система CI/CD")
        self.assertEqual(event["author"]["username"], "system")
        self.assertEqual(event["author"]["avatar_url"], "")

    def test_pipeline_to_event_minimal_data(self):
        """Тест конвертации pipeline с минимальными данными"""
        minimal_pipeline = {
            "id": 789,
            "status": "failed",
            "created_at": "2025-10-03T20:00:00Z"
        }
        
        event = pipeline_to_event(minimal_pipeline, self.sample_project)
        
        self.assertEqual(event["id"], "pipeline_789_failed")
        self.assertEqual(event["data"]["status"], "failed")
        self.assertEqual(event["author"]["name"], "Система CI/CD")

    def test_is_new_pipeline_event(self):
        """Тест проверки нового pipeline события"""
        mock_cache = Mock()
        
        # Тест нового события
        mock_cache.get_project_events.return_value = None
        self.assertTrue(is_new_pipeline_event(self.sample_pipeline, 123, mock_cache))
        
        # Тест события в кеше
        mock_cache.get_project_events.return_value = {"pipeline_456_success"}
        self.assertFalse(is_new_pipeline_event(self.sample_pipeline, 123, mock_cache))
        
        # Тест другого события в кеше
        mock_cache.get_project_events.return_value = {"pipeline_123"}
        self.assertTrue(is_new_pipeline_event(self.sample_pipeline, 123, mock_cache))

    def test_save_pipeline_event_to_cache(self):
        """Тест сохранения pipeline события в кеш"""
        mock_cache = Mock()
        
        save_pipeline_event_to_cache(self.sample_pipeline, 123, mock_cache)
        
        mock_cache.save_project_event.assert_called_once_with(123, "pipeline_456_success")

    def test_pipeline_event_description(self):
        """Тест генерации описания для pipeline события"""
        event = pipeline_to_event(self.sample_pipeline, self.sample_project)
        description = get_event_description(event)
        
        self.assertIn("Pipeline #456 успешно", description)
        self.assertIn("для main", description)
        self.assertIn("John Doe", description)

    def test_pipeline_status_emoji(self):
        """Тест получения emoji для статусов pipeline"""
        self.assertEqual(get_pipeline_status_emoji("success"), "✅")
        self.assertEqual(get_pipeline_status_emoji("failed"), "❌")
        self.assertEqual(get_pipeline_status_emoji("running"), "🏃")
        self.assertEqual(get_pipeline_status_emoji("pending"), "⏳")
        self.assertEqual(get_pipeline_status_emoji("canceled"), "🚫")
        self.assertEqual(get_pipeline_status_emoji("unknown"), "❓")

    def test_pipeline_event_description_different_statuses(self):
        """Тест описаний для разных статусов pipeline"""
        statuses = ["success", "failed", "running", "pending", "canceled"]
        expected_descriptions = [
            "успешно", "с ошибкой", "выполняется", "ожидает", "отменен"
        ]
        
        for status, expected in zip(statuses, expected_descriptions):
            pipeline = {**self.sample_pipeline, "status": status}
            event = pipeline_to_event(pipeline, self.sample_project)
            description = get_event_description(event)
            
            self.assertIn(expected, description)

    def test_pipeline_event_with_branch(self):
        """Тест pipeline события с указанием ветки"""
        pipeline_with_branch = {
            **self.sample_pipeline,
            "ref": "feature/new-feature"
        }
        
        event = pipeline_to_event(pipeline_with_branch, self.sample_project)
        description = get_event_description(event)
        
        self.assertIn("для feature/new-feature", description)

    def test_pipeline_event_without_branch(self):
        """Тест pipeline события без указания ветки"""
        pipeline_no_branch = {
            **self.sample_pipeline,
            "ref": ""
        }
        
        event = pipeline_to_event(pipeline_no_branch, self.sample_project)
        description = get_event_description(event)
        
        # Не должно содержать "для"
        self.assertNotIn("для", description)

    def test_pipeline_event_date_formatting(self):
        """Тест форматирования даты в pipeline событии"""
        event = pipeline_to_event(self.sample_pipeline, self.sample_project)
        description = get_event_description(event)
        
        # Проверяем наличие даты в описании (формат может быть разным)
        self.assertTrue("03.10" in description or "2025-10-03" in description)


class TestPipelineIntegration(unittest.TestCase):
    """Интеграционные тесты для pipeline функциональности"""

    def test_multiple_pipeline_statuses(self):
        """Тест обработки различных статусов pipelines"""
        project = {
            "id": 123,
            "name_with_namespace": "test-group/test-project"
        }
        
        pipelines = [
            {"id": 1, "status": "success", "created_at": "2025-10-03T19:00:00Z"},
            {"id": 2, "status": "failed", "created_at": "2025-10-03T19:10:00Z"},
            {"id": 3, "status": "running", "created_at": "2025-10-03T19:20:00Z"},
        ]
        
        events = [pipeline_to_event(pipeline, project) for pipeline in pipelines]
        
        # Проверяем, что все события созданы правильно
        self.assertEqual(len(events), 3)
        
        for i, event in enumerate(events):
            self.assertEqual(event["target_type"], "Pipeline")
            self.assertEqual(event["data"]["status"], pipelines[i]["status"])
            
            description = get_event_description(event)
            if pipelines[i]["status"] == "success":
                self.assertIn("успешно", description)
            elif pipelines[i]["status"] == "failed":
                self.assertIn("с ошибкой", description)
            elif pipelines[i]["status"] == "running":
                self.assertIn("выполняется", description)

    def test_pipeline_event_uniqueness(self):
        """Тест уникальности ID pipeline событий"""
        project = {"id": 123, "name_with_namespace": "test/test"}
        
        pipeline1 = {"id": 100, "status": "success", "created_at": "2025-10-03T19:00:00Z"}
        pipeline2 = {"id": 101, "status": "failed", "created_at": "2025-10-03T19:10:00Z"}
        
        event1 = pipeline_to_event(pipeline1, project)
        event2 = pipeline_to_event(pipeline2, project)
        
        # ID должны быть уникальными
        self.assertNotEqual(event1["id"], event2["id"])
        self.assertEqual(event1["id"], "pipeline_100_success")
        self.assertEqual(event2["id"], "pipeline_101_failed")


def run_pipeline_tests():
    """Запустить все тесты pipeline событий"""
    print("🧪 Запуск тестов pipeline событий")
    print("=" * 50)
    
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineEvents))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineIntegration))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результат
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ Все тесты pipeline событий пройдены!")
    else:
        print(f"❌ Тесты не пройдены: {len(result.failures)} ошибок, {len(result.errors)} сбоев")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_pipeline_tests()