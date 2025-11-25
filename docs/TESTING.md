# Testing Guide for Ranex Framework

This guide explains how to run tests for the Ranex Framework codebase.

## Quick Start

### 0. Setup Development Environment (First Time Only)

**Important:** Before running tests or examples, you need to set up the development environment so Python can find the `ranex` module.

**Option A: Install in Development Mode (Recommended)**

```bash
# Install ranex package with CLI dependencies
pip install -e .
```

This will:
- Install CLI dependencies (typer, rich, PyYAML)
- Set up the `ranex` command
- Install `ranex_core` wheel (if not already installed)
- Install `ranex` package in development mode (editable install)
- Verify everything works

**Option B: Set PYTHONPATH Manually**

```bash
# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH (needs to be done in each terminal session)
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# Or add to your shell profile (~/.bashrc or ~/.zshrc):
# export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH
```

### 1. Run Existing Verification Scripts

The codebase includes verification scripts that test installation and structure:

```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Verify installation
./scripts/verify_installation.sh

# Verify structure
./scripts/test/verify_structure.sh
```

### 2. Run Demo Examples as Tests

The `examples/` directory contains 19 demo scripts that can be used as integration tests:

```bash
# If you used setup_dev.sh, you can run directly:
cd examples
python3 basic_contract.py
python3 state_machine_demo.py
python3 workflow_management_demo.py
python3 import_validation_demo.py
python3 structure_enforcement_demo.py

# If you're using PYTHONPATH, make sure it's set:
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH
cd examples
python3 basic_contract.py

# Or run all demos with a script
for demo in *.py; do
    echo "Testing $demo..."
    python3 "$demo" && echo "✅ $demo passed" || echo "❌ $demo failed"
done
```

## Setting Up Your Own Test Suite

### Option 1: Using pytest (Recommended)

#### Install pytest

```bash
source venv/bin/activate
pip install pytest pytest-asyncio pytest-cov
```

#### Create Test Directory Structure

```bash
mkdir -p tests
mkdir -p tests/unit
mkdir -p tests/integration
```

#### Example Test File: `tests/test_state_machine.py`

```python
"""Tests for StateMachine functionality."""
import pytest
from ranex_core import StateMachine


class TestStateMachine:
    """Test StateMachine class."""
    
    def test_create_state_machine(self):
        """Test creating a state machine."""
        sm = StateMachine("payment")
        assert sm.current_state == "Idle"
    
    def test_valid_transition(self):
        """Test valid state transition."""
        sm = StateMachine("payment")
        sm.transition("Processing")
        assert sm.current_state == "Processing"
    
    def test_invalid_transition(self):
        """Test invalid state transition raises error."""
        sm = StateMachine("payment")
        with pytest.raises(ValueError, match="Illegal transition"):
            sm.transition("Paid")  # Cannot skip Processing
    
    def test_state_machine_rules(self):
        """Test state machine rules are accessible."""
        sm = StateMachine("payment")
        assert sm.rules.initial == "Idle"
        assert "Processing" in sm.rules.states
```

#### Example Test File: `tests/test_contract.py`

```python
"""Tests for @Contract decorator."""
import pytest
import asyncio
from ranex import Contract
from pydantic import BaseModel, Field


class PaymentRequest(BaseModel):
    """Test payment request schema."""
    amount: float = Field(gt=0)
    currency: str = Field(default="USD")


@pytest.mark.asyncio
async def test_contract_decorator():
    """Test @Contract decorator works."""
    @Contract(feature="payment")
    async def process_payment(_ctx, amount: float):
        _ctx.transition("Processing")
        _ctx.transition("Paid")
        return {"status": "success", "amount": amount}
    
    result = await process_payment(100.0)
    assert result["status"] == "success"
    assert result["amount"] == 100.0


@pytest.mark.asyncio
async def test_contract_with_schema():
    """Test @Contract with Pydantic schema."""
    @Contract(feature="payment", input_schema=PaymentRequest)
    async def process_payment(_ctx, request: PaymentRequest):
        _ctx.transition("Processing")
        _ctx.transition("Paid")
        return {"status": "success", "amount": request.amount}
    
    request = PaymentRequest(amount=50.0, currency="USD")
    result = await process_payment(request)
    assert result["status"] == "success"
```

#### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_state_machine.py

# Run with coverage
pytest --cov=ranex --cov=ranex_core tests/

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_state_machine.py::TestStateMachine::test_valid_transition
```

### Option 2: Using unittest (Standard Library)

#### Example Test File: `tests/test_state_machine_unittest.py`

```python
"""Tests using unittest framework."""
import unittest
from ranex_core import StateMachine


