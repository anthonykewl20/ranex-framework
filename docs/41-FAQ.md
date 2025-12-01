# Frequently Asked Questions

---

## General

### What is Ranex?

Ranex is an **AI-native governance framework** that makes AI-generated code production-ready. It provides:
- State machine validation
- Security scanning
- Import validation
- Architecture enforcement

### Why do I need Ranex?

AI generates code with three problems:
1. **Logic Drift** - Skips business rules (Ranex enforces state machines)
2. **Hallucination** - Imports fake packages (Ranex detects typosquatting)
3. **Security Issues** - Writes vulnerable code (Ranex scans for vulnerabilities)

### Is Ranex a replacement for FastAPI/Django?

No! Ranex sits **alongside** your web framework. It adds governance, not replacement.

```python
# FastAPI + Ranex work together
from fastapi import FastAPI
from ranex import Contract

app = FastAPI()

@Contract(feature="orders")  # Ranex decorator
@app.post("/orders/{id}/confirm")  # FastAPI decorator
async def confirm_order(id: str, *, _ctx=None):
    _ctx.transition("Confirmed")
    return {"status": "confirmed"}
```

---

## State Machines

### Why use YAML for state machines?

1. **Human-readable** - Business analysts can review
2. **Version-controlled** - Track changes in git
3. **AI-readable** - Inject into prompts
4. **Runtime-enforced** - Validated at execution

### Can I have multiple state machines per feature?

Not in Community Edition. One feature = one state machine.

Team Edition supports multiple state machines per feature.

### How do I handle complex workflows?

Keep state machines simple. Handle complexity in code:

```yaml
# Keep state machine simple
states:
  Pending: {}
  Processing: {}
  Complete: { terminal: true }
  Failed: { terminal: true }
```

```python
# Handle complexity in code
@Contract(feature="orders")
async def process_order(order_id: str, *, _ctx=None):
    _ctx.transition("Processing")
    
    # Complex logic here
    if requires_review(order):
        await send_to_review(order)
    elif requires_approval(order):
        await request_approval(order)
    else:
        await process_normally(order)
    
    _ctx.transition("Complete")
```

### Why doesn't state persist between function calls?

**By design.** Each @Contract call gets a fresh state machine for thread safety.

**Sync with your database:**
```python
@Contract(feature="orders")
async def ship_order(order_id: str, *, _ctx=None):
    order = await db.get(order_id)
    _ctx.current_state = order.status  # Sync!
    _ctx.transition("Shipped")
```

---

## Security

### What vulnerabilities does Community Edition detect?

7 patterns:
1. SQL Injection
2. Hardcoded Secrets
3. Command Injection
4. Weak Cryptography (MD5, SHA1)
5. Insecure Deserialization (pickle)
6. Path Traversal
7. Insecure Random

Team Edition adds 23+ more patterns.

### Can I add custom security patterns?

Not in Community Edition. Team Edition supports custom patterns.

### Does Ranex replace security audits?

No! Ranex is a **first line of defense**. You should still:
- Conduct security audits
- Use SAST/DAST tools
- Perform penetration testing
- Review code manually

---

## Performance

### What's the performance overhead?

| Operation | Latency |
|-----------|---------|
| State transition | **71ns** |
| Security scan (per file) | ~10ms |
| Import validation | ~1ms |

Total overhead is typically <1% of API response time.

### Is Ranex suitable for high-traffic production?

Yes. The Rust core is optimized for performance:
- State machines: 71ns per transition
- No memory allocations in hot path
- Thread-safe without locks

### Does scanning slow down my build?

Scanning adds ~1-2 seconds for typical projects (1000 files). Run in parallel with tests:

```yaml
# CI/CD - run in parallel
jobs:
  test:
    - pytest
  scan:
    - ranex scan
```

---

## Integration

### Does Ranex work with async/await?

Yes! @Contract supports both sync and async:

```python
@Contract(feature="orders")
async def async_function(order_id: str, *, _ctx=None):
    _ctx.transition("Confirmed")
    return result

@Contract(feature="orders")
def sync_function(order_id: str, *, _ctx=None):
    _ctx.transition("Confirmed")
    return result
```

### Can I use Ranex with Django?

Yes! @Contract works with any Python function:

```python
# Django view
from ranex import Contract

@Contract(feature="orders")
def confirm_order_view(request, order_id, *, _ctx=None):
    _ctx.transition("Confirmed")
    return JsonResponse({"status": "confirmed"})
```

### Does Ranex work with Celery?

Yes! State machines work with background tasks:

```python
from celery import shared_task
from ranex import Contract

@shared_task
@Contract(feature="orders")
def process_order_task(order_id: str, *, _ctx=None):
    order = db.get(order_id)
    _ctx.current_state = order.status
    _ctx.transition("Processing")
    # Process order
```

---

## MCP & AI Integration

### What AI assistants does Ranex support?

Any MCP-compatible assistant:
- Claude Desktop
- Cursor
- Any custom MCP client

### Do I need MCP to use Ranex?

No! MCP is optional. You can use Ranex purely via Python API and CLI.

MCP adds real-time AI integration during code generation.

### Can AI bypass Ranex checks?

No. Ranex validates at **runtime**. Even if AI generates invalid code, Ranex will reject it when executed.

---

## Licensing & Pricing

### Is Community Edition really free?

Yes! Free forever for:
- Personal projects
- Commercial projects
- Open source

### What's in Team Edition?

| Feature | Community | Team |
|---------|:---------:|:----:|
| SAST Patterns | 7 | 30+ |
| MCP Tools | 10 | 43 |
| CLI Commands | 8 | 22 |
| RAG Search | TF-IDF | Semantic |
| ARBITER | ❌ | ✅ |
| Drift Detection | ❌ | ✅ |
| Priority Support | ❌ | ✅ |

### How do I upgrade?

Contact sales@ranex.dev

---

## Troubleshooting

### Where can I get help?

1. **Documentation:** You're reading it!
2. **Troubleshooting:** [40-TROUBLESHOOTING.md](./40-TROUBLESHOOTING.md)
3. **GitHub Issues:** Report bugs
4. **Discord:** Community support
5. **Team Edition:** Priority support included

### I found a bug. How do I report it?

Open a GitHub issue with:
1. Ranex version (`pip show ranex_core`)
2. Python version
3. OS
4. Steps to reproduce
5. Expected vs actual behavior

---

## Next Steps

- [Troubleshooting](./40-TROUBLESHOOTING.md) - Common issues
- [Upgrade to Team](./42-UPGRADE-TO-TEAM.md) - Team Edition features

