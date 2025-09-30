import asyncio
import time
from typing import Any, Dict, List, Optional

from .notifier import Notifier


class OptimizedNotifier:
    """Оптимизированный класс для отправки уведомлений с батчингом"""

    def __init__(self, batch_size: int = 5, batch_timeout: float = 10.0):
        """Инициализация оптимизированного нотификатора"""
        self.base_notifier = Notifier()
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self._pending_notifications = []
        self._last_batch_time = time.time()
        self._lock = asyncio.Lock()

    async def send_notification(
        self,
        title: str,
        message: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None,
    ):
        """Отправить уведомление с батчингом"""
        async with self._lock:
            notification = {
                "title": title,
                "message": message,
                "url": url,
                "icon_url": icon_url,
                "timestamp": time.time(),
            }

            self._pending_notifications.append(notification)

            # Проверяем, нужно ли отправить батч
            if (
                len(self._pending_notifications) >= self.batch_size
                or time.time() - self._last_batch_time >= self.batch_timeout
            ):
                await self._flush_batch()

    async def _flush_batch(self):
        """Отправить накопленные уведомления"""
        if not self._pending_notifications:
            return

        notifications = self._pending_notifications.copy()
        self._pending_notifications.clear()
        self._last_batch_time = time.time()

        # Если одно уведомление - отправляем как обычно
        if len(notifications) == 1:
            notif = notifications[0]
            await asyncio.to_thread(
                self.base_notifier.send_notification,
                notif["title"],
                notif["message"],
                notif["url"],
                notif["icon_url"],
            )
            return

        # Если несколько уведомлений - группируем
        await self._send_batch_notification(notifications)

    async def _send_batch_notification(self, notifications: List[Dict[str, Any]]):
        """Отправить групповое уведомление"""
        # Группируем по проектам
        project_groups = {}
        for notif in notifications:
            project_name = notif["title"]
            if project_name not in project_groups:
                project_groups[project_name] = []
            project_groups[project_name].append(notif)

        # Отправляем уведомления по проектам
        for project_name, project_notifs in project_groups.items():
            if len(project_notifs) == 1:
                # Одно уведомление для проекта
                notif = project_notifs[0]
                await asyncio.to_thread(
                    self.base_notifier.send_notification,
                    notif["title"],
                    notif["message"],
                    notif["url"],
                    notif["icon_url"],
                )
            else:
                # Несколько уведомлений для проекта - группируем
                messages = [n["message"] for n in project_notifs]
                summary = f"Новых событий: {len(project_notifs)}"

                # Берем URL из последнего уведомления
                last_url = project_notifs[-1]["url"]

                await asyncio.to_thread(
                    self.base_notifier.send_notification,
                    title=f"События GitLab - {project_name}",
                    message=summary,
                    url=last_url,
                    icon_url="https://gitlab.com/assets/favicon-72a2cad5025aa931d6ea56c3201d1f18e8951c71e3363e712a476bead75f0a83.png",
                )

                # Выводим детали в консоль
                for msg in messages:
                    print(f"  - {msg}")

    async def force_flush(self):
        """Принудительно отправить все накопленные уведомления"""
        async with self._lock:
            await self._flush_batch()

    def test_notification(self):
        """Отправить тестовое уведомление"""
        self.base_notifier.test_notification()
