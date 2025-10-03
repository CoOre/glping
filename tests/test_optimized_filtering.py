#!/usr/bin/env python3
"""
Тесты оптимизированной фильтрации проектов по last_activity_after
"""

import asyncio
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from glping.async_gitlab_api import AsyncGitLabAPI
from glping.async_watcher import AsyncGitLabWatcher
from glping.cache import Cache
from glping.config import Config


class TestOptimizedFiltering(unittest.IsolatedAsyncioTestCase):
    """Тесты оптимизированной фильтрации проектов"""

    def setUp(self):
        """Подготовка тестового окружения"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.temp_dir, "test_cache.json")
        
        # Создаем тестовую конфигурацию
        self.config = MagicMock()
        self.config.gitlab_url = "https://gitlab.example.com"
        self.config.gitlab_token = "test_token"
        self.config.cache_file = self.cache_file
        self.config.get_project_filter.return_value = {"membership": True}

    def tearDown(self):
        """Очистка тестового окружения"""
        if os.path.exists(self.cache_file):
            os.unlink(self.cache_file)
        os.rmdir(self.temp_dir)

    async def test_server_side_filtering_with_last_activity_after(self):
        """Тест серверной фильтрации с параметром last_activity_after"""
        # Создаем мок API
        mock_api = AsyncMock(spec=AsyncGitLabAPI)
        
        # Тестовые проекты
        active_projects = [
            {
                "id": 1,
                "name": "Active Project 1",
                "name_with_namespace": "Group / Active Project 1",
                "last_activity_at": "2025-09-30T10:00:00Z"
            },
            {
                "id": 2, 
                "name": "Active Project 2",
                "name_with_namespace": "Group / Active Project 2",
                "last_activity_at": "2025-09-30T12:00:00Z"
            }
        ]
        
        mock_api.get_projects.return_value = active_projects
        
        # Создаем watcher с мок API
        with patch('glping.async_watcher.AsyncGitLabAPI', return_value=mock_api):
            watcher = AsyncGitLabWatcher(self.config)
            watcher.api = mock_api
            
            # Устанавливаем дату последней проверки
            last_checked = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            await watcher.cache.set_last_checked_async(last_checked)
            
            # Выполняем проверку
            await watcher.check_projects(verbose=False)
            
            # Проверяем, что API был вызван с фильтрацией
            mock_api.get_projects.assert_called_once_with(
                membership=True,
                fields=[
                    "id",
                    "name", 
                    "name_with_namespace",
                    "path_with_namespace",
                    "last_activity_at",
                ],
                last_activity_after=last_checked
            )

    async def test_first_run_without_filtering(self):
        """Тест первого запуска без фильтрации"""
        # Создаем мок API
        mock_api = AsyncMock(spec=AsyncGitLabAPI)
        
        # Тестовые проекты
        all_projects = [
            {
                "id": 1,
                "name": "Project 1",
                "name_with_namespace": "Group / Project 1",
                "last_activity_at": "2025-09-28T10:00:00Z"
            },
            {
                "id": 2,
                "name": "Project 2", 
                "name_with_namespace": "Group / Project 2",
                "last_activity_at": "2025-09-29T12:00:00Z"
            }
        ]
        
        mock_api.get_projects.return_value = all_projects
        
 # Создаем watcher с мок API
        with patch('glping.async_watcher.AsyncGitLabAPI', return_value=mock_api):
            watcher = AsyncGitLabWatcher(self.config)
            watcher.api = mock_api
            
            # Принудительно очищаем кеш для имитации первого запуска
            watcher.cache.data = {}
            
            # Первый запуск - нет даты последней проверки
            await watcher.check_projects(verbose=False)
            
            # Проверяем, что API был вызван БЕЗ параметра last_activity_after
            mock_api.get_projects.assert_called_once_with(
                membership=True,
                fields=[
                    "id",
                    "name",
                    "name_with_namespace", 
                    "path_with_namespace",
                    "last_activity_at",
                ]
            )

    async def test_cache_activity_update(self):
        """Тест обновления кеша активности проектов"""
        # Создаем мок API
        mock_api = AsyncMock(spec=AsyncGitLabAPI)
        
        test_project = {
            "id": 123,
            "name": "Test Project",
            "name_with_namespace": "Group / Test Project",
            "last_activity_at": "2025-09-30T15:30:00Z"
        }
        
        mock_api.get_projects.return_value = [test_project]
        mock_api.get_project_events.return_value = []
        
        # Создаем watcher с мок API
        with patch('glping.async_watcher.AsyncGitLabAPI', return_value=mock_api):
            watcher = AsyncGitLabWatcher(self.config)
            watcher.api = mock_api
            
            # Устанавливаем дату последней проверки
            last_checked = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            await watcher.cache.set_last_checked_async(last_checked)
            
            # Выполняем проверку
            await watcher.check_projects(verbose=False)
            
            # Проверяем, что активность проекта была сохранена в кеш
            cached_activity = watcher.cache.get_project_activity(123)
            self.assertEqual(cached_activity, "2025-09-30T15:30:00Z")

    def test_sync_api_supports_filtering(self):
        """Тест поддержки фильтрации в синхронном API"""
        from glping.gitlab_api import GitLabAPI
        
        # Создаем мок для gitlab
        with patch('glping.gitlab_api.gitlab') as mock_gitlab:
            mock_gl = MagicMock()
            mock_gitlab.Gitlab.return_value = mock_gl
            
            # Создаем тестовые проекты
            mock_projects = [
                MagicMock(asdict=lambda: {
                    "id": 1,
                    "name": "Test Project",
                    "last_activity_at": "2025-09-30T10:00:00Z"
                })
            ]
            
            mock_gl.projects.list.return_value = mock_projects
            
            # Создаем API и вызываем с фильтрацией
            api = GitLabAPI("https://gitlab.example.com", "test_token")
            projects = api.get_projects(
                membership=True, 
                last_activity_after="2025-09-29T00:00:00Z"
            )
            
            # Проверяем, что list был вызван с правильными параметрами
            mock_gl.projects.list.assert_called_once_with(
                membership=True,
                get_all=True,
                last_activity_after="2025-09-29T00:00:00Z"
            )
            
            self.assertEqual(len(projects), 1)
            self.assertEqual(projects[0]["id"], 1)


def run_async_test(coro):
    """Вспомогательная функция для запуска асинхронных тестов"""
    return asyncio.run(coro)


if __name__ == "__main__":
    # Адаптируем асинхронные тесты для unittest
    class TestOptimizedFilteringAsync(TestOptimizedFiltering):
        def test_server_side_filtering_with_last_activity_after(self):
            run_async_test(super().test_server_side_filtering_with_last_activity_after())
        
        def test_first_run_without_filtering(self):
            run_async_test(super().test_first_run_without_filtering())
            
        def test_cache_activity_update(self):
            run_async_test(super().test_cache_activity_update())
    
    unittest.main()