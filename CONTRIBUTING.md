# Contributing to Audio Transcriber

Thank you for your interest in contributing to Audio Transcriber! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your changes
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- Git

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/audio-transcriber.git
cd audio-transcriber

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Making Changes

### Branch Naming

- `feature/description` - For new features
- `fix/description` - For bug fixes
- `docs/description` - For documentation changes
- `refactor/description` - For code refactoring

### Commit Messages

Follow the conventional commits specification:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(cli): add support for batch processing
fix(segmenter): resolve audio duration calculation bug
docs(readme): update installation instructions
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=audio_transcriber --cov-report=html

# Run specific test file
pytest tests/test_utils.py

# Run specific test
pytest tests/test_utils.py::TestFormatDuration::test_seconds_only
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the existing test structure

Example:
```python
def test_feature_description(self):
    # Arrange
    input_data = "test"
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

## Code Quality

### Code Formatting

We use Black for code formatting:

```bash
# Format code
black src tests

# Check formatting
black --check src tests
```

### Import Sorting

We use isort for import organization:

```bash
# Sort imports
isort src tests

# Check sorting
isort --check-only src tests
```

### Linting

We use flake8 for linting:

```bash
flake8 src tests --max-line-length=100
```

### Type Checking

We encourage type hints and use mypy:

```bash
mypy src
```

### Pre-commit Hooks

Pre-commit hooks run automatically on commit to ensure code quality:

```bash
# Run manually
pre-commit run --all-files
```

## Submitting Changes

### Pull Request Process

1. **Update Documentation**: Update README.md, docstrings, and comments as needed
2. **Add Tests**: Include tests for new features or bug fixes
3. **Update Changelog**: Add an entry to CHANGELOG.md (if applicable)
4. **Run Quality Checks**: Ensure all tests pass and code quality checks succeed
5. **Create Pull Request**: Provide a clear description of changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Description of testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings
```

### Review Process

- Maintainers will review your pull request
- Address any feedback or requested changes
- Once approved, your changes will be merged

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Keep functions focused and concise
- Add docstrings to all public functions and classes
- Use type hints where appropriate

### Documentation

- Update docstrings for modified functions
- Keep README.md up to date
- Add inline comments for complex logic
- Update examples if behavior changes

### Performance

- Consider performance implications of changes
- Profile code for performance-critical sections
- Avoid premature optimization

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Reach out to maintainers
- Check existing issues and discussions

Thank you for contributing! 🎉
