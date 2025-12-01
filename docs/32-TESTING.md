# Testing with Ranex

Strategies for testing Ranex-protected applications.

---

## Testing State Machines

### Direct Testing

```python
import pytest
from ranex_core import StateMachine

def test_valid_transition():
    sm = StateMachine("orders")
    assert sm.current_state == "Pending"
    
    sm.transition("Confirmed")
    assert sm.current_state == "Confirmed"

def test_invalid_transition():
    sm = StateMachine("orders")
    
    with pytest.raises(ValueError) as exc:
        sm.transition("Delivered")  # Pending → Delivered invalid
    
    assert "Illegal transition" in str(exc.value)

def test_terminal_state():
    sm = StateMachine("orders")
    sm.transition("Confirmed")
    sm.transition("Processing")
    sm.transition("Shipped")
    sm.transition("Delivered")  # Terminal
    
    with pytest.raises(ValueError):
        sm.transition("Pending")  # Can't leave terminal
```

### Testing All Transitions

```python
def test_all_transitions():
    """Verify all transitions in state.yaml work."""
    sm = StateMachine("orders")
    
    # Happy path
    sm.transition("Confirmed")
    assert sm.current_state == "Confirmed"
    
    sm.transition("Processing")
    assert sm.current_state == "Processing"
    
    sm.transition("Shipped")
    assert sm.current_state == "Shipped"
    
    sm.transition("Delivered")
    assert sm.current_state == "Delivered"

def test_cancellation_path():
    sm = StateMachine("orders")
    
    # Cancel from Pending
    sm.transition("Cancelled")
    assert sm.current_state == "Cancelled"

def test_cancel_from_confirmed():
    sm = StateMachine("orders")
    sm.transition("Confirmed")
    sm.transition("Cancelled")
    assert sm.current_state == "Cancelled"
```

---

## Testing @Contract Functions

### Basic Test

```python
import pytest
from app.features.orders.service import confirm_order

@pytest.mark.asyncio
async def test_confirm_order():
    result = await confirm_order("ORD-001")
    assert result["status"] == "Confirmed"
```

### Testing with Database

```python
import pytest
from app.features.orders.service import confirm_order
from app.db import get_test_db

@pytest.fixture
async def test_db():
    """Create test database with order."""
    db = get_test_db()
    db.execute("INSERT INTO orders (id, status) VALUES ('ORD-001', 'Pending')")
    yield db
    db.execute("DELETE FROM orders")

@pytest.mark.asyncio
async def test_confirm_order_updates_db(test_db):
    result = await confirm_order("ORD-001")
    
    # Check database was updated
    order = test_db.execute("SELECT status FROM orders WHERE id = 'ORD-001'")
    assert order.status == "Confirmed"
```

### Testing Invalid Transitions

```python
@pytest.mark.asyncio
async def test_cannot_ship_pending_order():
    """Test that you can't ship a pending order."""
    from app.features.orders.service import ship_order
    
    # Order is in Pending state
    with pytest.raises(ValueError) as exc:
        await ship_order("ORD-001")
    
    assert "Illegal transition" in str(exc.value)
```

---

## Testing Security

### Test Security Scanner

```python
import tempfile
from ranex_core import SecurityScanner

def test_detects_sql_injection():
    scanner = SecurityScanner()
    
    vuln_code = '''
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
        f.write(vuln_code)
        f.flush()
        
        result = scanner.scan_file_py(f.name)
        
        assert not result.secure
        assert len(result.violations) > 0
        assert any(v.pattern == "sql_injection" for v in result.violations)

def test_clean_code_passes():
    scanner = SecurityScanner()
    
    clean_code = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    return db.execute(query, (user_id,))
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
        f.write(clean_code)
        f.flush()
        
        result = scanner.scan_file_py(f.name)
        
        assert result.secure
```

---

## Testing Import Validation

```python
from ranex_core import ImportValidator

def test_detects_typosquat():
    validator = ImportValidator()
    
    result = validator.check_package("reqests")
    
    assert not result.is_valid
    assert result.suggestion == "requests"

def test_allows_valid_package():
    validator = ImportValidator()
    
    result = validator.check_package("requests")
    
    assert result.is_valid
```

---

## Integration Tests

### FastAPI Test Client

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_create_order(client):
    response = client.post("/orders/", json={
        "product_id": "PROD-001",
        "quantity": 2
    })
    
    assert response.status_code == 200
    assert response.json()["status"] == "Pending"

def test_confirm_order(client):
    # Create order first
    create_response = client.post("/orders/", json={
        "product_id": "PROD-001",
        "quantity": 2
    })
    order_id = create_response.json()["id"]
    
    # Confirm it
    confirm_response = client.post(f"/orders/{order_id}/confirm")
    
    assert confirm_response.status_code == 200
    assert confirm_response.json()["status"] == "Confirmed"

def test_cannot_ship_pending(client):
    # Create order (Pending state)
    create_response = client.post("/orders/", json={
        "product_id": "PROD-001",
        "quantity": 2
    })
    order_id = create_response.json()["id"]
    
    # Try to ship without confirming
    ship_response = client.post(f"/orders/{order_id}/ship")
    
    assert ship_response.status_code == 400
    assert "Illegal transition" in ship_response.json()["detail"]
```

---

## Test Fixtures

### conftest.py

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import get_db, init_test_db

@pytest.fixture(scope="session")
def test_db():
    """Initialize test database."""
    db = init_test_db()
    yield db
    db.close()

@pytest.fixture
def client(test_db):
    """Create test client."""
    app.dependency_overrides[get_db] = lambda: test_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def sample_order(test_db):
    """Create a sample order."""
    order_id = "TEST-001"
    test_db.execute("""
        INSERT INTO orders (id, status, product_id, quantity)
        VALUES (?, 'Pending', 'PROD-001', 1)
    """, (order_id,))
    test_db.commit()
    
    yield order_id
    
    test_db.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    test_db.commit()
```

---

## Testing Patterns

### Pattern 1: Test Each State Path

```python
@pytest.mark.parametrize("final_state,expected_path", [
    ("Confirmed", ["Confirmed"]),
    ("Processing", ["Confirmed", "Processing"]),
    ("Shipped", ["Confirmed", "Processing", "Shipped"]),
    ("Delivered", ["Confirmed", "Processing", "Shipped", "Delivered"]),
])
def test_state_paths(final_state, expected_path):
    sm = StateMachine("orders")
    
    for state in expected_path:
        sm.transition(state)
    
    assert sm.current_state == final_state
```

### Pattern 2: Test Edge Cases

```python
def test_concurrent_transitions():
    """Test that transitions are atomic."""
    import asyncio
    from app.features.orders.service import confirm_order
    
    # Create multiple orders
    order_ids = ["ORD-001", "ORD-002", "ORD-003"]
    
    # Confirm all concurrently
    results = await asyncio.gather(*[
        confirm_order(oid) for oid in order_ids
    ])
    
    assert all(r["status"] == "Confirmed" for r in results)
```

### Pattern 3: Test Error Messages

```python
def test_clear_error_message():
    sm = StateMachine("orders")
    
    try:
        sm.transition("Delivered")
    except ValueError as e:
        error = str(e)
        assert "Pending" in error  # Shows current state
        assert "Delivered" in error  # Shows attempted state
        assert "Confirmed" in error  # Shows allowed states
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/features/test_orders.py

# Run specific test
pytest tests/features/test_orders.py::test_confirm_order

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

---

## CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Next Steps

- [FastAPI Integration](./33-FASTAPI-INTEGRATION.md) - Full application example
- [Troubleshooting](./40-TROUBLESHOOTING.md) - Common issues

