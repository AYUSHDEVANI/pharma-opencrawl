# Unit Tests

## Overview

This directory contains unit tests for the Pharma Intelligence System.

## Test Files

- **`test_config.py`**: Configuration and environment variable tests
- **`test_extractors.py`**: Data extraction and parsing tests
- **`test_agents.py`**: AI agent initialization and functionality tests

## Running Tests

### Run All Tests
```bash
# From project root
python -m pytest tests/ -v

# Or using unittest
python -m unittest discover tests/
```

### Run Specific Test File
```bash
# Run config tests
python -m pytest tests/test_config.py -v

# Run extractor tests
python -m pytest tests/test_extractors.py -v

# Run agent tests
python -m pytest tests/test_agents.py -v
```

### Run Specific Test Class
```bash
python -m pytest tests/test_agents.py::TestValidatorAgent -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=agents --cov=crawler --cov=config --cov-report=html
```

## Test Structure

### Configuration Tests (`test_config.py`)
Tests configuration loading and validation:
- API key loading
- Model configuration
- Directory setup
- Environment variables
- Default values

### Extractor Tests (`test_extractors.py`)
Tests data extraction logic:
- Disease category mapping
- Drug information extraction
- Text parsing
- Crawled data processing

### Agent Tests (`test_agents.py`)
Tests AI agent functionality:
- Agent initialization
- Response structure validation
- Fallback behavior
- Batch processing
- Mock AI responses

## Mocking

Agent tests use mocking to avoid requiring API keys:
```python
@patch('agents.validator.ExtractionValidatorAgent._create_agent')
def test_validator_agent_init(self, mock_create):
    mock_llm = Mock()
    agent = ExtractionValidatorAgent(mock_llm)
```

## Test Data

Tests use sample data for validation:
```python
sample_text = """
FDA approves Ozempic (semaglutide) manufactured by Novo Nordisk
for the treatment of Type 2 diabetes.
"""
```

## Adding New Tests

1. Create test file: `test_<module_name>.py`
2. Import required modules
3. Create test class inheriting from `unittest.TestCase`
4. Write test methods starting with `test_`
5. Run tests to verify

Example:
```python
import unittest
from module import MyClass

class TestMyClass(unittest.TestCase):
    def setUp(self):
        self.obj = MyClass()

    def test_my_function(self):
        result = self.obj.my_function()
        self.assertEqual(result, expected_value)
```

## CI/CD Integration

### GitHub Actions (example)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ -v
```

## Coverage Report

Generate HTML coverage report:
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # View in browser
```

## Known Limitations

- Agent tests use mocks (no real AI calls)
- Web crawler tests don't test actual websites
- No integration tests yet

## Future Improvements

- [ ] Add integration tests
- [ ] Add performance tests
- [ ] Test real API calls (with test key)
- [ ] Add end-to-end workflow tests
- [ ] Increase coverage to >80%
