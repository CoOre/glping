import os
import sys
import fcntl
import tempfile
from typing import Optional, ContextManager
from contextlib import contextmanager


class ProcessLock:
    """Механизм блокировки для предотвращения двойного запуска"""
    
    def __init__(self, lock_name: str = "glping"):
        self.lock_name = lock_name
        self.lock_file: Optional[int] = None
        self.lock_path: Optional[str] = None
        
    def acquire(self) -> bool:
        """Попытаться получить блокировку. Возвращает True если успешно"""
        try:
            # Создаем временный файл для блокировки
            temp_dir = tempfile.gettempdir()
            self.lock_path = os.path.join(temp_dir, f"{self.lock_name}.lock")
            
            # Открываем файл для блокировки
            self.lock_file = open(self.lock_path, 'w')
            
            # Пытаемся получить эксклюзивную блокировку
            fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Записываем PID текущего процесса
            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()
            
            return True
            
        except (IOError, BlockingIOError):
            # Не удалось получить блокировку - процесс уже запущен
            if self.lock_file:
                self.lock_file.close()
                self.lock_file = None
            return False
        except Exception:
            # Другая ошибка
            if self.lock_file:
                self.lock_file.close()
                self.lock_file = None
            return False
    
    def release(self):
        """Освободить блокировку"""
        if self.lock_file:
            try:
                fcntl.flock(self.lock_file, fcntl.LOCK_UN)
                self.lock_file.close()
                self.lock_file = None
                
                # Удаляем файл блокировки
                if self.lock_path and os.path.exists(self.lock_path):
                    os.unlink(self.lock_path)
            except Exception:
                pass  # Игнорируем ошибки при освобождении
    
    def __enter__(self):
        """Контекстный менеджер - вход"""
        return self.acquire()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        self.release()
    
    def is_locked(self) -> bool:
        """Проверить, заблокирован ли процесс"""
        if not self.lock_path:
            temp_dir = tempfile.gettempdir()
            self.lock_path = os.path.join(temp_dir, f"{self.lock_name}.lock")
        
        try:
            if not os.path.exists(self.lock_path):
                return False
                
            # Пытаемся получить блокировку для проверки
            with open(self.lock_path, 'r') as f:
                try:
                    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    # Если получили блокировку, значит процесс не запущен
                    fcntl.flock(f, fcntl.LOCK_UN)
                    return False
                except (IOError, BlockingIOError):
                    # Не удалось получить блокировку - процесс запущен
                    return True
        except Exception:
            return False


@contextmanager
def process_lock(lock_name: str = "glping") -> ContextManager[bool]:
    """Контекстный менеджер для блокировки процесса"""
    lock = ProcessLock(lock_name)
    acquired = lock.acquire()
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()