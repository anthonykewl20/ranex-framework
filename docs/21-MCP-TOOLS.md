# MCP Tools Reference

MCP (Model Context Protocol) tools allow AI assistants like Claude, Cursor, and Copilot to use Ranex features during code generation.

---

## What is MCP?

MCP is a protocol that lets AI assistants use external tools. When you ask Claude to "validate this state transition," it can call Ranex's `validate_transition` tool directly.

---

## Setup

### For Cursor

1. Copy the MCP binary:
```bash
sudo cp ranex_mcp /usr/local/bin/
# or
cp ranex_mcp ~/.local/bin/
```

2. Create `.cursor/mcp.json` in your project:
```json
{
  "mcpServers": {
    "ranex": {
      "command": "/usr/local/bin/ranex_mcp",
      "args": [],
      "env": {
        "RANEX_APP_DIR": "./app"
      }
    }
  }
}
```

3. Restart Cursor.

### For Claude Desktop

Add to `~/.config/claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ranex": {
      "command": "/usr/local/bin/ranex_mcp"
    }
  }
}
```

---

## Community Edition Tools (10)

| Tool | Purpose |
|------|---------|
| `validate_file_structure` | Architecture validation |
| `validate_transition` | State machine checks |
| `check_import` | Import security |
| `security_scan` | SAST scanning |
| `detect_antipattern` | Code smell detection |
| `list_db_aliases` | Database configuration |
| `validate_sql` | SQL validation |
| `validate_intent` | Ambiguity detection |
| `check_function_exists` | Semantic search |
| `get_active_persona` | View persona |

---

## Tool Reference

### validate_file_structure

Validates that a file follows architecture rules.

**Input:**
```json
{
  "file_path": "app/features/orders/routes.py"
}
```

**Output:**
```json
{
  "valid": true,
  "violations": [],
  "suggestions": []
}
```

**Example violations:**
```json
{
  "valid": false,
  "violations": [
    {
      "line": 15,
      "message": "Route layer directly imports database",
      "suggestion": "Use service layer instead"
    }
  ]
}
```

---

### validate_transition

Checks if a state transition is valid.

**Input:**
```json
{
  "feature": "orders",
  "from_state": "Pending",
  "to_state": "Shipped"
}
```

**Output (invalid):**
```json
{
  "valid": false,
  "current_state": "Pending",
  "requested_state": "Shipped",
  "allowed_transitions": ["Confirmed", "Cancelled"],
  "message": "Cannot transition from 'Pending' to 'Shipped'. Must go through: Confirmed → Processing → Shipped"
}
```

**Output (valid):**
```json
{
  "valid": true,
  "current_state": "Pending",
  "requested_state": "Confirmed",
  "allowed_transitions": ["Confirmed", "Cancelled"]
}
```

---

### check_import

Validates an import for typosquatting.

**Input:**
```json
{
  "package_name": "reqests"
}
```

**Output:**
```json
{
  "valid": false,
  "is_suspicious": true,
  "suggestion": "requests",
  "levenshtein_distance": 1,
  "message": "Did you mean 'requests'? This looks like a typosquatted package."
}
```

---

### security_scan

Scans code for security vulnerabilities.

**Input:**
```json
{
  "file_path": "app/features/orders/service.py"
}
```

**Output:**
```json
{
  "secure": false,
  "violations": [
    {
      "line": 45,
      "pattern": "sql_injection",
      "severity": "high",
      "message": "Potential SQL injection: f-string in query",
      "code": "query = f\"SELECT * FROM orders WHERE id = {order_id}\""
    }
  ],
  "scan_time_ms": 12
}
```

**Patterns (Community Edition):**
- `sql_injection`
- `hardcoded_secret`
- `command_injection`
- `weak_crypto`
- `insecure_deserialization`
- `path_traversal`
- `insecure_random`

---

### detect_antipattern

Detects code smells and antipatterns.

**Input:**
```json
{
  "file_path": "app/features/orders/service.py"
}
```

**Output:**
```json
{
  "antipatterns": [
    {
      "line": 23,
      "type": "magic_number",
      "message": "Magic number 0.0825 - consider using a named constant",
      "suggestion": "TAX_RATE = 0.0825"
    },
    {
      "line": 67,
      "type": "print_statement",
      "message": "Print statement in production code",
      "suggestion": "Use logging instead"
    }
  ]
}
```

**Patterns (Community Edition):**
- `god_class` - Class over 500 LOC
- `magic_number` - Unexplained numeric literals
- `print_statement` - Print in production
- `bare_except` - Except without type
- `mutable_default` - Mutable default arguments

---

### list_db_aliases

Lists configured database aliases.

**Input:**
```json
{}
```

**Output:**
```json
{
  "aliases": {
    "primary": "postgresql://localhost/main",
    "replica": "postgresql://localhost/replica",
    "sqlite": "./data/app.db"
  },
  "detected": ["sqlite"]
}
```

---

### validate_sql

Validates a SQL query.

**Input:**
```json
{
  "query": "SELECT id, name FROM users WHERE status = 'active'"
}
```

**Output:**
```json
{
  "valid": true,
  "query_type": "SELECT",
  "tables": ["users"],
  "columns": ["id", "name"],
  "conditions": ["status = 'active'"]
}
```

**Invalid query:**
```json
{
  "valid": false,
  "error": "Syntax error at position 7: unexpected token 'FORM'",
  "suggestion": "Did you mean 'FROM'?"
}
```

---

### validate_intent

Detects ambiguous or unclear code intent.

**Input:**
```json
{
  "code": "def process(data):\n    return data * 2",
  "context": "order processing"
}
```

**Output:**
```json
{
  "clear": false,
  "ambiguities": [
    {
      "type": "vague_function_name",
      "message": "'process' is too generic for order processing",
      "suggestion": "Consider 'process_order' or 'calculate_order_total'"
    },
    {
      "type": "unclear_operation",
      "message": "'data * 2' meaning unclear in order context",
      "suggestion": "Add comment explaining why multiplying by 2"
    }
  ]
}
```

---

### check_function_exists

Searches for existing functions (TF-IDF based).

**Input:**
```json
{
  "query": "calculate tax"
}
```

**Output:**
```json
{
  "found": true,
  "matches": [
    {
      "function": "calculate_tax",
      "file": "app/commons/math_utils.py",
      "line": 15,
      "signature": "def calculate_tax(amount: float, rate: float) -> float",
      "similarity": 0.95
    },
    {
      "function": "apply_tax_rate",
      "file": "app/features/payments/service.py",
      "line": 45,
      "signature": "def apply_tax_rate(subtotal: Decimal) -> Decimal",
      "similarity": 0.72
    }
  ]
}
```

**Note:** Community Edition uses TF-IDF. Team Edition uses RAG with semantic embeddings.

---

### get_active_persona

Gets the currently active AI persona.

**Input:**
```json
{}
```

**Output:**
```json
{
  "active_persona": "python_engineer",
  "role": "Senior Python Engineer",
  "capabilities": [
    "Python development",
    "FastAPI integration",
    "Database design"
  ],
  "boundaries": [
    "Do not modify infrastructure",
    "Do not change security settings"
  ]
}
```

**Note:** Community Edition is read-only. Team Edition can set personas.

---

## Usage Examples

### Example 1: Before Code Generation

Ask Claude: *"Check if I can transition an order from Pending to Shipped"*

Claude calls:
```json
{
  "tool": "validate_transition",
  "feature": "orders",
  "from_state": "Pending",
  "to_state": "Shipped"
}
```

Response informs Claude this is invalid, so it generates correct code:
```python
# Correct path: Pending → Confirmed → Processing → Shipped
_ctx.transition("Confirmed")
_ctx.transition("Processing")
_ctx.transition("Shipped")
```

### Example 2: During Code Review

Ask Claude: *"Scan this file for security issues"*

Claude calls:
```json
{
  "tool": "security_scan",
  "file_path": "app/features/orders/service.py"
}
```

Claude reports findings and suggests fixes.

### Example 3: Finding Existing Code

Ask Claude: *"Do we have a function to calculate tax?"*

Claude calls:
```json
{
  "tool": "check_function_exists",
  "query": "calculate tax"
}
```

Claude finds `calculate_tax` in `commons/math_utils.py` and uses it instead of creating a duplicate.

---

## Team Edition Tools (33 Additional)

| Category | Tools |
|----------|-------|
| **ARBITER** | `validate_test_coverage`, `check_mutation_score`, `detect_tautological_tests`, `get_arbiter_report`, `run_mutation_test` |
| **Drift** | `create_spec_snapshot`, `check_drift`, `get_drift_report`, `compare_snapshots`, `list_snapshots` |
| **RAG** | `semantic_search`, `index_function`, `get_similar_code`, `explain_function` |
| **Governance** | `check_phase_gate`, `transition_phase`, `get_governance_status`, `validate_compliance` |
| **Persona** | `set_persona`, `list_personas`, `validate_response`, `get_persona_boundaries` |
| **Security** | `deep_security_scan`, `get_cve_info`, `check_dependency_vulnerabilities` |
| **Compliance** | `generate_audit_report`, `verify_attestation`, `list_attestations` |
| **Spec** | `parse_requirements`, `validate_implementation`, `generate_tests_from_spec` |

Contact sales@ranex.dev for Team Edition.

---

## Next Steps

- [Python API Reference](./22-PYTHON-API.md) - Direct Python usage
- [CLI Reference](./20-CLI-REFERENCE.md) - CLI commands

