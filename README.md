# GitLab Ping

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/coore/glping)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/CoOre?color=ff69b4)](https://github.com/sponsors/CoOre)

CLI-утилита для отслеживания событий в GitLab с push-уведомлениями.

## Функциональность

- Отслеживание событий во всех проектах GitLab
- Поддержка коммитов, Merge Requests, Issues, Pipeline и комментариев
- Кроссплатформенные push-уведомления с правильным стекированием
- Работа в режиме демона или однократный запуск
- Унифицированная система кэширования для предотвращения дублирования уведомлений
- Асинхронный режим для улучшенной производительности

## Установка

### Требования
- Python 3.11+
- GitLab personal access token

### Быстрая установка с помощью Makefile

**Для конечных пользователей:**
```bash
git clone https://github.com/CoOre/glping.git
cd glping
make prod-setup
```

**Для разработчиков:**
```bash
git clone https://github.com/CoOre/glping.git
cd glping
make dev-setup
```

### Ручная установка

```bash
git clone https://github.com/CoOre/glping.git
cd glping
pip install -e .
```

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Установка бинарника
```bash
# Установка пакета в системную директорию
pip install -e .
```

### Установка для macOS (рекомендуется)

Для правильной работы уведомлений на macOS установите `terminal-notifier`:

```bash
# Через Homebrew
brew install terminal-notifier

# Или вручную
curl -L https://github.com/julienXX/terminal-notifier/releases/download/2.0.0/terminal-notifier-2.0.0.zip -o terminal-notifier.zip
unzip terminal-notifier.zip
sudo cp terminal-notifier-2.0.0/terminal-notifier.app/Contents/MacOS/terminal-notifier /usr/local/bin/
```

## Конфигурация

1. Скопируйте файл конфигурации:
```bash
cp .env.example .env
```

2. Отредактируйте `.env` файл:
```env
GITLAB_URL=https://gitlab.example.com
GITLAB_TOKEN=your_private_token_here
CHECK_INTERVAL=60
CACHE_FILE=glping_cache.json
```

3. Создайте GitLab personal access token:
   - Перейдите в Settings → Access Tokens
   - Создайте токен с правами `read_api` и `read_repository`

## Использование

### Основные команды

```bash
# Запуск в режиме демона (по умолчанию)
glping

# Однократная проверка
glping --once

# Запуск с детальным логированием
glping --verbose

# Изменить интервал проверки
glping --interval 120

# Отслеживать только конкретный проект
glping --project 12345

# Сбросить кеш
glping --reset-cache

# Тестовое уведомление
glping --test-notification

# Тест стекирования уведомлений
glping --test-stacking
```

### Примеры использования

```bash
# Мониторинг всех проектов с интервалом 30 секунд
glping --daemon --interval 30 --verbose

# Проверка конкретного проекта один раз
glping --once --project 12345 --verbose

# Тестирование уведомлений
glping --test-notification

# Тестирование стекирования уведомлений
glping --test-stacking
```

### Автоматический запуск

#### Рекомендуемый способ: launchd (macOS)

Для macOS рекомендуется использовать встроенную систему launchd вместо crontab:

```bash
# Быстрая настройка
./launchd_setup.sh

# Проверить статус
launchctl list | grep glping

# Посмотреть логи
tail -f ~/glping/logs/glping.log
```

**Преимущества launchd:**
- ✅ Идеальные уведомления без "редактора скриптов"
- ✅ Автоматический перезапуск при сбоях
- ✅ Встроенное логирование
- ✅ Нативный для macOS

#### Альтернатива: crontab

Для использования в crontab указывайте полный путь к команде:

```bash
# Редактирование crontab
crontab -e

# Добавить строку (используйте полный путь):
* * * * * /usr/local/bin/glping --async --optimized --once --verbose >> ~/glping.log 2>&1
```

**Важно:** crontab использует ограниченное окружение, поэтому уведомления могут появляться "от редактора скриптов". Для правильных уведомлений используйте launchd.

### Управление сервисом (launchd)

```bash
# Запустить сервис
launchctl start com.glping.daemon

# Остановить сервис
launchctl stop com.glping.daemon

# Перезапустить сервис
launchctl kickstart -k gui/$(id -u)/com.glping.daemon

# Удалить сервис
./launchd_cleanup.sh

# Просмотр логов
tail -f ~/glping/logs/glping.log
tail -f ~/glping/logs/glping.error.log
```

### Использование Makefile

Makefile предоставляет удобные скрипты для установки и управления:

```bash
# Показать доступные команды
make help

# Проверить системные требования
make check-reqs

# Установка для конечных пользователей
make prod-setup

# Установка для разработчиков
make dev-setup

# Запустить все тесты
make test

# Тестировать уведомления
make test-notif

# Тестировать стекирования уведомлений
make test-stacking

# Удалить приложение
make uninstall

# Очистить артефакты сборки
make clean
```

## Поддерживаемые события

- **Коммиты** - новые коммиты и сообщения
- **Merge Requests** - создание, обновление, комментарии, закрытие, мёрдж
- **Issues** - создание, комментарии, закрытие, reopen
- **Pipeline** - успешное выполнение и падение
- **Комментарии** - ко всем сатегориям сущностей

## Архитектура

```
glping/
├── __init__.py      # Пакетная информация
├── main.py          # Точка входа CLI
├── config.py        # Конфигурация из .env
├── cache.py         # Унифицированная система кэширования
├── gitlab_api.py    # Обёртка для GitLab API
├── async_gitlab_api.py # Асинхронная обёртка для GitLab API
├── notifier.py      # Push-уведомления с поддержкой стекирования и cron detection
├── optimized_notifier.py # Оптимизированные уведомления
├── watcher.py       # Основная логика
├── async_watcher.py # Асинхронная основная логика
├── requirements.txt # Зависимости
├── setup.py         # Установка пакета
├── pyproject.toml   # Современная конфигурация проекта
├── .env.example     # Пример конфигурации
├── com.glping.daemon.plist # launchd конфигурация для macOS
├── launchd_setup.sh # Скрипт настройки launchd
├── launchd_cleanup.sh # Скрипт очистки launchd
└── ~/glping/logs/   # Директория для логов launchd в домашней директории
```

## Кэширование

Утилита использует унифицированный JSON файл (`glping_cache.json`) для хранения:
- Метаданных (дата установки, время последней проверки)
- ID последнего обработанного события для каждого проекта
- Времени последней активности проектов

Это предотвращает дублирование уведомлений и позволяет отслеживать только новые события. Система автоматически мигрирует данные из старых форматов кэша.

## Уведомления

Поддерживаются кроссплатформенные уведомления:
- **macOS** - системные уведомления с правильным стекированием через terminal-notifier
- **Linux** - notify2/libnotify с автоматическим определением DISPLAY
- **Windows** - win10toast

### Особенности реализации:
- **Стекирование уведомлений** на macOS - все уведомления остаются видимыми
- **Уникальные группы** для каждого уведомления предотвращают замену
- **Поддержка URL** - при клике на уведомление открывается соответствующая страница в GitLab
- **Кроссплатформенность** - единый API для всех операционных систем
- **Умное определение окружения** - автоматически адаптируется для cron/launchd
- **Оптимизация для macOS** - в cron окружении использует Finder вместо Terminal

### Устранение неполадок с уведомлениями

#### macOS: уведомления "от редактора скриптов"
Используйте launchd вместо crontab:
```bash
./launchd_setup.sh
```

#### Linux: нет уведомлений в cron
Убедитесь что установлен notify2:
```bash
pip install notify2
sudo apt-get install libnotify-bin
```

## Разработка

### Запуск в режиме разработки
```bash
python -m glping.main --once --verbose
```

### Тестирование
```bash
# Тестирование уведомлений
python -m glping.main --test-notification

# Тестирование стекирования уведомлений
python tests/test_notification_stacking.py

# Тестирование подключения
python -m glping.main --once --verbose

# Запуск всех тестов
make test
```

## Лицензия

MIT License - Copyright (c) 2025 Vladimir Nosov

## Управление сервисом

### Остановка и удаление launchd
```bash
./launchd_cleanup.sh
```

### Переход с crontab на launchd
```bash
# 1. Сохраните текущую crontab
crontab -l > crontab_backup.txt

# 2. Удалите glping из crontab
crontab -e
# Удалите строку с glping

# 3. Настройте launchd
./launchd_setup.sh

# 4. Проверьте работу
tail -f ~/glping/logs/glping.log
```

## Автор

Vladimir Nosov <inosovvv@gmail.com>

## Репозиторий

https://github.com/CoOre/glping

## Дополнительная документация

- [LAUNCHD_SETUP.md](LAUNCHD_SETUP.md) - Подробная инструкция по настройке launchd
- [DEVELOPMENT.md](DEVELOPMENT.md) - Руководство для разработчиков
- [CONTRIBUTING.md](CONTRIBUTING.md) - Как внести вклад в проект