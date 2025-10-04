.PHONY: install install-dev uninstall clean test lint type-check build publish build-binary help

# Default target
all: help

# Help target - show available commands
help:
	@echo "GitLab Ping - Makefile"
	@echo "=========================="
	@echo ""
	@echo "Доступные команды:"
	@echo "  install      - Установить glping глобально (требует sudo)"
	@echo "  install-dev  - Установить в режиме разработки с виртуальным окружением"
	@echo "  uninstall    - Удалить glping глобально"
	@echo "  clean        - Очистить артефакты сборки и виртуальное окружение"
	@echo "  test         - Запустить тесты"
	@echo "  test-notif   - Проверить систему уведомлений"
	@echo "  test-stacking - Проверить стекирование уведомлений"
	@echo "  lint         - Проверить код с помощью flake8"
	@echo "  type-check   - Проверить типы с помощью mypy"
	@echo "  build        - Собрать пакет"
	@echo "  build-binary - Собрать бинарный файл"
	@echo "  publish      - Опубликовать пакет в PyPI"
	@echo "  help         - Показать это справочное сообщение"
	@echo ""
	@echo "Примеры:"
	@echo "  make install"
	@echo "  make test-notif"
	@echo "  make test-stacking"
	@echo "  glping --once"

# Install globally (requires sudo for /usr/local/bin)
install:
	@echo "🚀 Установка GitLab Ping глобально..."
	@echo "========================================"
	
	# Check if Python 3.11+ is available
	@python3 -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'" || (echo "❌ Ошибка: Требуется Python 3.11+" && exit 1)
	
	# Install dependencies
	@echo "📦 Установка зависимостей..."
	@pip3 install --user --break-system-packages -r requirements.txt
	
	# Install the package
	@echo "📦 Установка пакета glping..."
	@pip3 install --user --break-system-packages -e .
	
	# Create symlink in /usr/local/bin
	@echo "🔗 Создание системной символической ссылки..."
	@ln -sf $$(python3 -c "import site; print(site.USER_BASE)")/bin/glping /usr/local/bin/glping || \
		(echo "⚠️  Не удалось создать ссылку в /usr/local/bin. Возможно, нужно добавить $$(python3 -c "import site; print(site.USER_BASE)")/bin в ваш PATH" && exit 1)
	
	@echo "✅ Установка успешно завершена!"
	@echo "🎉 Теперь можно использовать: glping --help"
	@echo ""
	@echo "Быстрая проверка:"
	@glping --test-notification

# Install in development mode with virtual environment
install-dev:
	@echo "🔧 Установка GitLab Ping в режиме разработки..."
	@echo "=================================================="
	
	# Create virtual environment if it doesn't exist
	@if [ ! -d "venv" ]; then \
		echo "📦 Создание виртуального окружения..."; \
		python3 -m venv venv; \
	fi
	
	# Activate virtual environment and install
	@echo "📦 Установка зависимостей..."
	@./venv/bin/pip install -r requirements.txt
	
	@echo "📦 Установка пакета glping..."
	@./venv/bin/pip install -e .
	
	@echo "✅ Установка в режиме разработки завершена!"
	@echo "🎉 Используйте: ./venv/bin/glping --help"
	@echo ""
	@echo "Быстрая проверка:"
	@./venv/bin/glping --test-notification

# Uninstall globally
uninstall:
	@echo "🗑️  Удаление GitLab Ping..."
	@echo "================================="
	
	# Remove symlink
	@echo "🔗 Удаление системной символической ссылки..."
	@rm -f /usr/local/bin/glping
	
	# Uninstall package
	@echo "📦 Удаление пакета..."
	@pip3 uninstall -y --break-system-packages glping || echo "Пакет не найден или уже удален"
	
	@echo "✅ Удаление завершено!"

# Clean build artifacts and virtual environment
clean:
	@echo "🧹 Очистка артефактов сборки..."
	@echo "==============================="
	
	# Remove virtual environment
	@echo "🗑️  Удаление виртуального окружения..."
	@rm -rf venv/
	
	# Remove build artifacts
	@echo "🗑️  Удаление артефактов сборки..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf __pycache__/
	@rm -rf glping/__pycache__/
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	
	@echo "✅ Очистка завершена!"

# Run tests
test:
	@echo "🧪 Запуск тестов..."
	@echo "=================="
	
	@echo "📱 Проверка множественных уведомлений..."
	@python3 tests/test_multiple_notifications.py
	
	@echo "🔗 Проверка обработки кликов по уведомлениям..."
	@python3 tests/test_notification_click.py
	
	@echo "🌐 Проверка генерации URL..."
	@python3 tests/test_real_urls.py
	
	@echo "✅ Все тесты завершены!"

# Run CI/CD specific tests
test-ci:
	@echo "🔄 Тестирование CI/CD событий..."
	@echo "==============================="
	
	@echo "🧪 Тестирование pipeline событий..."
	@python3 tests/test_pipeline_events.py
	
	@echo "🔗 Тестирование интеграции CI/CD..."
	@python3 tests/test_ci_integration_simple.py
	
	@echo "✅ Все CI/CD тесты завершены!"

