#!/bin/bash

# Скрипт для остановки и очистки launchd для glping

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_FILE="com.glping.daemon.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_FILE"

echo "🛑 Остановка и очистка launchd для glping..."

# Останавливаем сервис
echo "▶️ Остановка сервиса com.glping.daemon"
launchctl stop com.glping.daemon 2>/dev/null || true

# Выгружаем сервис
echo "📤 Выгрузка сервиса"
launchctl unload "$TARGET_PLIST" 2>/dev/null || true

# Удаляем plist файл
echo "🗑️ Удаление plist файла"
if [ -f "$TARGET_PLIST" ]; then
    rm "$TARGET_PLIST"
    echo "✅ Файл $TARGET_PLIST удален"
else
    echo "ℹ️ Файл $TARGET_PLIST не найден"
fi

# Проверяем что сервис удален
echo "🔍 Проверка что сервис удален"
if launchctl list | grep -q "com.glping.daemon"; then
    echo "⚠️ Сервис все еще виден в списке, возможно потребуется перезагрузка"
    launchctl list | grep "com.glping.daemon"
else
    echo "✅ Сервис успешно удален"
fi

echo ""
echo "📝 Логи остаются в:"
echo "   - stdout: ~/glping/logs/glping.log"
echo "   - stderr: ~/glping/logs/glping.error.log"
echo ""
echo "🧹 Для полной очистки удалите директорию:"
echo "   rm -rf ~/glping"