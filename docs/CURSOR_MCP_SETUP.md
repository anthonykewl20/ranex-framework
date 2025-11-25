# Installing Ranex MCP on Cursor - Step by Step

This guide shows you **exact commands** to install Ranex MCP server in Cursor IDE.

## Prerequisites

1. **Cursor IDE** installed and running
2. **Ranex Framework** downloaded (Pre-Release-v0.1)
3. **Linux x86_64** system (current binary is Linux-only)

## Step-by-Step Installation

### Step 1: Verify Binary Exists

```bash
cd /home/tonyo/projects/ranex/Pre-Release-v0.1
ls -lh bin/ranex_mcp
```

**Expected output:**
```
-rwxr-xr-x 1 user user 17M Nov 25 18:37 bin/ranex_mcp
```

### Step 2: Get Absolute Path to Binary

```bash
realpath bin/ranex_mcp
```

**Save this path** - you'll need it in the next step. Example:
```
/home/tonyo/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp
```

### Step 3: Create Cursor MCP Configuration

**Option A: Global Configuration (Recommended)**

```bash
# Create config directory if it doesn't exist
mkdir -p ~/.cursor

# Create or edit the config file
cat > ~/.cursor/mcp_config.json << 'EOF'
{
  "mcpServers": {
    "ranex-core": {
      "command": "/home/tonyo/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
EOF
```

**Important:** Replace `/home/tonyo/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp` with your actual path from Step 2.

**Option B: Project-Specific Configuration**

```bash
# Create config in project root
cd /home/tonyo/projects/ranex/Pre-Release-v0.1
mkdir -p .cursor

cat > .cursor/mcp_config.json << 'EOF'
{
  "mcpServers": {
    "ranex-core": {
      "command": "/home/tonyo/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
EOF
```

### Step 4: Verify JSON Syntax

```bash
# Check global config
python3 -m json.tool ~/.cursor/mcp_config.json

# Or check project config
python3 -m json.tool .cursor/mcp_config.json
```

**Expected:** Should print the JSON without errors.

### Step 5: Make Binary Executable (if needed)

```bash
chmod +x /home/tonyo/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp
```

### Step 6: Test Binary Manually (Optional)

```bash
# Test the binary starts
/home/tonyo/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp
```

**Expected:** Server starts and waits. Press `Ctrl+C` to stop.

### Step 7: Restart Cursor

**Important:** You must **completely quit** Cursor, not just reload.

```bash
# Quit Cursor completely
# Then restart it from your application menu
```

### Step 8: Verify Installation

1. **Open Cursor**
2. **Open MCP Settings:**
   - Go to Settings → Extensions → MCP
   - Or use Command Palette (Ctrl+Shift+P) → "MCP: Show Servers"
3. **Look for:**
   - Server name: **"Ranex AI Governance Framework"**
   - Version: **"0.0.1"**
   - Status: **Connected** or **Running**

4. **Check Tools Available:**
   You should see 11 tools:
   - Validate File Structure
   - Validate Intent
   - Check Function Exists
   - List Database Aliases
   - Validate SQL Query
   - Validate Transition
   - Check Import
   - Security Scan
   - Detect Antipattern
   - Scan Dependencies
   - Check Circular Imports

## Quick Installation Script

Here's a one-liner to set everything up:

```bash
cd /home/tonyo/projects/ranex/Pre-Release-v0.1 && \
mkdir -p ~/.cursor && \
cat > ~/.cursor/mcp_config.json << EOF
{
  "mcpServers": {
    "ranex-core": {
      "command": "$(realpath bin/ranex_mcp)",
      "env": {
        "RANEX_PROJECT_ROOT": "\${workspaceFolder}"
      }
    }
  }
}
EOF
chmod +x bin/ranex_mcp && \
echo "✅ Configuration created at ~/.cursor/mcp_config.json" && \
echo "📝 Now restart Cursor completely to activate MCP server"
```

## Troubleshooting Commands

### Check if Config File Exists

```bash
ls -lh ~/.cursor/mcp_config.json
```

### View Current Configuration

```bash
cat ~/.cursor/mcp_config.json
```

### Validate JSON Syntax

```bash
python3 -m json.tool ~/.cursor/mcp_config.json
```

### Check Binary Permissions

```bash
ls -l /home/tonyo/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp
```

### Test Binary Directly

```bash
/home/tonyo/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp
```

### Check Binary Dependencies

```bash
ldd /home/tonyo/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp
```

### Clear Cursor Cache (if old config persists)

```bash
rm -rf ~/.cursor/mcp_cache
```

## Configuration File Location

Cursor looks for MCP configuration in this order:

1. **Project-specific:** `.cursor/mcp_config.json` (in project root)
2. **Global:** `~/.cursor/mcp_config.json`

**Recommendation:** Use global config (`~/.cursor/mcp_config.json`) so it works for all projects.

## Using Relative Paths

If you want to use relative paths (from project root):

```bash
cat > ~/.cursor/mcp_config.json << 'EOF'
{
  "mcpServers": {
    "ranex-core": {
      "command": "${workspaceFolder}/Pre-Release-v0.1/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
EOF
```

**Note:** This only works if your project root contains the `Pre-Release-v0.1` directory.

## Verification Checklist

After installation, verify:

- [ ] Binary exists: `ls -lh bin/ranex_mcp`
- [ ] Binary is executable: `chmod +x bin/ranex_mcp`
- [ ] Config file created: `ls -lh ~/.cursor/mcp_config.json`
- [ ] JSON is valid: `python3 -m json.tool ~/.cursor/mcp_config.json`
- [ ] Binary path is correct in config
- [ ] Cursor restarted completely
- [ ] MCP server shows in Cursor settings
- [ ] Server name: "Ranex AI Governance Framework"
- [ ] Version: "0.0.1"
- [ ] 11 tools visible

## What You Should See in Cursor

After successful installation:

1. **MCP Panel** shows:
   - Server: Ranex AI Governance Framework
   - Status: Connected
   - Version: 0.0.1

2. **Available Tools** (11 total):
   - Validate File Structure
   - Validate Intent
   - Check Function Exists
   - List Database Aliases
   - Validate SQL Query
   - Validate Transition
   - Check Import
   - Security Scan
   - Detect Antipattern
   - Scan Dependencies
   - Check Circular Imports

## Next Steps

Once MCP is installed:

1. **Test the tools** - Try asking Cursor to validate file structure
2. **Read documentation** - See `docs/API_REFERENCE.md` for tool details
3. **Use in development** - Let Ranex enforce your architecture automatically

## Common Issues

### Issue: "command not found"

**Solution:**
```bash
# Use absolute path in config
realpath bin/ranex_mcp  # Get absolute path
# Update config with absolute path
```

### Issue: "Permission denied"

**Solution:**
```bash
chmod +x /home/tonyo/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp
```

### Issue: Tools not showing

**Solution:**
```bash
# 1. Verify config
python3 -m json.tool ~/.cursor/mcp_config.json

# 2. Clear cache
rm -rf ~/.cursor/mcp_cache

# 3. Restart Cursor completely
```

### Issue: Server crashes

**Solution:**
```bash
# Test binary directly
./bin/ranex_mcp

# Check dependencies
ldd bin/ranex_mcp
```

---

**Need more help?** See:
- [MCP_SETUP.md](setup/MCP_SETUP.md) - Complete MCP setup guide
- [API_REFERENCE.md](API_REFERENCE.md) - Tool API documentation