class TestStateMachine(unittest.TestCase):
    """Test StateMachine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sm = StateMachine("payment")
    
    def test_create_state_machine(self):
        """Test creating a state machine."""
        self.assertEqual(self.sm.current_state, "Idle")
    
    def test_valid_transition(self):
        """Test valid state transition."""
        self.sm.transition("Processing")
        self.assertEqual(self.sm.current_state, "Processing")
    
    def test_invalid_transition(self):
        """Test invalid state transition raises error."""
        with self.assertRaises(ValueError):
            self.sm.transition("Paid")  # Cannot skip Processing


if __name__ == "__main__":
    unittest.main()
```

#### Run Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_state_machine_unittest

# Run with verbose output
python -m unittest discover tests -v
```

## Test Configuration

### Create `pytest.ini` for pytest

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = 
    -v
    --strict-markers
    --tb=short
```

### Create `.coveragerc` for Coverage

```ini
[run]
source = ranex,ranex_core
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Running Tests in CI/CD

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install wheels/ranex_core-0.0.1-*.whl
          pip install pytest pytest-asyncio pytest-cov
          pip install -r app/requirements.txt
      - name: Run tests
        run: |
          export PYTHONPATH=$PWD:$PYTHONPATH
          pytest tests/ -v --cov=ranex --cov=ranex_core
      - name: Run verification scripts
        run: |
          chmod +x scripts/verify_installation.sh
          ./scripts/verify_installation.sh
```

## Test Categories

### Unit Tests

Test individual components in isolation:

```python
# tests/unit/test_state_machine.py
def test_state_machine_creation():
    sm = StateMachine("payment")
    assert sm.current_state == "Idle"
```

### Integration Tests

Test components working together:

```python
# tests/integration/test_contract_integration.py
@pytest.mark.asyncio
async def test_payment_flow():
    @Contract(feature="payment")
    async def process_payment(_ctx, amount: float):
        _ctx.transition("Processing")
        # Simulate processing
        _ctx.transition("Paid")
        return {"status": "success"}
    
    result = await process_payment(100.0)
    assert result["status"] == "success"
```

### End-to-End Tests

Test complete workflows:

```python
# tests/e2e/test_payment_workflow.py
@pytest.mark.asyncio
async def test_complete_payment_workflow():
    # Test the entire payment flow from start to finish
    # This might involve multiple functions, state transitions, etc.
    pass
```

## Testing Best Practices

1. **Test Isolation**: Each test should be independent
2. **Use Fixtures**: Share common setup code using pytest fixtures
3. **Test Edge Cases**: Test error conditions, boundary values
4. **Mock External Dependencies**: Use mocks for database, APIs, etc.
5. **Keep Tests Fast**: Unit tests should run quickly
6. **Descriptive Names**: Test names should describe what they test

## Example Test Fixtures

```python
# conftest.py
import pytest
from ranex_core import StateMachine


@pytest.fixture
def payment_state_machine():
    """Fixture providing a payment state machine."""
    return StateMachine("payment")


@pytest.fixture
def sample_payment_request():
    """Fixture providing a sample payment request."""
    from pydantic import BaseModel, Field
    
    class PaymentRequest(BaseModel):
        amount: float = Field(gt=0)
        currency: str = Field(default="USD")
    
    return PaymentRequest(amount=100.0, currency="USD")
```

## Running All Tests

Create a test runner script `run_tests.sh`:

```bash
#!/bin/bash
set -e

echo "🧪 Running Ranex Framework Tests"
echo "================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH

# Run verification scripts
echo "1. Running verification scripts..."
./scripts/verify_installation.sh
echo ""

# Run pytest tests (if they exist)
if [ -d "tests" ]; then
    echo "2. Running pytest tests..."
    pytest tests/ -v
    echo ""
fi

# Run demo examples as integration tests
echo "3. Running demo examples..."
cd examples
for demo in *.py; do
    echo "  Testing $demo..."
    python3 "$demo" > /dev/null 2>&1 && echo "    ✅ $demo passed" || echo "    ❌ $demo failed"
done
cd ..

echo ""
echo "✅ All tests complete!"
```

Make it executable:

```bash
chmod +x run_tests.sh
./run_tests.sh
```

## Troubleshooting

### Import Errors

If you get import errors, make sure PYTHONPATH is set:

```bash
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH
```

### Module Not Found

Ensure ranex_core is installed:

```bash
pip install wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
```

### Async Test Issues

For async tests with pytest, install pytest-asyncio:

```bash
pip install pytest-asyncio
```

And mark async tests:

```python
@pytest.mark.asyncio
async def test_async_function():
    # Your async test code
    pass
```

## Next Steps

1. Create your test files in `tests/` directory
2. Write tests for the features you're using
3. Run tests regularly during development
4. Add tests to your CI/CD pipeline
5. Aim for good test coverage (80%+)

---

**Happy Testing!** 🧪

