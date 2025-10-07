#!/usr/bin/env python3

import os
import sys
import unittest
from unittest.mock import Mock

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.utils.event_utils import (
    get_event_description,
    get_job_status_emoji,
    get_deployment_status_emoji,
    job_to_event,
    deployment_to_event,
    get_pipeline_status_emoji
)


class TestCICDEvents(unittest.TestCase):
    """Тестирование CI/CD событий GitLab"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.sample_project = {
            "id": 123,
            "name_with_namespace": "test-group/ci-project",
            "name": "ci-project"
        }

    def test_pipeline_skipped_status(self):
        """Тест статуса skipped для pipeline"""
        self.assertEqual(get_pipeline_status_emoji("skipped"), "⏭️")
        
        event = {
            "target_type": "Pipeline",
            "action_name": "updated",
            "author": {"name": "Система CI/CD"},
            "target_id": 456,
            "data": {"status": "skipped", "ref": "main"},
            "created_at": "2025-10-06T12:00:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Pipeline #456 пропущен", description)
        self.assertIn("для main", description)

    def test_job_status_emoji(self):
        """Тест emoji для статусов job"""
        self.assertEqual(get_job_status_emoji("success"), "✅")
        self.assertEqual(get_job_status_emoji("failed"), "❌")
        self.assertEqual(get_job_status_emoji("running"), "🔄")
        self.assertEqual(get_job_status_emoji("pending"), "⏳")
        self.assertEqual(get_job_status_emoji("canceled"), "🚫")
        self.assertEqual(get_job_status_emoji("skipped"), "⏭️")
        self.assertEqual(get_job_status_emoji("manual"), "⏸️")
        self.assertEqual(get_job_status_emoji("unknown"), "❓")

    def test_job_event_description(self):
        """Тест описания job событий"""
        event = {
            "target_type": "Job",
            "action_name": "updated",
            "author": {"name": "Иван Петров"},
            "target_id": 789,
            "data": {
                "status": "success",
                "name": "build",
                "stage": "test"
            },
            "created_at": "2025-10-06T12:05:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Job 'build' успешно", description)
        self.assertIn("(stage: test)", description)
        self.assertIn("Иван Петров", description)

    def test_job_event_without_name(self):
        """Тест job события без имени"""
        event = {
            "target_type": "Job",
            "action_name": "updated",
            "author": {"name": "Система CI/CD"},
            "target_id": 101,
            "data": {"status": "failed"},
            "created_at": "2025-10-06T12:10:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Job #101 с ошибкой", description)
        self.assertIn("Система CI/CD", description)

    def test_job_to_event_conversion(self):
        """Тест конвертации job в событие"""
        job = {
            "id": 456,
            "status": "success",
            "name": "test",
            "stage": "test",
            "ref": "main",
            "created_at": "2025-10-06T12:15:00Z",
            "duration": 120,
            "user": {
                "name": "Анна Смирнова",
                "username": "annasmirnova"
            }
        }
        
        event = job_to_event(job, self.sample_project)
        
        self.assertEqual(event["id"], "job_456")
        self.assertEqual(event["target_type"], "Job")
        self.assertEqual(event["target_id"], 456)
        self.assertEqual(event["data"]["status"], "success")
        self.assertEqual(event["data"]["name"], "test")
        self.assertEqual(event["data"]["stage"], "test")
        self.assertEqual(event["author"]["name"], "Анна Смирнова")

    def test_job_to_event_without_user(self):
        """Тест конвертации job без пользователя"""
        job = {
            "id": 789,
            "status": "failed",
            "name": "deploy",
            "created_at": "2025-10-06T12:20:00Z"
        }
        
        event = job_to_event(job, self.sample_project)
        
        self.assertEqual(event["author"]["name"], "Система CI/CD")
        self.assertEqual(event["author"]["username"], "system")

    def test_deployment_status_emoji(self):
        """Тест emoji для статусов deployment"""
        self.assertEqual(get_deployment_status_emoji("created"), "📝")
        self.assertEqual(get_deployment_status_emoji("running"), "🚀")
        self.assertEqual(get_deployment_status_emoji("success"), "✅")
        self.assertEqual(get_deployment_status_emoji("failed"), "❌")
        self.assertEqual(get_deployment_status_emoji("canceled"), "🚫")
        self.assertEqual(get_deployment_status_emoji("skipped"), "⏭️")
        self.assertEqual(get_deployment_status_emoji("unknown"), "❓")

    def test_deployment_event_description(self):
        """Тест описания deployment событий"""
        event = {
            "target_type": "Deployment",
            "action_name": "updated",
            "author": {"name": "Михаил Козлов"},
            "target_id": 202,
            "data": {
                "status": "success",
                "environment": "production"
            },
            "created_at": "2025-10-06T12:25:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Развертывание #202 успешно", description)
        self.assertIn("в production", description)
        self.assertIn("Михаил Козлов", description)

    def test_deployment_event_without_environment(self):
        """Тест deployment события без environment"""
        event = {
            "target_type": "Deployment",
            "action_name": "updated",
            "author": {"name": "Ольга Новикова"},
            "target_id": 303,
            "data": {"status": "running"},
            "created_at": "2025-10-06T12:30:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Развертывание #303 выполняется", description)
        self.assertIn("Ольга Новикова", description)
        # Не должно содержать "в " (с пробелом) - нет environment
        self.assertNotIn(" в ", description)

    def test_deployment_to_event_conversion(self):
        """Тест конвертации deployment в событие"""
        deployment = {
            "id": 404,
            "status": "success",
            "environment": "staging",
            "ref": "main",
            "created_at": "2025-10-06T12:35:00Z",
            "updated_at": "2025-10-06T12:40:00Z",
            "user": {
                "name": "Дмитрий Волков",
                "username": "dmitryvolkov"
            }
        }
        
        event = deployment_to_event(deployment, self.sample_project)
        
        self.assertEqual(event["id"], "deployment_404")
        self.assertEqual(event["target_type"], "Deployment")
        self.assertEqual(event["target_id"], 404)
        self.assertEqual(event["data"]["status"], "success")
        self.assertEqual(event["data"]["environment"], "staging")
        self.assertEqual(event["author"]["name"], "Дмитрий Волков")

    def test_deployment_to_event_without_user(self):
        """Тест конвертации deployment без пользователя"""
        deployment = {
            "id": 505,
            "status": "failed",
            "environment": "production",
            "created_at": "2025-10-06T12:45:00Z"
        }
        
        event = deployment_to_event(deployment, self.sample_project)
        
        self.assertEqual(event["author"]["name"], "Система CI/CD")
        self.assertEqual(event["author"]["username"], "system")

    def test_all_job_statuses(self):
        """Тест всех статусов job"""
        statuses = ["success", "failed", "running", "pending", "canceled", "skipped", "manual"]
        expected_words = ["успешно", "с ошибкой", "выполняется", "ожидает", "отменен", "пропущен", "вручную"]
        
        for status, expected in zip(statuses, expected_words):
            event = {
                "target_type": "Job",
                "action_name": "updated",
                "author": {"name": "Test User"},
                "target_id": 1,
                "data": {"status": status, "name": "test-job"},
                "created_at": "2025-10-06T12:00:00Z"
            }
            
            description = get_event_description(event)
            self.assertIn(expected, description, f"Статус {status} не содержит ожидаемое слово '{expected}'")

    def test_all_deployment_statuses(self):
        """Тест всех статусов deployment"""
        statuses = ["created", "running", "success", "failed", "canceled", "skipped"]
        expected_words = ["создано", "выполняется", "успешно", "с ошибкой", "отменено", "пропущено"]
        
        for status, expected in zip(statuses, expected_words):
            event = {
                "target_type": "Deployment",
                "action_name": "updated",
                "author": {"name": "Test User"},
                "target_id": 1,
                "data": {"status": status, "environment": "test"},
                "created_at": "2025-10-06T12:00:00Z"
            }
            
            description = get_event_description(event)
            self.assertIn(expected, description, f"Статус {status} не содержит ожидаемое слово '{expected}'")


class TestCICDIntegration(unittest.TestCase):
    """Интеграционные тесты для CI/CD функциональности"""

    def test_job_and_deployment_uniqueness(self):
        """Тест уникальности ID для job и deployment событий"""
        project = {"id": 123, "name_with_namespace": "test/test"}
        
        job = {"id": 100, "status": "success", "created_at": "2025-10-06T12:00:00Z"}
        deployment = {"id": 100, "status": "success", "created_at": "2025-10-06T12:00:00Z"}
        
        job_event = job_to_event(job, project)
        deployment_event = deployment_to_event(deployment, project)
        
        # ID должны быть разными даже при одинаковом исходном ID
        self.assertNotEqual(job_event["id"], deployment_event["id"])
        self.assertEqual(job_event["id"], "job_100")
        self.assertEqual(deployment_event["id"], "deployment_100")

    def test_ci_cd_event_date_formatting(self):
        """Тест форматирования даты в CI/CD событиях"""
        project = {"id": 123, "name_with_namespace": "test/test"}
        
        job = {
            "id": 200,
            "status": "success",
            "name": "test",
            "created_at": "2025-10-06T15:30:00Z"
        }
        
        event = job_to_event(job, project)
        description = get_event_description(event)
        
        # Проверяем наличие даты в описании
        self.assertTrue("06.10" in description or "2025-10-06" in description)


def run_ci_cd_tests():
    """Запустить все тесты CI/CD событий"""
    print("🧪 Запуск тестов CI/CD событий GitLab")
    print("=" * 50)
    
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestCICDEvents))
    suite.addTests(loader.loadTestsFromTestCase(TestCICDIntegration))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результат
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ Все тесты CI/CD событий пройдены!")
    else:
        print(f"❌ Тесты не пройдены: {len(result.failures)} ошибок, {len(result.errors)} сбоев")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_ci_cd_tests()