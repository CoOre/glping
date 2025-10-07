#!/usr/bin/env python3

import os
import sys
import unittest
from unittest.mock import Mock

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.utils.event_utils import get_event_description


class TestNewEvents(unittest.TestCase):
    """Тестирование новых событий GitLab"""

    def test_merge_request_reopened(self):
        """Тест события переоткрытия Merge Request"""
        event = {
            "target_type": "MergeRequest",
            "action_name": "reopened",
            "author": {"name": "Анна Смирнова"},
            "target_title": "Fix critical bug",
            "created_at": "2025-10-06T10:00:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Merge Request переоткрыт", description)
        self.assertIn("Анна Смирнова", description)
        self.assertIn("Fix critical bug", description)

    def test_merge_request_unapproved(self):
        """Тест события отзыва одобрения Merge Request"""
        event = {
            "target_type": "MergeRequest",
            "action_name": "unapproved",
            "author": {"name": "Михаил Козлов"},
            "target_title": "Add new feature",
            "created_at": "2025-10-06T10:05:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Одобрение Merge Request отозвано", description)
        self.assertIn("Михаил Козлов", description)

    def test_merge_request_review_requested(self):
        """Тест события запроса ревью Merge Request"""
        event = {
            "target_type": "MergeRequest",
            "action_name": "review_requested",
            "author": {"name": "Иван Петров"},
            "target_title": "Refactor code",
            "created_at": "2025-10-06T10:10:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Запрошено ревью Merge Request", description)
        self.assertIn("Иван Петров", description)

    def test_merge_request_ready(self):
        """Тест события перевода MR в статус Ready"""
        event = {
            "target_type": "MergeRequest",
            "action_name": "ready",
            "author": {"name": "Ольга Новикова"},
            "target_title": "Update documentation",
            "created_at": "2025-10-06T10:15:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Merge Request переведен в статус Ready", description)
        self.assertIn("Ольга Новикова", description)

    def test_merge_request_draft(self):
        """Тест события перевода MR в статус Draft"""
        event = {
            "target_type": "MergeRequest",
            "action_name": "draft",
            "author": {"name": "Елена Петрова"},
            "target_title": "WIP: New implementation",
            "created_at": "2025-10-06T10:20:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Merge Request переведен в статус Draft", description)
        self.assertIn("Елена Петрова", description)

    def test_issue_updated(self):
        """Тест события обновления задачи"""
        event = {
            "target_type": "Issue",
            "action_name": "updated",
            "author": {"name": "Александр Иванов"},
            "target_title": "Bug in authentication",
            "created_at": "2025-10-06T10:25:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Задача обновлена", description)
        self.assertIn("Александр Иванов", description)
        self.assertIn("Bug in authentication", description)

    def test_issue_moved(self):
        """Тест события перемещения задачи"""
        event = {
            "target_type": "Issue",
            "action_name": "moved",
            "author": {"name": "Дмитрий Волков"},
            "target_title": "Performance issue",
            "created_at": "2025-10-06T10:30:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Задача перемещена", description)
        self.assertIn("Дмитрий Волков", description)

    def test_push_new_branch(self):
        """Тест события создания новой ветки"""
        event = {
            "action_name": "pushed new",
            "author": {"name": "Сергей Сидоров"},
            "push_data": {
                "ref": "refs/heads/feature/new-branch",
                "action": "created",
                "commit_count": 0
            },
            "created_at": "2025-10-06T10:35:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Создана новая ветка", description)
        self.assertIn("feature/new-branch", description)
        self.assertIn("Сергей Сидоров", description)

    def test_push_delete_branch(self):
        """Тест события удаления ветки"""
        event = {
            "action_name": "pushed",
            "author": {"name": "Анна Кузнецова"},
            "push_data": {
                "ref": "refs/heads/old-branch",
                "action": "removed",
                "commit_count": 0
            },
            "created_at": "2025-10-06T10:40:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Ветка old-branch удалена", description)
        self.assertIn("Анна Кузнецова", description)

    def test_push_tag_created(self):
        """Тест события создания тега"""
        event = {
            "action_name": "pushed",
            "author": {"name": "Михаил Попов"},
            "push_data": {
                "ref": "refs/tags/v2.0.0",
                "action": "created",
                "commit_title": "Release version 2.0.0"
            },
            "created_at": "2025-10-06T10:45:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Создан тег v2.0.0", description)
        self.assertIn("Михаил Попов", description)
        self.assertIn("Release version 2.0.0", description)

    def test_push_tag_deleted(self):
        """Тест события удаления тега"""
        event = {
            "action_name": "pushed",
            "author": {"name": "Ольга Белова"},
            "push_data": {
                "ref": "refs/tags/old-version",
                "action": "removed",
                "commit_count": 0
            },
            "created_at": "2025-10-06T10:50:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Удален тег old-version", description)
        self.assertIn("Ольга Белова", description)


def run_new_events_tests():
    """Запустить все тесты новых событий"""
    print("🧪 Запуск тестов новых событий GitLab")
    print("=" * 50)
    
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestNewEvents))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результат
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ Все тесты новых событий пройдены!")
    else:
        print(f"❌ Тесты не пройдены: {len(result.failures)} ошибок, {len(result.errors)} сбоев")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_new_events_tests()