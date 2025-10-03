# Development Guide

This guide provides detailed information for developers working on GitLab Ping.

## Development Environment Setup

### Prerequisites
- Python 3.11 or higher
- Git
- Docker (optional)
- Make

### Quick Start
```bash
# Clone the repository
git clone https://github.com/CoOre/glping.git
cd glping

# Set up development environment
make dev-setup

# Run tests
make test

# Start development server
python -m glping --dev
```

## Project Structure

```
glping/
├── glping/                    # Main application package
│   ├── __init__.py           # Package initialization and version
│   ├── main.py               # Entry point and CLI
│   ├── base_gitlab_api.py    # Base GitLab API client
│   ├── base_watcher.py       # Base event watcher
│   ├── gitlab_api.py         # Synchronous GitLab API client
│   ├── async_gitlab_api.py   # Asynchronous GitLab API client
│   ├── watcher.py            # Synchronous event watcher
│   ├── async_watcher.py      # Asynchronous event watcher
│   ├── notifier.py           # Desktop notifications
│   ├── optimized_notifier.py # Optimized notification system
│   ├── cache.py              # Cache management
│   ├── config.py             # Configuration management
│   ├── lock.py               # File locking utilities
│   ├── assets/               # Application assets
│   │   ├── glping-icon.png   # Main icon
│   │   ├── glping-icon-128.png # 128px icon
│   │   └── glping-icon-256.png # 256px icon
│   └── utils/                # Utility functions
│       ├── __init__.py       # Utilities package initialization
│       ├── date_utils.py     # Date and time utilities
│       ├── event_utils.py    # Event processing utilities
│       └── url_utils.py      # URL handling utilities
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_gitlab_events.py
│   ├── test_notifications.py
│   ├── test_cache_critical.py
│   ├── test_config_validation.py
│   ├── test_cron_detection.py
│   ├── test_multiple_notifications.py
│   ├── test_notification_click.py
│   ├── test_notification_stacking.py
│   ├── test_optimized_filtering.py
│   ├── test_performance_comparison.py
│   ├── test_real_multiple_events.py
│   ├── test_real_urls.py
│   ├── test_url_comparison.py
│   └── test_all_notifications.py
├── docs/                     # Documentation
├── docker/                   # Docker files
├── scripts/                  # Utility scripts
├── config.example.yaml       # Example configuration
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Development dependencies
├── setup.py                  # Package setup
├── Makefile                  # Common tasks
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

## Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# Write tests
# Update documentation

# Run tests and linting
make test
make lint

# Commit changes
git add .
git commit -m "feat: add your feature description"

# Push to fork
git push origin feature/your-feature-name

# Create pull request
```

### 2. Bug Fixing
```bash
# Create bug fix branch
git checkout -b fix/bug-description

# Make minimal changes to fix the bug
# Add tests to prevent regression

# Run tests
make test

# Commit changes
git add .
git commit -m "fix: describe the bug fix"

# Push and create PR
```

### 3. Code Review Process
1. **Self-Review**: Review your own code before submitting
2. **Automated Checks**: Ensure all CI checks pass
3. **Peer Review**: Address reviewer comments
4. **Final Review**: Merge after approval

## Testing

### Test Structure
- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Platform Tests**: Test OS-specific functionality

### Running Tests
```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
python -m pytest tests/test_notifier.py

# Run with verbose output
python -m pytest -v

# Run specific test category
python -m pytest -m "unit"
python -m pytest -m "integration"
```

### Writing Tests
```python
import pytest
from unittest.mock import Mock, patch
from glping.notifier import Notifier

class TestNotifier:
    def setup_method(self):
        self.notifier = Notifier()
    
    def test_notification_creation(self):
        """Test that notifications are created correctly"""
        result = self.notifier.send_notification(
            title="Test Title",
            message="Test Message"
        )
        assert result is True
    
    @patch('glping.notifier.platform.system')
    def test_platform_detection(self, mock_system):
        """Test platform detection logic"""
        mock_system.return_value = 'Darwin'
        notifier = Notifier()
        assert notifier.platform == 'macos'
```

### Test Coverage
- Aim for 80%+ coverage
- Focus on critical paths
- Test both success and error cases
- Use mocking for external dependencies

## Code Quality

### Linting and Formatting
```bash
# Run linting
make lint

# Format code
make format

# Check formatting
make format-check

# Run all quality checks
make quality
```

### Code Style Guidelines
- Follow PEP 8
- Use Black for formatting
- Use isort for import sorting
- Use flake8 for linting
- Use mypy for type checking

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Configuration

