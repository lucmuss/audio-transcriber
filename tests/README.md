# Tests 🧪

Testing documentation for audio-transcriber.

## Overview

This directory contains the test suite for audio-transcriber, using pytest as the testing framework.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── README.md                # This file
├── test_merger.py           # Tests for transcript merging
├── test_utils.py            # Tests for utility functions
└── fixtures/                # Test data (if needed)
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=audio_transcriber --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run Specific Test File

```bash
pytest tests/test_utils.py
```

### Run Specific Test

```bash
pytest tests/test_utils.py::test_specific_function
```

### Run with Verbose Output

```bash
pytest -v
```

### Run and Stop on First Failure

```bash
pytest -x
```

### Run Only Failed Tests

```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

## Test Categories

### Unit Tests

Test individual functions and classes in isolation:
- `test_utils.py` - Utility functions
- `test_merger.py` - Merge logic

### Integration Tests

Test interaction between components (when added):
- API integration
- End-to-end workflows

## Writing Tests

### Test File Naming

- Prefix with `test_`
- Match module name: `merger.py` → `test_merger.py`

### Test Function Naming

```python
def test_function_name_expected_behavior():
    """Test that function_name does expected behavior."""
    # Arrange
    input_data = "test"
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result == expected_output
```

### Using Fixtures

```python
import pytest

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value"}

def test_with_fixture(sample_data):
    """Test using fixture."""
    assert sample_data["key"] == "value"
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
])
def test_multiple_cases(input, expected):
    """Test with multiple parameter sets."""
    assert function(input) == expected
```

## Test Coverage Goals

- **Core logic:** 95%+ coverage
- **CLI interface:** 80%+ coverage  
- **Integration:** Complete user workflows
- **Edge cases:** Error handling, special inputs

## Continuous Integration

Tests run automatically on:
- Every push to main/develop
- Every pull request
- Before releases

See `.github/workflows/ci.yml` for configuration.

## Mocking External Services

### Mock API Calls

```python
from unittest.mock import Mock, patch

@patch('audio_transcriber.transcriber.OpenAI')
def test_transcription(mock_openai):
    """Test transcription with mocked API."""
    mock_client = Mock()
    mock_openai.return_value = mock_client
    mock_client.audio.transcriptions.create.return_value = Mock(text="test")
    
    # Test code here
    result = transcribe_audio("test.mp3")
    assert result == "test"
```

### Mock File Operations

```python
from pathlib import Path
from unittest.mock import mock_open, patch

def test_file_reading():
    """Test reading files."""
    mock_data = "test content"
    
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = read_file("test.txt")
        assert result == mock_data
```

## Test Best Practices

### 1. Arrange-Act-Assert Pattern

```python
def test_something():
    # Arrange - Set up test data
    input_data = prepare_data()
    
    # Act - Execute the function
    result = function_to_test(input_data)
    
    # Assert - Verify the result
    assert result == expected
```

### 2. One Assertion Per Test

```python
# Good
def test_addition_result():
    assert add(2, 2) == 4

def test_addition_type():
    assert isinstance(add(2, 2), int)

# Avoid
def test_addition():
    result = add(2, 2)
    assert result == 4
    assert isinstance(result, int)
    assert result > 0
```

### 3. Descriptive Test Names

```python
# Good
def test_merge_removes_duplicate_sentences():
    """Test that merge function removes duplicate sentences."""
    pass

# Poor
def test_merge():
    """Test merge."""
    pass
```

### 4. Test Error Cases

```python
def test_invalid_input_raises_error():
    """Test that invalid input raises ValueError."""
    with pytest.raises(ValueError):
        process_data(None)
```

### 5. Use Fixtures for Setup

```python
@pytest.fixture
def temp_audio_file(tmp_path):
    """Create temporary audio file for testing."""
    file_path = tmp_path / "test.mp3"
    file_path.write_bytes(b"mock audio data")
    return file_path

def test_audio_processing(temp_audio_file):
    """Test audio processing with temp file."""
    result = process_audio(temp_audio_file)
    assert result is not None
```

## Debugging Failed Tests

### Print Debug Information

```bash
pytest -s  # Show print statements
```

### Drop into Debugger on Failure

```bash
pytest --pdb  # Python debugger
```

### Run Specific Test with Verbose

```bash
pytest tests/test_utils.py::test_function -vv
```

## Adding New Tests

1. **Create test file** if needed: `tests/test_newmodule.py`
2. **Import module** to test
3. **Write test functions** with `test_` prefix
4. **Run tests** to verify
5. **Check coverage** to identify gaps

Example:

```python
# tests/test_newmodule.py
import pytest
from audio_transcriber.newmodule import new_function

def test_new_function_basic_case():
    """Test new_function with basic input."""
    result = new_function("input")
    assert result == "expected"

def test_new_function_edge_case():
    """Test new_function with edge case."""
    result = new_function("")
    assert result == ""

def test_new_function_error_case():
    """Test new_function raises error on invalid input."""
    with pytest.raises(ValueError):
        new_function(None)
```

## Resources

- **pytest docs:** https://docs.pytest.org/
- **pytest-cov:** https://pytest-cov.readthedocs.io/
- **Testing best practices:** https://docs.python-guide.org/writing/tests/

## Contributing Tests

When contributing:
1. Add tests for new features
2. Update tests for changed functionality
3. Ensure all tests pass
4. Maintain or improve coverage
5. Follow existing test patterns

---

**Good tests lead to good code! 🧪**
