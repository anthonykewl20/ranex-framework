# Ranex Community Edition

**AI-Native Governance Framework for Python**

> Making AI-generated code production-ready.

---

## 🎁 What's Included (FREE)

### ✅ 20 Features Included

| Category | Features |
|----------|----------|
| **Workflow Management** | Phase Management, Status Tracking, Phase Transitions |
| **Security Scanning** | SAST Scanner (7 patterns), Antipattern Detection (5 patterns), Import Validation, Structure Sentinel |
| **Architecture** | Layer Enforcement, Architecture Reports |
| **State Machine** | YAML-based State Machine Validation (71ns latency) |
| **Database** | Schema Discovery, SQL Validation |
| **MCP Tools** | 10 tools for AI integration |
| **CLI Commands** | 13+ commands |
| **Python Package** | @Contract Decorator, Auto-Rollback |

---

## 🚀 Quick Start

### Installation

```bash
# Run the installer (creates virtual environment)
./install.sh

# Activate the virtual environment
source .venv/bin/activate
```

Or manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ranex_core-0.0.1-cp312-cp312-manylinux_2_39_x86_64.whl
```

### Initialize Your Project

```bash
cd your-project
ranex init
ranex scan
```

### Use in Your Code

```python
from ranex import Contract

@Contract(feature="orders")
async def process_order(order_data, *, _ctx=None):
    """
    State Machine enforced: Pending → Confirmed → Processing → Shipped → Delivered
    """
    _ctx.transition("Confirmed")
    # ... your business logic
    return {"status": "confirmed"}
```

---

## 📦 What's in This Package

```
community-edition/
├── ranex_core-*.whl          # Rust core + Python package (PyO3)
├── ranex_mcp                 # MCP Server binary (21MB)
├── ranex-cli                 # CLI binary (4MB)
├── ranex/                    # Python source (bundled in wheel)
│   ├── __init__.py          # @Contract decorator
│   ├── cli.py               # CLI commands
│   ├── errors.py            # Error types
│   ├── logging.py           # Logging utilities
│   ├── simulation.py        # Holodeck simulation
│   └── templates.py         # Project templates
├── docs/                    # Documentation (20 guides)
├── mcp_config.json          # MCP configuration template
├── MCP_SETUP.md             # MCP setup guide
├── README.md                # This file
├── QUICK_START.md           # 5-minute guide
├── install.sh               # Easy installer (creates venv)
└── LICENSE                  # MIT License
```

---

## 🔧 Community Edition Features

### 1. State Machine Validation

Prevent AI from skipping business logic steps:

```yaml
# app/features/orders/state.yaml
feature: orders
initial_state: Pending

states:
  Pending: { description: "New order" }
  Confirmed: { description: "Order confirmed" }
  Processing: { description: "Being prepared" }
  Shipped: { description: "In transit" }
  Delivered: { description: "Completed", terminal: true }
  Cancelled: { description: "Cancelled", terminal: true }

transitions:
  - { from: Pending, to: Confirmed }
  - { from: Pending, to: Cancelled }
  - { from: Confirmed, to: Processing }
  - { from: Processing, to: Shipped }
  - { from: Shipped, to: Delivered }
```

**What happens when AI violates rules:**
```
StateTransitionError: [orders] 🛑 ILLEGAL STATE TRANSITION
  Current State: Pending
  Attempted: Pending → Delivered
  Allowed: Pending → [Confirmed, Cancelled]
```

### 2. Security Scanning (7 Patterns)

```bash
ranex scan
```

Detects:
- SQL Injection
- Command Injection (os.system)
- Hardcoded Secrets
- Weak Cryptography (MD5, SHA1)
- Insecure Deserialization (pickle)
- Path Traversal
- Insecure Random

### 3. Import Validation (Typosquatting)

```python
from ranex_core import ImportValidator

validator = ImportValidator()
result = validator.check_package("reqests")  # Flags typosquat!
```

### 4. CLI Commands

```bash
ranex init          # Initialize project
ranex scan          # Security + architecture scan
ranex arch          # Architecture validation
ranex fix           # Auto-remediation
ranex doctor        # Health check
ranex task          # Workflow management (status/design/build)
ranex context       # Generate AI alignment prompts
ranex verify        # Holodeck simulation testing
ranex db            # Database utilities
ranex graph         # Generate Mermaid diagrams
ranex bench         # Performance benchmarks
ranex stress        # Stress testing
ranex update-rules  # Refresh AI governance rules
```

### 5. MCP Server (AI Integration)

The `ranex_mcp` binary provides 10 tools for AI assistants:

```bash
# Install MCP server
cp ranex_mcp /usr/local/bin/

# Add to Cursor (.cursor/mcp.json)
{
  "mcpServers": {
    "ranex": {
      "command": "/usr/local/bin/ranex_mcp"
    }
  }
}
```

**Community Edition MCP Tools:**
- `validate_file_structure` - Architecture validation
- `validate_transition` - State machine checks
- `check_import` - Typosquatting detection
- `security_scan` - SAST (7 patterns)
- `detect_antipattern` - Code smells (5 patterns)
- `list_db_aliases` - Database config
- `validate_sql` - SQL validation
- `validate_intent` - Ambiguity detection
- `check_function_exists` - Semantic search (TF-IDF)
- `get_active_persona` - View persona

See [MCP_SETUP.md](./MCP_SETUP.md) for full setup guide.

---

## ⬆️ Upgrade to Team Edition

Need more? Team Edition includes:

| Feature | Community | Team |
|---------|:---------:|:----:|
| SAST Patterns | 7 | 30+ |
| Antipatterns | 5 | 15+ |
| MCP Tools | 10 | 43 |
| CLI Commands | 13 | 22+ |
| RAG Semantic Search | ❌ | ✅ |
| ARBITER Test Validation | ❌ | ✅ |
| Drift Detection | ❌ | ✅ |
| Persona Enforcement | ❌ | ✅ |
| Advanced Audit Trail | ❌ | ✅ |

Contact: [sales@ranex.dev](mailto:sales@ranex.dev)

---

## 📄 License

MIT License - Use freely in personal and commercial projects.

---

## 🆘 Support

- Documentation: [ranex.dev/docs](https://ranex.dev/docs)
- Issues: [GitHub Issues](https://github.com/anthonykewl20/ranex-framework/issues)

---

**Ranex v0.0.1 Community Edition**
© 2025 Ranex Project

