import os
import sys
import tempfile
import platform
from typing import Optional, ContextManager
from contextlib import contextmanager

# Кроссплатформенный импорт fcntl
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    # Windows не поддерживает fcntl
    HAS_FCNTL = False


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
            
            # На Windows используем простой механизм через файл
            if not HAS_FCNTL:
                # Проверяем существует ли файл блокировки
                if os.path.exists(self.lock_path):
                    # Проверяем актуальность PID
                    try:
                        with open(self.lock_path, 'r') as f:
                            pid = int(f.read().strip())
                        # Проверяем жив ли процесс
                        if self._is_process_running(pid):
                            return False
                    except (ValueError, FileNotFoundError):
                        pass
                
                # Создаем новый файл блокировки
                self.lock_file = open(self.lock_path, 'w')
                self.lock_file.write(str(os.getpid()))
                self.lock_file.flush()
                return True
            
            # На Unix системах используем fcntl
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
                if HAS_FCNTL:
                    fcntl.flock(self.lock_file, fcntl.LOCK_UN)
                self.lock_file.close()
                self.lock_file = None
                
                # Удаляем файл блокировки
                if self.lock_path and os.path.exists(self.lock_path):
                    os.unlink(self.lock_path)
            except Exception:
                pass  # Игнорируем ошибки при освобождении
    
    def _is_process_running(self, pid: int) -> bool:
        """Проверить, запущен ли процесс с указанным PID (кроссплатформенно)"""
        try:
            if platform.system() == "Windows":
                # На Windows проверяем через tasklist или psutil если доступен
                try:
                    import psutil
                    return psutil.pid_exists(pid)
                except ImportError:
                    # Резервный метод для Windows без psutil
                    import subprocess
                    result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                          capture_output=True, text=True)
                    return str(pid) in result.stdout
            else:
                # Unix системы
                os.kill(pid, 0)
                return True
        except (OSError, ImportError, ProcessLookupError, subprocess.SubprocessError):
            return False
    
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
            
            if not HAS_FCNTL:
                # На Windows проверяем PID
                with open(self.lock_path, 'r') as f:
                    try:
                        pid = int(f.read().strip())
                        return self._is_process_running(pid)
                    except (ValueError, FileNotFoundError):
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