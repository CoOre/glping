#!/usr/bin/env python3

import os
import sys
import unittest
from unittest.mock import Mock

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.utils.event_utils import (
    is_new_pipeline_event, save_pipeline_event_to_cache,
    is_new_job_event, save_job_event_to_cache,
    is_new_deployment_event, save_deployment_event_to_cache
)


class TestCICDCaching(unittest.TestCase):
    """Тестирование кеширования CI/CD событий с учетом статуса"""

    def setUp(self):
        """Настройка тестового окружения"""
        self.cache = Mock()
        self.cache.get_project_events.return_value = []
        self.cache.save_project_event = Mock()
        self.project_id = 123

    def test_pipeline_caching_with_status_changes(self):
        """Тест кеширования pipeline с изменением статуса"""
        pipeline = {
            "id": 1001,
            "status": "pending",
            "created_at": "2025-10-07T10:00:00Z"
        }
        
        # Первый раз - новый pipeline
        self.assertTrue(is_new_pipeline_event(pipeline, self.project_id, self.cache))
        
        # Имитируем сохранение в кеш
        self.cache.get_project_events.return_value = ["pipeline_1001_pending"]
        
        # Второй раз с тем же статусом - не новый
        self.assertFalse(is_new_pipeline_event(pipeline, self.project_id, self.cache))
        
        # Изменяем статус - снова новый
        pipeline["status"] = "running"
        self.assertTrue(is_new_pipeline_event(pipeline, self.project_id, self.cache))
        
        # Имитируем сохранение нового статуса
        self.cache.get_project_events.return_value = ["pipeline_1001_pending", "pipeline_1001_running"]
        
        # Еще раз с тем же статусом - не новый
        self.assertFalse(is_new_pipeline_event(pipeline, self.project_id, self.cache))
        
        # Изменяем на success - снова новый
        pipeline["status"] = "success"
        self.assertTrue(is_new_pipeline_event(pipeline, self.project_id, self.cache))

    def test_job_caching_with_status_changes(self):
        """Тест кеширования job с изменением статуса"""
        job = {
            "id": 2001,
            "status": "running",
            "created_at": "2025-10-07T10:05:00Z"
        }
        
        # Первый раз - новый job
        self.assertTrue(is_new_job_event(job, self.project_id, self.cache))
        
        # Имитируем сохранение в кеш
        self.cache.get_project_events.return_value = ["job_2001_running"]
        
        # Второй раз с тем же статусом - не новый
        self.assertFalse(is_new_job_event(job, self.project_id, self.cache))
        
        # Изменяем статус - снова новый
        job["status"] = "success"
        self.assertTrue(is_new_job_event(job, self.project_id, self.cache))
        
        # Имитируем сохранение нового статуса
        self.cache.get_project_events.return_value = ["job_2001_running", "job_2001_success"]
        
        # Еще раз с тем же статусом - не новый
        self.assertFalse(is_new_job_event(job, self.project_id, self.cache))
        
        # Изменяем на failed - снова новый
        job["status"] = "failed"
        self.assertTrue(is_new_job_event(job, self.project_id, self.cache))

    def test_deployment_caching_with_status_changes(self):
        """Тест кеширования deployment с изменением статуса"""
        deployment = {
            "id": 3001,
            "status": "created",
            "created_at": "2025-10-07T10:10:00Z"
        }
        
        # Первый раз - новый deployment
        self.assertTrue(is_new_deployment_event(deployment, self.project_id, self.cache))
        
        # Имитируем сохранение в кеш
        self.cache.get_project_events.return_value = ["deployment_3001_created"]
        
        # Второй раз с тем же статусом - не новый
        self.assertFalse(is_new_deployment_event(deployment, self.project_id, self.cache))
        
        # Изменяем статус - снова новый
        deployment["status"] = "running"
        self.assertTrue(is_new_deployment_event(deployment, self.project_id, self.cache))
        
        # Имитируем сохранение нового статуса
        self.cache.get_project_events.return_value = ["deployment_3001_created", "deployment_3001_running"]
        
        # Еще раз с тем же статусом - не новый
        self.assertFalse(is_new_deployment_event(deployment, self.project_id, self.cache))
        
        # Изменяем на success - снова новый
        deployment["status"] = "success"
        self.assertTrue(is_new_deployment_event(deployment, self.project_id, self.cache))

    def test_different_ids_same_status(self):
        """Тест разных ID с одинаковым статусом"""
        pipeline1 = {"id": 1001, "status": "success"}
        pipeline2 = {"id": 1002, "status": "success"}
        
        # Оба должны быть новыми
        self.assertTrue(is_new_pipeline_event(pipeline1, self.project_id, self.cache))
        self.assertTrue(is_new_pipeline_event(pipeline2, self.project_id, self.cache))

    def test_same_id_different_status(self):
        """Тест одного ID с разными статусами"""
        pipeline_id = 1001
        statuses = ["pending", "running", "success", "failed"]
        
        for status in statuses:
            pipeline = {"id": pipeline_id, "status": status}
            self.assertTrue(is_new_pipeline_event(pipeline, self.project_id, self.cache))
            save_pipeline_event_to_cache(pipeline, self.project_id, self.cache)

    def test_cache_save_calls(self):
        """Тест вызовов сохранения в кеш"""
        pipeline = {"id": 1001, "status": "success"}
        job = {"id": 2001, "status": "failed"}
        deployment = {"id": 3001, "status": "running"}
        
        save_pipeline_event_to_cache(pipeline, self.project_id, self.cache)
        save_job_event_to_cache(job, self.project_id, self.cache)
        save_deployment_event_to_cache(deployment, self.project_id, self.cache)
        
        # Проверяем что save_project_event был вызван с правильными ID
        expected_calls = [
            unittest.mock.call(self.project_id, "pipeline_1001_success"),
            unittest.mock.call(self.project_id, "job_2001_failed"),
            unittest.mock.call(self.project_id, "deployment_3001_running")
        ]
        
        self.cache.save_project_event.assert_has_calls(expected_calls)

    def test_cache_with_existing_events(self):
        """Тест работы с существующими событиями в кеше"""
        # Имитируем существующие события в кеше
        self.cache.get_project_events.return_value = [
            "pipeline_1001_pending",
            "job_2001_running",
            "deployment_3001_created"
        ]
        
        # Те же события - не новые
        pipeline_pending = {"id": 1001, "status": "pending"}
        job_running = {"id": 2001, "status": "running"}
        deployment_created = {"id": 3001, "status": "created"}
        
        self.assertFalse(is_new_pipeline_event(pipeline_pending, self.project_id, self.cache))
        self.assertFalse(is_new_job_event(job_running, self.project_id, self.cache))
        self.assertFalse(is_new_deployment_event(deployment_created, self.project_id, self.cache))
        
        # Те же ID но другие статусы - новые
        pipeline_success = {"id": 1001, "status": "success"}
        job_failed = {"id": 2001, "status": "failed"}
        deployment_running = {"id": 3001, "status": "running"}
        
        self.assertTrue(is_new_pipeline_event(pipeline_success, self.project_id, self.cache))
        self.assertTrue(is_new_job_event(job_failed, self.project_id, self.cache))
        self.assertTrue(is_new_deployment_event(deployment_running, self.project_id, self.cache))


if __name__ == "__main__":
    unittest.main()