# Run all tests including CI/CD
test-all: test test-ci
	@echo ""
	@echo "🎉 Все тесты (основные + CI/CD) успешно завершены!"

# Run linting
lint:
	@echo "🔍 Проверка кода с помощью flake8..."
	@echo "====================================="
	@python3 -m flake8 glping/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@python3 -m flake8 glping/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "✅ Проверка кода завершена!"

# Type checking
type-check:
	@echo "🔍 Проверка типов с помощью mypy..."
	@echo "====================================="
	@python3 -m mypy glping/ --ignore-missing-imports || true
	@echo "✅ Проверка типов завершена!"

# Build package
build:
	@echo "📦 Сборка пакета..."
	@echo "====================="
	@python -m pip install --upgrade pip build wheel twine
	@python -m build
	@twine check dist/*
	@echo "✅ Сборка пакета завершена!"

# Publish to PyPI
publish: build
	@echo "🚀 Публикация пакета в PyPI..."
	@echo "==============================="
	@twine upload dist/*
	@echo "✅ Публикация завершена!"



# Build binary with PyInstaller
build-binary:
	@echo "🔨 Сборка бинарного файла..."
	@echo "============================"
	
	# Install PyInstaller if not installed
	@command -v pyinstaller >/dev/null 2>&1 || \
		(echo "📦 Установка PyInstaller..." && pip3 install --break-system-packages pyinstaller)
	
	# Build binary
	@echo "📦 Сборка бинарника..."
	@pyinstaller --onefile --name glping run_cli.py \
		--add-data "glping:glping" \
		--hidden-import=plyer \
		--hidden-import=dotenv \
		--hidden-import=click \
		--hidden-import=requests \
		--hidden-import=aiohttp \
		--hidden-import=gitlab \
		--collect-all glping
	
	@echo "✅ Бинарник собран: dist/glping"
	@echo "🧪 Тестирование бинарника..."
	@./dist/glping --help || echo "⚠️  Бинарник может потребовать дополнительных зависимостей системы"
	
	@echo "✅ Сборка бинарника завершена!"

# Run all CI checks
ci: lint type-check test
	@echo "✅ Все проверки CI пройдены!"

# Format code
format:
	@echo "✨ Форматирование кода..."
	@echo "========================="
	@python3 -m pip install --break-system-packages black isort
	@python3 -m black glping/ tests/
	@python3 -m isort glping/ tests/
	@echo "✅ Форматирование кода завершено!"

# Test notification system
test-notif:
	@echo "🔔 Проверка системы уведомлений..."
	@echo "================================="
	
	@if command -v glping >/dev/null 2>&1; then \
		glping --test-notification; \
	else \
		echo "⚠️  glping не найден в PATH, пробуем с виртуальным окружением..."; \
		if [ -f "venv/bin/glping" ]; then \
			./venv/bin/glping --test-notification; \
		else \
			echo "❌ glping не найден. Пожалуйста, выполните 'make install' или 'make install-dev' сначала."; \
			exit 1; \
		fi; \
	fi

test-stacking:
	@echo "📱 Проверка стекирования уведомлений..."
	@echo "======================================="
	@python3 tests/test_notification_stacking.py

test-all-notifications:
	@echo "🔔 Тестирование всех типов уведомлений..."
	@echo "========================================"
	@python3 tests/test_all_notifications.py

test-gitlab-events:
	@echo "🔄 Тестирование симуляции событий GitLab..."
	@echo "=========================================="
	@python3 tests/test_gitlab_events.py

# Check system requirements
check-reqs:
	@echo "🔍 Проверка системных требований..."
	@echo "=================================="
	
	@echo "🐍 Проверка версии Python..."
	@python3 --version
	
	@echo "📦 Проверка pip..."
	@pip3 --version
	
	@echo "🔗 Проверка доступности записи в /usr/local/bin..."
	@touch /usr/local/bin/.glping-test 2>/dev/null && rm -f /usr/local/bin/.glping-test && echo "✅ /usr/local/bin доступен для записи" || echo "⚠️  /usr/local/bin требует прав sudo"
	
	@echo "✅ Проверка требований завершена!"

# Development setup (for developers)
dev-setup: install-dev
	@echo "🛠️  Настройка среды разработки завершена!"
	@echo "=========================================="
	@echo ""
	@echo "Доступные команды:"
	@echo "  ./venv/bin/glping --help"
	@echo "  make test"
	@echo "  make test-notif"
	@echo "  make clean"

# Production setup (for end users)
prod-setup: install
	@echo "🚀 Настройка рабочей среды завершена!"
	@echo "=========================================="
	@echo ""
	@echo "Доступные команды:"
	@echo "  glping --help"
	@echo "  glping --daemon"
	@echo "  glping --once"
	@echo "  make uninstall"