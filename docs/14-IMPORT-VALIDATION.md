# Import Validation & Typosquatting Detection

Ranex detects typosquatted packages to protect against supply chain attacks.

---

## What Problem Does It Solve?

AI often hallucinates imports with typos:

```python
# AI-generated code with typos
import reqests      # Should be "requests"
import numpyy       # Should be "numpy"
import pandsa       # Should be "pandas"
```

These typos might match malicious packages published by attackers (typosquatting).

---

## How It Works

Ranex uses **Levenshtein distance** to detect packages that are suspiciously similar to popular packages:

```
"reqests" vs "requests" → Distance: 1 → SUSPICIOUS
"numpyy" vs "numpy" → Distance: 1 → SUSPICIOUS
"tensorflow" vs "tensorflow" → Distance: 0 → VALID
```

---

## Using Import Validation

### CLI

```bash
ranex scan
```

Part of scan output:
```
Import Validation:
  ✅ requests: Valid
  ⚠️  reqests: SUSPICIOUS
      Did you mean 'requests'? (Levenshtein distance: 1)
  ✅ numpy: Valid
  ⚠️  numpyy: SUSPICIOUS
      Did you mean 'numpy'? (Levenshtein distance: 1)
```

### Python API

```python
from ranex_core import ImportValidator

validator = ImportValidator()

# Check a package
result = validator.check_package("reqests")

print(f"Valid: {result.is_valid}")
print(f"Suggestion: {result.suggestion}")
print(f"Distance: {result.distance}")
```

Output:
```
Valid: False
Suggestion: requests
Distance: 1
```

---

## What Gets Flagged

### Levenshtein Distance ≤ 2

Packages with small edit distance from popular packages:

| Import | Similar To | Distance | Flagged? |
|--------|------------|----------|----------|
| `reqests` | `requests` | 1 | ⚠️ Yes |
| `requets` | `requests` | 2 | ⚠️ Yes |
| `requxsts` | `requests` | 3 | ❌ No |
| `numpyy` | `numpy` | 1 | ⚠️ Yes |
| `pandsa` | `pandas` | 1 | ⚠️ Yes |

### Known Typosquats

Common malicious package names that Ranex blocks:

| Malicious | Real Package |
|-----------|--------------|
| `python-nmap` | `nmap` |
| `python3-nmap` | `nmap` |
| `urllib2` | `urllib3` |
| `opencv-python3` | `opencv-python` |

---

## Popular Packages Database

Ranex checks against a database of 1000+ popular PyPI packages:

- `requests`
- `numpy`
- `pandas`
- `flask`
- `django`
- `fastapi`
- `sqlalchemy`
- `boto3`
- `tensorflow`
- `pytorch`
- `scipy`
- `matplotlib`
- ... and more

---

## Configuration

### Allowlist Custom Packages

If you have legitimate packages that get flagged:

```toml
# .ranex/config.toml
[imports]
allow = [
    "my-reqests",  # Our internal package
    "numpyy-special"
]
```

### Block Specific Packages

```toml
# .ranex/config.toml
[imports]
block = [
    "os.system",
    "eval",
    "exec",
    "__import__"
]
```

---

## Real-World Attacks Prevented

### Case 1: request-files (2017)

Attacker published `request-files` package that looked like `requests` but contained malware.

**Ranex catches this:**
```
⚠️ request-files: SUSPICIOUS
   Did you mean 'requests'? 
```

### Case 2: python-dateutil (2019)

Attacker published `python3-dateutil` to steal SSH keys.

**Ranex catches this:**
```
⚠️ python3-dateutil: SUSPICIOUS
   Did you mean 'python-dateutil'?
```

### Case 3: colors.js incident

Package with similar name contained crypto mining code.

**Ranex catches typosquats before they execute.**

---

## Integration

### CI/CD Check

```yaml
# GitHub Actions
- name: Check Imports
  run: |
    ranex scan --imports-only
    if [ $? -ne 0 ]; then
      echo "Suspicious imports detected!"
      exit 1
    fi
```

### Pre-commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ranex-imports
        name: Check imports
        entry: ranex scan --imports-only
        language: system
        types: [python]
```

---

## API Reference

### ImportValidator Class

```python
from ranex_core import ImportValidator

validator = ImportValidator()
```

### Methods

#### `check_package(name: str) -> ValidationResult`

Check if a package name is valid.

```python
result = validator.check_package("reqests")
```

**Returns:** `ValidationResult` with:
- `is_valid: bool` - True if package is safe
- `suggestion: str | None` - Suggested correct package
- `distance: int` - Levenshtein distance to closest match
- `message: str` - Human-readable message

#### `check_import(import_line: str) -> ValidationResult`

Check an import statement.

```python
result = validator.check_import("import reqests")
result = validator.check_import("from numpyy import array")
```

---

## Handling Flagged Imports

### Option 1: Fix the Typo

```python
# Before
import reqests

# After
import requests
```

### Option 2: Allowlist Legitimate Package

```toml
# .ranex/config.toml
[imports]
allow = ["my-internal-reqests"]
```

### Option 3: Inline Ignore

```python
# ranex: ignore-import
import my_special_reqests
```

---

## Best Practices

### 1. Review All Warnings

Even if a package is legitimate, investigate warnings:

```python
# This might be intentional, but verify!
import python_dateutil  # Is this the right package?
```

### 2. Pin Dependencies

```
# requirements.txt
requests==2.31.0
numpy==1.26.0
pandas==2.1.3
```

### 3. Use Lockfiles

```bash
pip freeze > requirements.lock
```

### 4. Audit New Dependencies

```bash
pip install pipdeptree
pipdeptree --warn fail
```

---

## Troubleshooting

### "False positive on my package"

Add to allowlist:
```toml
[imports]
allow = ["my-reqests"]
```

### "Not detecting known bad package"

Report it! The database is updated regularly.

### "AI keeps generating typos"

Include import validation feedback in AI context:
```
RULE: Always verify imports against pypi.org before suggesting.
Common mistakes: reqests→requests, numpyy→numpy
```

---

## Next Steps

- [Security Scanning](./12-SECURITY-SCANNING.md) - Vulnerability detection
- [Architecture](./13-ARCHITECTURE.md) - Layer enforcement
- [MCP Tools](./21-MCP-TOOLS.md) - AI integration

