# Troubleshooting

Common issues and solutions.

---

## Installation Issues

### "Python version mismatch"

**Problem:** Wheel requires Python 3.12

**Solution:**
```bash
# Check your version
python3 --version

# Use pyenv to install 3.12
pyenv install 3.12.3
pyenv local 3.12.3

# Or use conda
conda create -n ranex python=3.12
conda activate ranex
```

### "Command not found: ranex"

**Problem:** CLI binary not in PATH

**Solution:**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Make permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "ModuleNotFoundError: No module named 'ranex_core'"

**Problem:** Wheel not installed

**Solution:**
```bash
pip install ranex_core-*.whl

# Verify
pip list | grep ranex
```

---

## State Machine Issues

### "Feature 'X' not found"

**Problem:** State file not found

**Solution:**
1. Check file exists:
```bash
ls -la app/features/orders/state.yaml
```

2. Check path:
```python
import os
print(os.environ.get("RANEX_APP_DIR", "./app"))
# State file should be at: {RANEX_APP_DIR}/features/orders/state.yaml
```

3. Set correct app directory:
```bash
export RANEX_APP_DIR="./src/app"
```

### "Illegal transition from X to Y"

**Problem:** Invalid state transition

**Solution:**
1. Check your state.yaml transitions
2. Verify current database state matches state machine
3. Sync state before transitioning:

```python
@Contract(feature="orders")
async def process_order(order_id: str, *, _ctx=None):
    order = await db.get(order_id)
    
    # IMPORTANT: Sync with database state
    _ctx.current_state = order.status
    
    # Now transition
    _ctx.transition("Processing")
```

### "Cannot transition from terminal state"

**Problem:** Trying to leave a terminal state

**Solution:**
Terminal states (marked `terminal: true`) are final. You cannot transition from them.

Check your state.yaml:
```yaml
states:
  Delivered:
    terminal: true  # Cannot transition from this
```

---

## @Contract Issues

### "_ctx is None"

**Problem:** Context not injected

**Solution:** Make `_ctx` a keyword-only argument:

```python
# WRONG
@Contract(feature="orders")
async def process(order_id, _ctx=None):  # Not keyword-only
    ...

# CORRECT
@Contract(feature="orders")
async def process(order_id, *, _ctx=None):  # Keyword-only (after *)
    ...
```

### "multiple values for argument '_ctx'"

**Problem:** Passing _ctx when calling function

**Solution:** Don't pass _ctx manually, it's injected:

```python
# WRONG
result = await process_order(order_id, _ctx=my_ctx)

# CORRECT
result = await process_order(order_id)  # _ctx is injected
```

### State not persisting between calls

**Problem:** Each call creates new state machine

**This is by design.** Each @Contract call gets a fresh state machine starting at `initial_state`.

**Solution:** Sync with database:

```python
@Contract(feature="orders")
async def ship_order(order_id: str, *, _ctx=None):
    # Load from database
    order = await db.get(order_id)
    
    # Sync state machine to database state
    _ctx.current_state = order.status  # e.g., "Processing"
    
    # Now transition works correctly
    _ctx.transition("Shipped")
    
    # Update database
    order.status = "Shipped"
    await db.save(order)
```

---

## Security Scanner Issues

### "No violations found" but code is vulnerable

**Problem:** Pattern not detected

**Check:** Community Edition has 7 patterns. Some advanced vulnerabilities require Team Edition.

**Solution:**
```python
# Ensure pattern is detectable
# These ARE detected:
f"SELECT * FROM users WHERE id = {id}"  # SQL injection
os.system(cmd)  # Command injection
API_KEY = "sk-..."  # Hardcoded secret

# These are NOT detected (Team Edition):
# - Blind SQL injection
# - Second-order SQL injection
# - Complex XSS
```

### "False positive"

**Problem:** Clean code flagged as vulnerable

**Solution 1:** Inline ignore
```python
# ranex: ignore-next-line
API_KEY = "test-key-for-development"
```

**Solution 2:** File ignore (.ranex/ignore)
```
tests/
**/test_*.py
```

---

## MCP Issues

### "connection closed: initialized request"

**Problem:** MCP server expects stdio connection

**Solution:** This is normal! MCP communicates via stdio with AI clients. You can't "test" it by running directly.

**To verify it works:**
1. Configure in Cursor/Claude Desktop
2. Ask AI to use a Ranex tool

### AI not using MCP tools

**Problem:** Tools not appearing

**Solution:**
1. Check MCP config:
```json
// .cursor/mcp.json
{
  "mcpServers": {
    "ranex": {
      "command": "/usr/local/bin/ranex_mcp"
    }
  }
}
```

2. Restart Cursor/Claude
3. Check binary path is correct:
```bash
which ranex_mcp
/usr/local/bin/ranex_mcp --help
```

---

## CLI Issues

### "ranex scan" shows no results

**Problem:** Not scanning correct directory

**Solution:**
```bash
# Specify directory
ranex scan ./app

# Or set environment
export RANEX_APP_DIR="./app"
ranex scan
```

### "ranex doctor" shows unhealthy

**Problem:** Configuration issues

**Solution:** Run with verbose:
```bash
ranex doctor --verbose
```

Check each reported issue.

---

## Database Issues

### "Cannot detect database"

**Problem:** No database found

**Solution:**
```bash
# Set explicitly
export RANEX_DB_PRIMARY_URL="sqlite:///./data/app.db"

# Or create a database file
mkdir -p data
touch data/app.db
```

### "Permission denied" on database

**Problem:** Database user lacks permissions

**Solution:**
```sql
-- Grant read permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO your_user;
```

---

## Import Validation Issues

### "Valid package flagged as suspicious"

**Problem:** False positive on legitimate package

**Solution:** Add to allowlist:
```toml
# .ranex/config.toml
[imports]
allow = ["my-internal-reqests"]
```

---

## Performance Issues

### Scans are slow

**Problem:** Scanning too many files

**Solution:** Create .ranex/ignore:
```
node_modules/
.venv/
venv/
__pycache__/
*.pyc
.git/
dist/
build/
*.egg-info/
```

### State transitions seem slow

**Problem:** Not actually slow (71ns)

**Check:** The slowness is likely from:
- Database queries
- External API calls
- File I/O

**Solution:** Profile your code:
```python
import time

start = time.perf_counter_ns()
_ctx.transition("Confirmed")
elapsed = time.perf_counter_ns() - start
print(f"Transition: {elapsed}ns")  # Should be ~71ns
```

---

## Getting Help

### Still stuck?

1. **Run doctor:**
   ```bash
   ranex doctor --verbose
   ```

2. **Check logs:**
   ```bash
   RANEX_LOG_LEVEL=debug ranex scan 2>&1 | head -50
   ```

3. **Community:**
   - GitHub Issues: Report bugs
   - Discord: Ask questions

4. **Team Edition:**
   - Priority support included
   - Contact: sales@ranex.dev

---

## Next Steps

- [FAQ](./41-FAQ.md) - Frequently asked questions
- [Upgrade to Team](./42-UPGRADE-TO-TEAM.md) - Team Edition features

