#!/usr/bin/env python3

import os
import sys
import unittest

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from glping.utils.event_utils import get_event_description


class TestProjectManagementEvents(unittest.TestCase):
    """Тестирование событий управления проектом"""

    def test_release_created_event(self):
        """Тест события создания релиза"""
        event = {
            "target_type": "Release",
            "action_name": "created",
            "author": {"name": "Анна Смирнова"},
            "data": {"tag": "v1.0.0", "name": "Release v1.0.0"},
            "created_at": "2025-10-06T10:00:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Создан релиз", description)
        self.assertIn("Анна Смирнова", description)
        self.assertIn("v1.0.0", description)

    def test_release_updated_event(self):
        """Тест события обновления релиза"""
        event = {
            "target_type": "Release",
            "action_name": "updated",
            "author": {"name": "Михаил Козлов"},
            "data": {"tag": "v1.0.1", "name": "Release v1.0.1"},
            "created_at": "2025-10-06T10:05:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Релиз обновлен", description)
        self.assertIn("Михаил Козлов", description)
        self.assertIn("v1.0.1", description)

    def test_release_deleted_event(self):
        """Тест события удаления релиза"""
        event = {
            "target_type": "Release",
            "action_name": "deleted",
            "author": {"name": "Елена Петрова"},
            "data": {"tag": "v1.0.0"},
            "created_at": "2025-10-06T10:10:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Релиз удален", description)
        self.assertIn("Елена Петрова", description)
        self.assertIn("v1.0.0", description)

    def test_wiki_page_created_event(self):
        """Тест события создания wiki страницы"""
        event = {
            "target_type": "WikiPage",
            "action_name": "created",
            "author": {"name": "Дмитрий Иванов"},
            "data": {"title": "Getting Started", "slug": "getting-started"},
            "created_at": "2025-10-06T10:15:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Создана wiki страница", description)
        self.assertIn("Дмитрий Иванов", description)
        self.assertIn("Getting Started", description)

    def test_wiki_page_updated_event(self):
        """Тест события обновления wiki страницы"""
        event = {
            "target_type": "WikiPage",
            "action_name": "updated",
            "author": {"name": "Ольга Сидорова"},
            "data": {"title": "Installation Guide", "slug": "installation-guide"},
            "created_at": "2025-10-06T10:20:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Wiki страница обновлена", description)
        self.assertIn("Ольга Сидорова", description)
        self.assertIn("Installation Guide", description)

    def test_wiki_page_deleted_event(self):
        """Тест события удаления wiki страницы"""
        event = {
            "target_type": "WikiPage",
            "action_name": "deleted",
            "author": {"name": "Павел Новиков"},
            "data": {"title": "Old Documentation", "slug": "old-documentation"},
            "created_at": "2025-10-06T10:25:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Wiki страница удалена", description)
        self.assertIn("Павел Новиков", description)
        self.assertIn("Old Documentation", description)

    def test_tag_created_event(self):
        """Тест события создания тега"""
        event = {
            "target_type": "TagPush",
            "action_name": "created",
            "author": {"name": "Мария Волкова"},
            "push_data": {"ref": "refs/tags/v2.0.0"},
            "created_at": "2025-10-06T10:30:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Тег v2.0.0", description)
        self.assertIn("Мария Волкова", description)

    def test_tag_deleted_event(self):
        """Тест события удаления тега"""
        event = {
            "target_type": "TagPush",
            "action_name": "removed",
            "author": {"name": "Алексей Соколов"},
            "push_data": {"ref": "refs/tags/old-version"},
            "created_at": "2025-10-06T10:35:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Тег old-version", description)
        self.assertIn("Алексей Соколов", description)

    def test_member_added_event(self):
        """Тест события добавления участника"""
        event = {
            "target_type": "Member",
            "action_name": "added",
            "author": {"name": "Ирина Кузнецова"},
            "data": {"user_name": "Новый Пользователь", "access_level": "Developer"},
            "created_at": "2025-10-06T10:40:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Добавлен участник", description)
        self.assertIn("Ирина Кузнецова", description)
        self.assertIn("Новый Пользователь", description)
        self.assertIn("Developer", description)

    def test_member_removed_event(self):
        """Тест события удаления участника"""
        event = {
            "target_type": "Member",
            "action_name": "removed",
            "author": {"name": "Сергей Попов"},
            "data": {"user_name": "Старый Пользователь", "access_level": "Reporter"},
            "created_at": "2025-10-06T10:45:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Удален участник", description)
        self.assertIn("Сергей Попов", description)
        self.assertIn("Старый Пользователь", description)

    def test_member_updated_event(self):
        """Тест события обновления участника"""
        event = {
            "target_type": "Member",
            "action_name": "updated",
            "author": {"name": "Татьяна Белова"},
            "data": {"user_name": "Повышенный Пользователь", "access_level": "Maintainer"},
            "created_at": "2025-10-06T10:50:00Z"
        }
        
        description = get_event_description(event)
        self.assertIn("Изменены права участника", description)
        self.assertIn("Татьяна Белова", description)
        self.assertIn("Повышенный Пользователь", description)
        self.assertIn("Maintainer", description)


if __name__ == "__main__":
    unittest.main()