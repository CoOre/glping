#!/usr/bin/env python3

import asyncio
import sys

import click

from .config import Config
from .watcher import GitLabWatcher
from .lock import process_lock


def _handle_test_operations(test_notification, test_stacking, reset_cache, reset_installation_date, config):
    """Обработка тестовых операций, не требующих подключения к GitLab"""
    if test_notification:
        from .notifier import Notifier
        notifier = Notifier()
        notifier.test_notification()
        return True
    
    if test_stacking:
        import os
        
        # Add the parent directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from tests.test_notification_stacking import test_notification_stacking
        
        test_notification_stacking()
        return True
    
    if reset_cache:
        from .cache import Cache
        cache = Cache(config.cache_file)
        cache.reset()
        print("Кеш успешно очищен")
        return True
    
    if reset_installation_date:
        from .cache import Cache
        cache = Cache(config.cache_file)
        cache.reset_installation_date()
        return True
    
    return False


@click.command()
@click.option("--once", is_flag=True, help="Однократный запуск")
@click.option("--daemon", is_flag=True, help="Запуск в режиме демона")
@click.option(
    "--interval", type=int, help="Интервал проверки в секундах (переопределяет .env)"
)
@click.option("--verbose", is_flag=True, help="Детализированное логирование")
@click.option("--reset-cache", is_flag=True, help="Очистить кеш")
@click.option("--project", type=int, help="Отслеживать только указанный проект")
@click.option("--test-notification", is_flag=True, help="Тестовое уведомление")
@click.option("--test-stacking", is_flag=True, help="Тест стекирования уведомлений")
@click.option(
    "--async",
    "use_async",
    is_flag=True,
    help="Использовать асинхронный режим (быстрее)",
)
@click.option(
    "--optimized", is_flag=True, help="Использовать оптимизированные уведомления"
)
@click.option(
    "--reset-installation-date",
    is_flag=True,
    help="Сбросить дату последней проверки на начало сегодняшних суток",
)
def main(
    once,
    daemon,
    interval,
    verbose,
    reset_cache,
    project,
    test_notification,
    test_stacking,
    use_async,
    optimized,
    reset_installation_date,
):
    """CLI-утилита для отслеживания событий в GitLab"""
    
    # Сначала обрабатываем операции, не требующие блокировки
    try:
        config = Config()
        
        if project:
            config.set_project_id(project)
        
        if interval:
            config.check_interval = interval
        
        # Обработка тестовых операций
        if _handle_test_operations(test_notification, test_stacking, reset_cache, reset_installation_date, config):
            return
            
    except ValueError as e:
        click.echo(f"Ошибка конфигурации: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nПрервано пользователем")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Неожиданная ошибка: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Основные операции требуют блокировки процесса
    with process_lock("glping") as locked:
        if not locked:
            click.echo("Процесс уже запущен. Пропуск выполнения.")
            sys.exit(0)
        
        try:
            # Операции, требующие подключения к GitLab
            if use_async:
                from .async_watcher import AsyncGitLabWatcher
                watcher = AsyncGitLabWatcher(config)
                print("🚀 Используется асинхронный режим для ускорения работы")
            else:
                watcher = GitLabWatcher(config)

            # Если включена оптимизация, заменяем notifier
            if optimized and not use_async:
                from .optimized_notifier import OptimizedNotifier
                watcher.notifier = OptimizedNotifier()
                print("⚡ Используются оптимизированные уведомления с батчингом")

            if once and daemon:
                click.echo("Ошибка: нельзя использовать одновременно --once и --daemon")
                sys.exit(1)

            if not once and not daemon:
                daemon = True

            if once:
                if use_async:
                    success = asyncio.run(watcher.run_once(verbose))
                else:
                    success = watcher.run_once(verbose)
                sys.exit(0 if success else 1)
            elif daemon:
                if use_async:
                    success = asyncio.run(watcher.run_daemon(verbose))
                else:
                    success = watcher.run_daemon(verbose)
                sys.exit(0 if success else 1)

        except ValueError as e:
            click.echo(f"Ошибка конфигурации: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            click.echo("\nПрервано пользователем")
            sys.exit(0)
        except Exception as e:
            click.echo(f"Неожиданная ошибка: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
