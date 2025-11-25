# Testing Commands - Direct Command Reference

This guide provides direct commands for testing Ranex Framework **without using scripts**.

## Prerequisites

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Setup Development Environment (One-time)
```bash
# Install ranex_core wheel
pip install wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl

# Create .pth file for development (makes ranex importable)
python3 -c "import site; print(site.getsitepackages()[0])" | xargs -I {} sh -c 'echo "$(pwd)" > {}/ranex-dev.pth'
```

**Or use the setup script:**
```bash
./setup_dev.sh
```

## Testing Commands

### 1. Verify Installation

```bash
# Check ranex_core
python3 -c "import ranex_core; print('✅ Ranex Core installed')"

# Check ranex package
python3 -c "import ranex; print('✅ Ranex package installed')"

# Check Contract decorator
python3 -c "from ranex import Contract; print('✅ Contract decorator available')"
```

### 2. Run Unit Tests with pytest

```bash
# Install pytest (if not already installed)
pip install pytest pytest-asyncio

# Set PYTHONPATH (if not using .pth file)
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_state_machine.py -v

# Run specific test
pytest tests/test_state_machine.py::TestStateMachine::test_valid_transition -v

# Run with coverage
pytest tests/ --cov=ranex --cov=ranex_core
```

### 3. Run Unit Tests with unittest

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# Run all tests
python3 -m unittest discover tests

# Run specific test file
python3 -m unittest tests.test_state_machine

# Run with verbose output
python3 -m unittest discover tests -v
```

### 4. Run Demo Examples as Integration Tests

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# Run individual demos
cd examples
python3 basic_contract.py
python3 state_machine_demo.py
python3 workflow_management_demo.py
python3 import_validation_demo.py
python3 structure_enforcement_demo.py

# Run all demos in a loop
for demo in *.py; do
    echo "Testing $demo..."
    python3 "$demo" && echo "✅ $demo passed" || echo "❌ $demo failed"
done
```

### 5. Test State Machine Directly

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# Test state machine creation
python3 -c "from ranex_core import StateMachine; sm = StateMachine('payment'); print(f'Current state: {sm.current_state}')"

# Test valid transition
python3 -c "from ranex_core import StateMachine; sm = StateMachine('payment'); sm.transition('Processing'); print(f'State: {sm.current_state}')"

# Test invalid transition (should fail)
python3 -c "from ranex_core import StateMachine; sm = StateMachine('payment'); sm.transition('Paid')" 2>&1 || echo "✅ Invalid transition correctly rejected"
```

### 6. Test Contract Decorator Directly

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# Test Contract import
python3 -c "from ranex import Contract; print('✅ Contract imported')"

# Test Contract decorator (create a test file)
cat > /tmp/test_contract.py << 'EOF'
import asyncio
from ranex import Contract

@Contract(feature="payment")
async def test_payment(_ctx, amount: float):
    _ctx.transition("Processing")
    _ctx.transition("Paid")
    return {"status": "success", "amount": amount}

result = asyncio.run(test_payment(100.0))
print(f"✅ Contract test passed: {result}")
EOF

python3 /tmp/test_contract.py
```

### 7. Test Import Validation

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# Test ImportValidator
python3 -c "from ranex_core import ImportValidator; iv = ImportValidator(); result = iv.check_package('fastapi'); print(f'fastapi is safe: {result.is_safe}')"
```

### 8. Test Workflow Manager

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# Test WorkflowManager
python3 -c "from ranex_core import WorkflowManager, ProjectPhase; import tempfile; wm = WorkflowManager(tempfile.mkdtemp()); print(f'Current phase: {wm.get_phase()}')"
```

### 9. Test Structure Sentinel

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# Test StructureSentinel
python3 -c "from ranex_core import StructureSentinel; ss = StructureSentinel('.'); print('✅ StructureSentinel created')"
```

### 10. Run All Tests in Sequence

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# 1. Verify installation
echo "1. Verifying installation..."
python3 -c "import ranex_core; import ranex; from ranex import Contract; print('✅ All imports work')"

# 2. Run pytest tests
echo "2. Running pytest tests..."
pytest tests/ -v --tb=short

# 3. Run demo examples
echo "3. Running demo examples..."
cd examples
python3 basic_contract.py > /dev/null 2>&1 && echo "✅ basic_contract.py passed" || echo "❌ basic_contract.py failed"
python3 state_machine_demo.py > /dev/null 2>&1 && echo "✅ state_machine_demo.py passed" || echo "❌ state_machine_demo.py failed"
cd ..
```

## Quick Test Checklist

Run these commands to verify everything works:

```bash
# 1. Setup (one-time)
source venv/bin/activate
pip install wheels/ranex_core-0.0.1-cp312-cp312-linux_x86_64.whl
python3 -c "import site; print(site.getsitepackages()[0])" | xargs -I {} sh -c 'echo "$(pwd)" > {}/ranex-dev.pth'

# 2. Verify imports
python3 -c "import ranex_core; import ranex; from ranex import Contract; print('✅ All imports work')"

# 3. Run tests
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH
pytest tests/ -v

# 4. Test demos
cd examples
python3 basic_contract.py
python3 state_machine_demo.py
```

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError: No module named 'ranex'`:

```bash
# Option 1: Set PYTHONPATH
export PYTHONPATH=/home/tonyo/projects/ranex/Pre-Release-v0.1:$PYTHONPATH

# Option 2: Use .pth file (persistent)
python3 -c "import site; print(site.getsitepackages()[0])" | xargs -I {} sh -c 'echo "$(pwd)" > {}/ranex-dev.pth'
```

### pytest Not Found

```bash
pip install pytest pytest-asyncio
```

### Virtual Environment Not Activated

```bash
source venv/bin/activate
```

---

**See also:**
- [TESTING.md](TESTING.md) - Complete testing guide with scripts
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide

