# Testing Guide

This document explains how to run tests for both TypeScript/JavaScript and Python components.

## Quick Start

```bash
# Install dependencies
npm install                    # TypeScript/JavaScript dependencies
pip install -r requirements-test.txt  # Python testing dependencies

# Run all tests
npm test                       # Run Jest tests
pytest                         # Run Python tests

# Run with coverage
npm run test:coverage          # JavaScript coverage report
pytest --cov=. --cov-report=html  # Python coverage report
```

---

## TypeScript/JavaScript Testing

### Configuration
- **Framework**: Jest with ts-jest
- **Environment**: jsdom (for DOM testing)
- **Config**: `jest.config.js`

### Running Tests

```bash
# Run all tests
npm test

# Run in watch mode (auto-rerun on changes)
npm run test:watch

# Run with coverage report
npm run test:coverage

# Run specific test file
npm test -- tests/stateManager.test.ts

# Run tests matching a pattern
npm test -- --testNamePattern="initialization"
```

### Writing Tests

Test files should be named `*.test.ts` or `*.spec.ts` and located in the `tests/` directory.

```typescript
import { StateManager } from '../src/utils/StateManager';

describe('StateManager', () => {
  test('should initialize with default state', () => {
    const manager = StateManager.getInstance();
    expect(manager.getState().todayPnL).toBe(0);
  });
});
```

### Coverage Goals
- Statements: 70%
- Functions: 70%
- Lines: 70%
- Branches: 70%

---

## Python Testing

### Configuration
- **Framework**: pytest
- **Coverage**: pytest-cov
- **Config**: `pytest.ini`

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_gold_analysis.py

# Run specific test class
pytest tests/test_gold_analysis.py::TestDataValidation

# Run specific test method
pytest tests/test_gold_analysis.py::TestDataValidation::test_validate_dataframe_success

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Run only unit tests (skip integration tests)
pytest -m unit

# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

### Writing Tests

Test files should be named `test_*.py` and located in the `tests/` directory.

```python
import pytest
from gold_analysis_fixed import GoldMarketAnalyzer

def test_validate_dataframe_success():
    analyzer = GoldMarketAnalyzer()
    # ... test implementation
    assert is_valid is True
```

### Test Markers

Use markers to categorize tests:
- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, test interactions)
- `@pytest.mark.slow` - Slow tests (skip during quick checks)

---

## Test Structure

### TypeScript Tests
```
tests/
├── setup.ts              # Jest setup and mocks
├── stateManager.test.ts   # State management tests
├── tradeUtils.test.ts    # Trade utility tests
└── chartUtils.test.ts    # Chart rendering tests
```

### Python Tests
```
tests/
├── test_gold_analysis.py       # Gold analysis module tests
├── test_data_repository.py     # Data layer tests
├── test_strategy_discovery.py  # Strategy tests
└── test_backtesting.py         # Backtesting tests
```

---

## Mocking

### JavaScript/TypeScript

```typescript
// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock Chart.js
jest.mock('chart.js', () => ({
  Chart: jest.fn().mockImplementation(() => ({
    destroy: jest.fn(),
    update: jest.fn(),
  })),
}));
```

### Python

```python
from unittest.mock import patch, mock_open, MagicMock

# Mock file reading
with patch('builtins.open', mock_open(read_data='csv,data')):
    result = read_data_file()

# Mock pandas
with patch('pandas.read_csv') as mock_read:
    mock_read.return_value = sample_data
    analyzer = GoldMarketAnalyzer()
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test-javascript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm test
      - run: npm run typecheck

  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=. --cov-report=xml
```

---

## Common Issues

### Jest Issues

**Module not found:**
```bash
# Ensure path mapping is correct in jest.config.js
moduleNameMapper: {
  '^@/(.*)$': '<rootDir>/src/$1',
}
```

**TypeScript compilation errors:**
```bash
# Run type checking separately
npm run typecheck
```

### pytest Issues

**Import errors:**
```bash
# Ensure __init__.py exists in test directory
touch tests/__init__.py

# Run with python path
PYTHONPATH=. pytest
```

---

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on other tests
2. **Fast Tests**: Unit tests should run in milliseconds
3. **Clear Names**: Test names should describe what they're testing
4. **Arrange-Act-Assert**: Structure tests with clear setup, action, and verification
5. **Edge Cases**: Test boundary conditions and error cases
6. **Documentation**: Tests serve as documentation - make them readable

---

## Coverage Reports

### JavaScript
After running `npm run test:coverage`, view the report:
- Terminal: Shows coverage summary
- HTML: Open `coverage/lcov-report/index.html` in browser

### Python
After running `pytest --cov=. --cov-report=html`, view the report:
- Terminal: Shows missing lines
- HTML: Open `htmlcov/index.html` in browser
