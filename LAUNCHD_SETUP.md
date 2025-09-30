# Настройка glping с launchd (рекомендуется для macOS)

## Почему launchd лучше crontab?

- ✅ **Нативный для macOS** - встроенная система управления сервисами
- ✅ **Идеальные уведомления** - правильное GUI окружение
- ✅ **Автоматический перезапуск** - при сбоях сервис перезапустится
- ✅ **Встроенное логирование** - stdout и stderr в файлы
- ✅ **Управление процессом** - запуск, остановка, перезапуск

## Быстрая настройка

### 1. Запустите скрипт настройки:
```bash
./launchd_setup.sh
```

Скрипт автоматически:
- Скопирует plist файл в `~/Library/LaunchAgents/`
- Проверит синтаксис
- Загрузит и запустит сервис

### 2. Проверьте работу:
```bash
# Проверить статус
launchctl list | grep glping

# Посмотреть логи
tail -f logs/glping.log
```

## Ручная настройка

Если хотите настроить вручную:

### 1. Скопируйте plist файл:
```bash
cp com.glping.daemon.plist ~/Library/LaunchAgents/
```

### 2. Загрузите сервис:
```bash
launchctl load ~/Library/LaunchAgents/com.glping.daemon.plist
```

### 3. Запустите сервис:
```bash
launchctl start com.glping.daemon
```

## Управление сервисом

### Запуск/Остановка:
```bash
# Запустить
launchctl start com.glping.daemon

# Остановить
launchctl stop com.glping.daemon

# Перезапустить
launchctl kickstart -k gui/$(id -u)/com.glping.daemon
```

### Просмотр логов:
```bash
# Стандартный вывод
tail -f logs/glping.log

# Ошибки
tail -f logs/glping.error.log

# Оба сразу
tail -f logs/glping.log logs/glping.error.log
```

### Удаление сервиса:
```bash
# Используйте скрипт очистки
./launchd_cleanup.sh

# Или вручную:
launchctl stop com.glping.daemon
launchctl unload ~/Library/LaunchAgents/com.glping.daemon.plist
rm ~/Library/LaunchAgents/com.glping.daemon.plist
```

## Настройка параметров

### Изменение интервала проверки:
Откройте `com.glping.daemon.plist` и измените:
```xml
<key>StartInterval</key>
<integer>300</integer> <!-- секунд (300 = 5 минут) -->
```

### Изменение пути к Python:
Если Python в другой директории:
```xml
<key>ProgramArguments</key>
<array>
    <string>/path/to/your/python3</string>
    <string>/Users/vladimirnosov/Downloads/glping/glping/main.py</string>
</array>
```

## Преимущества над crontab

| Параметр | launchd | crontab |
|----------|---------|---------|
| Уведомления | ✅ Идеальные | ❌ "От редактора скриптов" |
| Автозапуск | ✅ | ✅ |
| Перезапуск | ✅ Автоматический | ❌ Ручной |
| Логирование | ✅ Встроенное | ❌ Требует настройки |
| Управление | ✅ Простое | ✅ Простое |
| macOS нативность | ✅ | ❌ Unix унаследованный |

## Troubleshooting

### Сервис не запускается:
```bash
# Проверьте синтаксис plist
plutil -lint ~/Library/LaunchAgents/com.glping.daemon.plist

# Посмотрите ошибки
cat logs/glping.error.log
```

### Уведомления не приходят:
```bash
# Проверьте что terminal-notifier установлен
which terminal-notifier

# Проверьте логи на ошибки уведомлений
grep -i "notification" logs/glping.log
```

### Сервис не виден:
```bash
# Проверьте что plist в правильной директории
ls -la ~/Library/LaunchAgents/com.glping.daemon.plist

# Проверьте что сервис загружен
launchctl list | grep glping
```

## Переход с crontab

1. **Сохраните текущую crontab:**
   ```bash
   crontab -l > crontab_backup.txt
   ```

2. **Удалите glping из crontab:**
   ```bash
   crontab -e
   # Удалите строку с glping
   ```

3. **Настройте launchd:**
   ```bash
   ./launchd_setup.sh
   ```

4. **Проверьте работу:**
   ```bash
   tail -f logs/glping.log
   ```

Теперь glping будет работать с идеальными уведомлениями macOS! 🎉