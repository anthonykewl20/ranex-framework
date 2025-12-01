# Security Scanning

Ranex Community Edition includes a SAST (Static Application Security Testing) scanner that detects 7 common vulnerability patterns in your code.

---

## What It Detects

| Pattern | Description | Example |
|---------|-------------|---------|
| **SQL Injection** | Unsanitized SQL queries | `f"SELECT * FROM users WHERE id = {user_id}"` |
| **Hardcoded Secrets** | API keys, passwords in code | `API_KEY = "sk-..."` |
| **Command Injection** | Unsafe system commands | `os.system(user_input)` |
| **Weak Cryptography** | MD5, SHA1 for security | `hashlib.md5(password)` |
| **Insecure Deserialization** | Unsafe pickle usage | `pickle.loads(data)` |
| **Path Traversal** | Directory traversal attacks | `open(f"../data/{filename}")` |
| **Insecure Random** | `random` for security | `random.randint()` for tokens |

---

## Running Security Scan

### CLI Command

```bash
ranex scan
```

Output:
```
🔍 Ranex Security Scan
======================

Scanning: ./app

Security Results:
  ✅ SQL Injection: None found
  ⚠️  Hardcoded Secrets: 1 found
     - app/config.py:15 - Potential hardcoded API key
  ✅ Command Injection: None found
  ✅ Weak Cryptography: None found
  ✅ Insecure Deserialization: None found
  ✅ Path Traversal: None found
  ✅ Insecure Random: None found

Summary: 1 issue found
```

### Python API

```python
from ranex_core import SecurityScanner

scanner = SecurityScanner()

# Scan a file
result = scanner.scan_file_py("app/service.py")

print(f"Secure: {result.secure}")
print(f"Violations: {len(result.violations)}")

for violation in result.violations:
    print(f"  - Line {violation.line}: {violation.message}")
```

---

## Pattern Details

### 1. SQL Injection

**What it catches:**
```python
# BAD: String interpolation in SQL
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(f"DELETE FROM orders WHERE id = {order_id}")

# BAD: String concatenation
query = "SELECT * FROM users WHERE name = '" + username + "'"
```

**How to fix:**
```python
# GOOD: Parameterized queries
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

---

### 2. Hardcoded Secrets

**What it catches:**
```python
# BAD: API keys in code
API_KEY = "sk-1234567890abcdef"
SECRET_KEY = "my-secret-key"
PASSWORD = "admin123"
DATABASE_PASSWORD = "password123"

# BAD: AWS/Azure/GCP credentials
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
```

**How to fix:**
```python
# GOOD: Environment variables
import os
API_KEY = os.environ.get("API_KEY")
SECRET_KEY = os.environ["SECRET_KEY"]

# GOOD: Secrets manager
from some_secrets_manager import get_secret
API_KEY = get_secret("api-key")
```

---

### 3. Command Injection

**What it catches:**
```python
# BAD: os.system with user input
os.system(f"ls {directory}")
os.system("rm -rf " + path)

# BAD: subprocess with shell=True
subprocess.call(f"grep {pattern} file.txt", shell=True)
subprocess.Popen(user_command, shell=True)
```

**How to fix:**
```python
# GOOD: Use list arguments
subprocess.run(["ls", directory])
subprocess.run(["grep", pattern, "file.txt"])

# GOOD: Avoid shell=True
subprocess.run(["rm", "-rf", path])
```

---

### 4. Weak Cryptography

**What it catches:**
```python
# BAD: MD5 for passwords/security
import hashlib
hashlib.md5(password.encode()).hexdigest()

# BAD: SHA1 for security
hashlib.sha1(data).hexdigest()
```

**How to fix:**
```python
# GOOD: Use bcrypt for passwords
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# GOOD: Use SHA-256+ for hashing
import hashlib
hashlib.sha256(data).hexdigest()

