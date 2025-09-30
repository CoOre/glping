#!/bin/bash

# Скрипт для настройки launchd для glping

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="com.glping.daemon.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "🚀 Настройка launchd для glping..."

# Проверяем что plist файл существует
if [ ! -f "$SCRIPT_DIR/$PLIST_FILE" ]; then
    echo "❌ Файл $PLIST_FILE не найден в $SCRIPT_DIR"
    exit 1
fi

# Проверяем что glping установлен
if ! command -v glping &> /dev/null; then
    echo "❌ glping не найден. Сначала установите:"
    echo "   cd $SCRIPT_DIR && make prod-setup"
    exit 1
fi

# Создаем директории
mkdir -p "$LAUNCH_AGENTS_DIR"
mkdir -p "$HOME/glping/logs"

# Находим путь к glping
GLPING_PATH=$(command -v glping)
echo "🔍 Найден glping: $GLPING_PATH"

# Обновляем путь в plist файле
echo "📝 Обновление пути в plist файле"
sed "s|/Users/vladimirnosov/Downloads/glping/venv/bin/glping|$GLPING_PATH|g" "$SCRIPT_DIR/$PLIST_FILE" > "$TARGET_PLIST"

# plist файл уже скопирован с обновленным путем выше

# Проверяем синтаксис plist файла
echo "✅ Проверка синтаксиса plist файла"
plutil -lint "$TARGET_PLIST"

# Выгружаем если уже загружен
echo "🔄 Выгрузка существующего сервиса (если есть)"
launchctl unload "$TARGET_PLIST" 2>/dev/null || true

# Загружаем сервис
echo "📥 Загрузка сервиса"
launchctl load "$TARGET_PLIST"

# Запускаем сервис
echo "▶️ Запуск сервиса"
launchctl start com.glping.daemon

# Проверяем статус
echo "🔍 Проверка статуса сервиса"
sleep 2
if launchctl list | grep -q "com.glping.daemon"; then
    echo "✅ Сервис com.glping.daemon успешно запущен"
    echo ""
    echo "📊 Статус:"
    launchctl list | grep "com.glping.daemon"
    echo ""
    echo "📝 Логи будут доступны в:"
    echo "   - stdout: ~/glping/logs/glping.log"
    echo "   - stderr: ~/glping/logs/glping.error.log"
    echo ""
    echo "🛠️ Управление сервисом:"
    echo "   - Остановить: launchctl stop com.glping.daemon"
    echo "   - Перезапустить: launchctl kickstart -k gui/$(id -u)/com.glping.daemon"
    echo "   - Выгрузить: launchctl unload $TARGET_PLIST"
    echo "   - Посмотреть логи: tail -f ~/glping/logs/glping.log"
else
    echo "❌ Не удалось запустить сервис"
    echo "Проверьте логи: ~/glping/logs/glping.error.log"
    exit 1
fi