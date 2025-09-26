# Contributing to GitLab Ping

We welcome contributions to GitLab Ping! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](.github/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork the Repository**
   ```bash
   # Fork the repository on GitHub
   # Clone your fork locally
   git clone https://github.com/your-username/glping.git
   cd glping
   ```

2. **Set Up Development Environment**
   ```bash
   # Create a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install development dependencies
   pip install -e ".[dev]"
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)

### Environment Setup
1. Copy the example configuration:
   ```bash
   cp config.example.yaml config.yaml
   ```

2. Configure your GitLab instance settings in `config.yaml`

3. Run the development server:
   ```bash
   python -m glping --dev
   ```

### Running Tests
```bash
# Run all tests
make test

# Run specific test file
python -m pytest tests/test_specific_file.py

# Run tests with coverage
make test-coverage

# Run notification stacking tests
make test-stacking
```

## Making Changes

### Branch Strategy
1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-fix-name
   ```

### Code Style
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

### Commit Messages
Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Examples:
```
feat(notifier): add macOS notification stacking support
fix(api): handle rate limiting errors gracefully
docs(readme): update installation instructions
```

## Submitting Changes

### Pull Request Process
1. **Ensure Tests Pass**
   ```bash
   make test
   make lint
   ```

2. **Update Documentation**
   - Update README.md if needed
   - Update CHANGELOG.md for significant changes
   - Add or update docstrings

3. **Create Pull Request**
   - Use the [pull request template](.github/PULL_REQUEST_TEMPLATE.md)
   - Link to any related issues
   - Describe your changes clearly
   - Include screenshots if applicable

4. **Review Process**
   - Address review comments promptly
   - Keep the PR up to date with the main branch
   - Be responsive to reviewer feedback

### Code Review Guidelines
- Be respectful and constructive
- Focus on the code, not the person
- Provide specific, actionable feedback
- Suggest improvements rather than just pointing out problems

## Reporting Issues

### Bug Reports
When reporting bugs, please include:
1. **Environment Information**
   - Operating system and version
   - Python version
   - GitLab Ping version
   - GitLab version (if applicable)

2. **Steps to Reproduce**
   - Clear, step-by-step instructions
   - Expected behavior
   - Actual behavior
   - Error messages (if any)

3. **Additional Context**
   - Screenshots
   - Configuration files (redact sensitive information)
   - Log files

### Feature Requests
When requesting features, please include:
1. **Problem Statement**
   - What problem are you trying to solve?
   - Why is this feature needed?

2. **Proposed Solution**
   - Describe the feature in detail
   - How would it work?
   - What would the user experience be?

3. **Alternatives**
   - Are there any existing workarounds?
   - Have you considered other approaches?

## Style Guidelines

### Python Code
- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 88 characters
- Use f-strings for string formatting
- Prefer list comprehensions over map/filter
- Use context managers for resource management

### Documentation
- Use Google-style docstrings
- Include examples for complex functions
- Keep documentation up to date with code changes
- Use clear, concise language

### Git
- Keep commits small and focused
- Write clear commit messages
- Use branches for development
- Keep your fork up to date with upstream

## Testing

### Writing Tests
- Write tests for all new features
- Write tests for bug fixes
- Use pytest for testing
- Mock external dependencies
- Test both success and error cases

### Test Coverage
- Aim for high test coverage
- Focus on critical paths
- Don't test implementation details
- Test user-facing behavior

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=glping

# Run specific test categories
pytest -m "unit"
pytest -m "integration"
```

## Getting Help

If you need help with contributing:
- Check the [documentation](README.md)
- Search existing issues
- Create a new issue with the "question" label
- Join our community discussions

---

Thank you for contributing to GitLab Ping! 🎉