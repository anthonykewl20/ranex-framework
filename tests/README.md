# Tests Directory

This directory contains unit tests and integration tests for the Ranex Framework.

## Quick Start

### Run All Tests

```bash
# From project root
./run_tests.sh
```

### Run Tests with pytest

```bash
# Install pytest first
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_state_machine.py -v

# Run specific test
pytest tests/test_state_machine.py::TestStateMachine::test_valid_transition -v
```

### Run Tests with unittest

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_state_machine
```

## Test Files

- `test_state_machine.py` - Tests for StateMachine class
- `test_contract.py` - Tests for @Contract decorator

## Adding New Tests

1. Create a new test file: `test_<feature>.py`
2. Follow pytest conventions:
   - Test functions start with `test_`
   - Test classes start with `Test`
   - Use pytest fixtures for setup
3. For async tests, use `@pytest.mark.asyncio` decorator

## Example Test

```python
import pytest
from ranex_core import StateMachine

def test_my_feature():
    """Test description."""
    sm = StateMachine("payment")
    assert sm.current_state == "Idle"
```