### Development Configuration
```yaml
# config.dev.yaml
gitlab:
  url: "https://gitlab.example.com"
  token: "dev-token"
  
monitoring:
  interval: 10  # Faster polling for development
  max_events: 50
  
notifications:
  enabled: true
  sound: false  # Disable sound in development
  
web:
  enabled: true
  port: 8080
  debug: true
```

### Environment Variables
```bash
# Development environment
export GLPING_CONFIG_PATH="config.dev.yaml"
export GLPING_LOG_LEVEL="DEBUG"
export GLPING_DEV_MODE="true"
```

## Debugging

### Logging Configuration
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### Debugging Tools
```bash
# Run with debug logging
python -m glping --log-level DEBUG

# Run with specific debug flags
python -m glping --debug-api --debug-cache

# Use Python debugger
python -m pdb -m glping
```

### Common Debugging Scenarios
1. **API Issues**: Check network connectivity and tokens
2. **Notification Issues**: Test platform-specific notifications
3. **Cache Issues**: Verify cache file permissions and integrity
4. **Configuration Issues**: Validate config file syntax

## Performance Testing

### Load Testing
```bash
# Install load testing tools
pip install locust

# Run load test
locust -f tests/load_test.py
```

### Performance Monitoring
```bash
# Monitor resource usage
python -m cProfile -m glping

# Memory profiling
python -m memory_profiler glping/main.py

# Network profiling
python -m socket_debug glping/main.py
```

## Documentation

### Code Documentation
```python
def process_event(event: dict) -> bool:
    """
    Process a GitLab event and determine if it should trigger a notification.
    
    Args:
        event: GitLab event dictionary containing event data
        
    Returns:
        bool: True if event should be notified, False otherwise
        
    Raises:
        ValueError: If event is malformed or missing required fields
        
    Example:
        >>> event = {"type": "push", "project_id": 123}
        >>> process_event(event)
        True
    """
    if not event.get('type'):
        raise ValueError("Event type is required")
    
    # Processing logic here
    return True
```

### API Documentation
- Use OpenAPI/Swagger for web API
- Document all public functions and classes
- Include examples and usage patterns
- Keep documentation in sync with code

## Release Process

### Version Management
```bash
# Update version (automatically handled by CI/CD)
bump2version patch  # or minor/major

# Build distribution
python -m build

# Upload to PyPI (automatically handled by CI/CD)
twine upload dist/*
```

### CI/CD Pipeline
The project uses GitHub Actions for automated:
- **Testing**: Multi-platform and multi-version Python testing
- **Building**: Package and binary creation for all platforms
- **Releasing**: Automatic version bumping and GitHub release creation
- **Publishing**: PyPI package publication

### Version Bumping Process
1. Push to `main` branch triggers automatic version bump
2. CI/CD creates new tag and GitHub release
3. Binaries are built for Linux, Windows, and macOS
4. PyPI package is automatically published

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] CHANGELOG.md updated
- [ ] Release tag created
- [ ] GitHub release created

## Docker Development

### Development Container
```bash
# Build development image
docker build -f docker/Dockerfile.dev -t glping:dev .

# Run development container
docker run -it glping:dev bash

# Run with mounted volume
docker run -v $(pwd):/app -it glping:dev bash
```

### Docker Compose
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  glping:
    build:
      context: .
      dockerfile: docker/Dockerfile.dev
    volumes:
      - .:/app
    environment:
      - GLPING_DEV_MODE=true
    ports:
      - "8080:8080"
```

## Contributing Guidelines

### Before Contributing
1. Read the [CONTRIBUTING.md](CONTRIBUTING.md)
2. Check existing issues and PRs
3. Discuss significant changes in an issue
4. Follow the code style guidelines

### Pull Request Process
1. Create a feature branch
2. Make your changes
3. Add tests and documentation
4. Ensure all checks pass
5. Submit a pull request
6. Address review feedback

### Community Guidelines
- Be respectful and constructive
- Focus on the code, not the person
- Provide clear, actionable feedback
- Help newcomers get started

## Troubleshooting

### Common Issues
1. **Import Errors**: Check Python path and virtual environment
2. **Permission Errors**: Check file permissions and user access
3. **Network Issues**: Check connectivity and firewall settings
4. **Configuration Issues**: Validate config file syntax

### Getting Help
- Check the [documentation](README.md)
- Search existing issues
- Create a new issue with detailed information
- Join community discussions

---

This development guide provides comprehensive information for contributing to GitLab Ping. For additional help, please refer to the project documentation or create an issue.