# GOOD: Use secrets for tokens
import secrets
token = secrets.token_hex(32)
```

---

### 5. Insecure Deserialization

**What it catches:**
```python
# BAD: pickle with untrusted data
import pickle
data = pickle.loads(user_data)  # Can execute arbitrary code!
pickle.load(open(untrusted_file, 'rb'))
```

**How to fix:**
```python
# GOOD: Use JSON for serialization
import json
data = json.loads(user_data)

# GOOD: If pickle required, validate first
import hmac
if hmac.compare_digest(signature, expected_signature):
    data = pickle.loads(trusted_data)
```

---

### 6. Path Traversal

**What it catches:**
```python
# BAD: User input in file paths
filename = request.args.get("file")
open(f"uploads/{filename}")  # User could pass "../../../etc/passwd"

# BAD: Direct concatenation
path = "data/" + user_path
```

**How to fix:**
```python
# GOOD: Validate and sanitize
import os
from pathlib import Path

def safe_path(base_dir, user_path):
    base = Path(base_dir).resolve()
    full_path = (base / user_path).resolve()
    
    # Ensure path is under base directory
    if not str(full_path).startswith(str(base)):
        raise ValueError("Invalid path")
    
    return full_path

# GOOD: Use allowlist
ALLOWED_FILES = ["report.pdf", "data.csv", "summary.txt"]
if filename not in ALLOWED_FILES:
    raise ValueError("File not allowed")
```

---

### 7. Insecure Random

**What it catches:**
```python
# BAD: random module for security
import random
token = random.randint(0, 999999)  # Predictable!
session_id = ''.join(random.choices(string.ascii_letters, k=32))
```

**How to fix:**
```python
# GOOD: Use secrets module
import secrets
token = secrets.token_hex(32)
session_id = secrets.token_urlsafe(32)
random_number = secrets.randbelow(1000000)
```

---

## Using in CI/CD

### GitHub Actions

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Ranex
        run: pip install ./ranex_core-*.whl ./ranex
      
      - name: Run Security Scan
        run: ranex scan --strict
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ranex-security
        name: Ranex Security Scan
        entry: ranex scan
        language: system
        types: [python]
```

---

## Ignoring False Positives

Create `.ranex/ignore` to exclude files:

```
# Ignore test files
tests/
test_*.py

# Ignore specific file
app/legacy/old_code.py

# Ignore pattern
**/migrations/*.py
```

For inline ignores (in code):

```python
# ranex: ignore-next-line
API_KEY = "test-key-for-development"  # This line won't be flagged
```

---

## API Reference

### SecurityScanner Class

```python
from ranex_core import SecurityScanner

scanner = SecurityScanner()
```

### Methods

#### `scan_file_py(path: str) -> SecurityScanResult`

Scan a Python file.

```python
result = scanner.scan_file_py("app/service.py")
```

**Returns:** `SecurityScanResult` with:
- `secure: bool` - True if no violations
- `violations: List[SecurityViolation]` - List of findings
- `scan_time_ms: int` - Scan duration

### SecurityViolation

```python
for v in result.violations:
    print(v.line)      # Line number
    print(v.column)    # Column number
    print(v.pattern)   # Pattern type (e.g., "sql_injection")
    print(v.message)   # Human-readable description
    print(v.severity)  # "high", "medium", "low"
```

---

## Team Edition: More Patterns

Community Edition includes 7 patterns. Team Edition adds 23+ more:

| Pattern | Community | Team |
|---------|:---------:|:----:|
| SQL Injection | ✅ Basic | ✅ Advanced (ORM) |
| XSS | ❌ | ✅ |
| CSRF | ❌ | ✅ |
| SSRF | ❌ | ✅ |
| XXE | ❌ | ✅ |
| Sensitive Data Exposure | ✅ Basic | ✅ Advanced |
| JWT Vulnerabilities | ❌ | ✅ |
| Race Conditions | ❌ | ✅ |
| ... and more | | |

Contact sales@ranex.dev for Team Edition.

---

## Next Steps

- [Import Validation](./14-IMPORT-VALIDATION.md) - Typosquatting detection
- [Architecture Enforcement](./13-ARCHITECTURE.md) - Layer validation
- [CLI Reference](./20-CLI-REFERENCE.md) - All scan options

