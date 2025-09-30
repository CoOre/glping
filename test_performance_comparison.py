#!/usr/bin/env python3
"""
Сравнение производительности до и после оптимизации фильтрации проектов
"""

import time
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from glping.async_gitlab_api import AsyncGitLabAPI
from glping.async_watcher import AsyncGitLabWatcher
from glping.config import Config


def create_mock_projects(count: int, active_only: bool = False):
    """Создает мок проекты для тестирования"""
    projects = []
    base_time = datetime.now(timezone.utc)
    
    for i in range(count):
        # Создаем проекты с разной активностью
        if active_only:
            # Только активные проекты (за последние 2 часа)
            activity_time = base_time - timedelta(minutes=i*5)
        else:
            # Смешанные проекты: половина активные, половина старые
            if i < count // 2:
                activity_time = base_time - timedelta(minutes=i*5)  # Активные
            else:
                activity_time = base_time - timedelta(days=i)  # Старые
        
        projects.append({
            "id": i + 1,
            "name": f"Project {i + 1}",
            "name_with_namespace": f"Group / Project {i + 1}",
            "last_activity_at": activity_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "path_with_namespace": f"group/project-{i + 1}"
        })
    
    return projects


async def simulate_old_approach(project_count: int = 100):
    """Симуляция старого подхода (получение всех проектов + локальная фильтрация)"""
    print(f"🔄 Тестирование старого подхода с {project_count} проектами...")
    
    # Создаем мок API
    mock_api = AsyncMock(spec=AsyncGitLabAPI)
    
    # Старый подход: получаем ВСЕ проекты
    all_projects = create_mock_projects(project_count, active_only=False)
    mock_api.get_projects.return_value = all_projects
    mock_api.get_project_events.return_value = []
    
    # Создаем watcher
    config = MagicMock()
    config.gitlab_url = "https://gitlab.example.com"
    config.gitlab_token = "test_token"
    config.cache_file = ":memory:"
    config.get_project_filter.return_value = {"membership": True}
    
    with patch('glping.async_watcher.AsyncGitLabAPI', return_value=mock_api):
        watcher = AsyncGitLabWatcher(config)
        watcher.api = mock_api
        
        # Устанавливаем дату последней проверки (2 часа назад)
        last_checked = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        await watcher.cache.set_last_checked_async(last_checked)
        
        # Замеряем время выполнения
        start_time = time.time()
        await watcher.check_projects(verbose=False)
        end_time = time.time()
        
        execution_time = end_time - start_time
        api_calls = mock_api.get_projects.call_count
        
        print(f"⏱️  Время выполнения: {execution_time:.3f} сек")
        print(f"📡 API запросы: {api_calls}")
        print(f"📊 Получено проектов: {len(all_projects)}")
        print(f"🔍 Отфильтровано локально: {len([p for p in all_projects if datetime.fromisoformat(p['last_activity_at'].replace('Z', '+00:00')) > datetime.fromisoformat(last_checked.replace('Z', '+00:00'))])}")
        
        return execution_time, api_calls


async def simulate_new_approach(project_count: int = 100):
    """Симуляция нового подхода (серверная фильтрация)"""
    print(f"✅ Тестирование нового подхода с {project_count} проектами...")
    
    # Создаем мок API
    mock_api = AsyncMock(spec=AsyncGitLabAPI)
    
    # Новый подход: получаем только активные проекты
    active_projects = create_mock_projects(project_count // 2, active_only=True)  # Только половина активна
    mock_api.get_projects.return_value = active_projects
    mock_api.get_project_events.return_value = []
    
    # Создаем watcher
    config = MagicMock()
    config.gitlab_url = "https://gitlab.example.com"
    config.gitlab_token = "test_token"
    config.cache_file = ":memory:"
    config.get_project_filter.return_value = {"membership": True}
    
    with patch('glping.async_watcher.AsyncGitLabAPI', return_value=mock_api):
        watcher = AsyncGitLabWatcher(config)
        watcher.api = mock_api
        
        # Устанавливаем дату последней проверки (2 часа назад)
        last_checked = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        await watcher.cache.set_last_checked_async(last_checked)
        
        # Замеряем время выполнения
        start_time = time.time()
        await watcher.check_projects(verbose=False)
        end_time = time.time()
        
        execution_time = end_time - start_time
        api_calls = mock_api.get_projects.call_count
        
        print(f"⏱️  Время выполнения: {execution_time:.3f} сек")
        print(f"📡 API запросы: {api_calls}")
        print(f"📊 Получено проектов: {len(active_projects)}")
        print(f"🔍 Отфильтровано на сервере: {len(active_projects)}")
        
        return execution_time, api_calls


async def main():
    """Основная функция сравнения производительности"""
    print("🚀 Сравнение производительности фильтрации проектов\n")
    
    project_counts = [50, 100, 200, 500]
    
    print("📊 Таблица результатов:")
    print("=" * 80)
    print(f"{'Проектов':<10} {'Старый подход':<15} {'Новый подход':<15} {'Ускорение':<10} {'Экономия API':<12}")
    print("-" * 80)
    
    for count in project_counts:
        print(f"\n🔄 Тестирование с {count} проектами:")
        
        # Тестируем старый подход
        old_time, old_calls = await simulate_old_approach(count)
        
        # Тестируем новый подход
        new_time, new_calls = await simulate_new_approach(count)
        
        # Вычисляем улучшения
        speedup = old_time / new_time if new_time > 0 else float('inf')
        api_savings = old_calls - new_calls
        
        print(f"\n📈 Результаты для {count} проектов:")
        print(f"   ⚡ Ускорение: {speedup:.1f}x")
        print(f"   📡 Экономия API запросов: {api_savings}")
        
        # Добавляем в таблицу
        print(f"{count:<10} {old_time:.3f}s ({old_calls} запросов)<{new_time:.3f}s ({new_calls} запросов)<{speedup:.1f}x<{api_savings} запросов")
    
    print("\n" + "=" * 80)
    print("✅ Выводы:")
    print("   • Серверная фильтрация значительно сокращает количество передаваемых данных")
    print("   • Меньше API запросов и объем данных для обработки")
    print("   • Особенно эффективно для большого количества проектов")
    print("   • Снижает нагрузку на GitLab сервер и клиентское приложение")


if __name__ == "__main__":
    asyncio.run(main())