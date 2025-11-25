# Ranex MCP Server Binary

**File:** `bin/ranex_mcp`  
**Version:** 0.0.1  
**Size:** ~17MB  
**Platform:** Linux x86_64  
**Status:** ✅ Pre-built and ready to use

---

## What is ranex_mcp?

`ranex_mcp` is the **Micro-Context Protocol (MCP) server** for Ranex Framework. It provides AI agents (like those in WindSurf and Cursor) with tools to:

1. **Validate File Structure** - Enforce architectural rules
2. **Validate Intent** - Clarify ambiguous feature requests
3. **Check Function Exists** - Prevent code duplication
4. **List Database Aliases** - Show database connections
5. **Validate SQL Query** - Prevent SQL errors

---

## Quick Start

The MCP binary is **already built and included** in Pre-Release-v0.1. You don't need to build it!

### Verify Binary Exists

```bash
cd Pre-Release-v0.1
ls -lh bin/ranex_mcp
```

**Expected output:**
```
-rwxr-xr-x 1 user user 17M Nov 25 18:37 bin/ranex_mcp
```

### Make Executable (if needed)

```bash
chmod +x bin/ranex_mcp
```

### Test the Binary

```bash
./bin/ranex_mcp
```

**Expected:** The server starts and waits for MCP client connections. Press `Ctrl+C` to stop.

---

## WindSurf Setup

### Step 1: Locate Configuration File

**Global configuration (recommended):**
```bash
~/.windsurf/mcp_config.json
```

**Project-specific configuration:**
```bash
.windsurf/mcp_config.json  # In your project root
```

### Step 2: Create/Edit Configuration

Create or edit the configuration file:

```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/absolute/path/to/Pre-Release-v0.1/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

**Important:** Use the **absolute path** to `ranex_mcp` binary.

**Example (Linux):**
```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/home/user/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

**Example (if using relative path from project root):**
```json
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
```

### Step 3: Restart WindSurf

1. **Completely quit WindSurf** (not just reload)
2. **Restart WindSurf**
3. Open your project

### Step 4: Verify Setup

1. Open the **MCP panel** in WindSurf
2. Look for **"Ranex AI Governance Framework"**
3. You should see **5 tools** available:
   - Validate File Structure
   - Validate Intent
   - Check Function Exists
   - List Database Aliases
   - Validate SQL Query

---

## Cursor Setup

### Step 1: Locate Configuration File

**Global configuration (recommended):**
```bash
~/.cursor/mcp_config.json
```

**Project-specific configuration:**
```bash
.cursor/mcp_config.json  # In your project root
```

### Step 2: Create/Edit Configuration

Create or edit the configuration file:

```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/absolute/path/to/Pre-Release-v0.1/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

**Important:** Use the **absolute path** to `ranex_mcp` binary.

**Example (Linux):**
```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/home/user/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

**Example (if using relative path from project root):**
```json
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
```

### Step 3: Restart Cursor

1. **Completely quit Cursor** (not just reload)
2. **Restart Cursor**
3. Open your project

### Step 4: Verify Setup

1. Open **MCP settings** in Cursor
2. Look for **"Ranex AI Governance Framework"**
3. You should see **5 tools** available:
   - Validate File Structure
   - Validate Intent
   - Check Function Exists
   - List Database Aliases
   - Validate SQL Query

---

## Configuration Details

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `RANEX_PROJECT_ROOT` | Path to your project root | Yes | `.` (current directory) |
| `RANEX_DB_ALIASES` | Comma-separated database aliases | No | `primary` |
| `RANEX_DB_PRIMARY_URL` | Primary database connection URL | No | Auto-detected |
| `RANEX_DB_{ALIAS}_URL` | Database URL for specific alias | No | - |

### Path Configuration

**Option 1: Absolute Path (Recommended)**
```json
{
  "command": "/home/user/projects/ranex/Pre-Release-v0.1/bin/ranex_mcp"
}
```

**Option 2: Relative Path from Project Root**
```json
{
  "command": "${workspaceFolder}/Pre-Release-v0.1/bin/ranex_mcp"
}
```

**Option 3: Add to PATH**
If you add `Pre-Release-v0.1/bin` to your PATH:
```json
{
  "command": "ranex_mcp"
}
```

---

## Database Configuration (Optional)

The MCP server can auto-detect databases, but you can also configure them explicitly:

### Single Database

```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/path/to/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}",
        "RANEX_DB_PRIMARY_URL": "postgresql://user:pass@localhost/mydb"
      }
    }
  }
}
```

### Multiple Databases

```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/path/to/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}",
        "RANEX_DB_ALIASES": "primary,secondary",
        "RANEX_DB_PRIMARY_URL": "postgresql://localhost/primary",
        "RANEX_DB_SECONDARY_URL": "sqlite://cache.db"
      }
    }
  }
}
```

---

## Troubleshooting

### Binary Not Found

**Error:** `command not found` or `No such file or directory`

**Solutions:**
1. **Check binary exists:**
   ```bash
   ls -lh Pre-Release-v0.1/bin/ranex_mcp
   ```

2. **Use absolute path:**
   ```json
   {
     "command": "/full/absolute/path/to/Pre-Release-v0.1/bin/ranex_mcp"
   }
   ```

3. **Make executable:**
   ```bash
   chmod +x Pre-Release-v0.1/bin/ranex_mcp
   ```

### Tools Not Showing Up

**Symptoms:** MCP server connects but no tools visible

**Solutions:**
1. **Check server version:**
   - Server should show: "Ranex AI Governance Framework v0.0.1"
   - If you see v5.0.0, you're using an old version

2. **Restart IDE completely:**
   - Quit completely (not just reload)
   - Restart IDE

3. **Check IDE logs:**
   - WindSurf: Check MCP panel for errors
   - Cursor: Check MCP settings for errors

4. **Verify JSON syntax:**
   ```bash
   python3 -m json.tool ~/.windsurf/mcp_config.json
   # or
   python3 -m json.tool ~/.cursor/mcp_config.json
   ```

### Environment Variables Not Working

**Symptoms:** `${workspaceFolder}` not resolving

**Solutions:**
1. **Use absolute path for binary:**
   ```json
   {
     "command": "/absolute/path/to/bin/ranex_mcp"
   }
   ```

2. **Set RANEX_PROJECT_ROOT explicitly:**
   ```json
   {
     "env": {
       "RANEX_PROJECT_ROOT": "/absolute/path/to/your/project"
     }
   }
   ```

### Server Crashes on Start

**Symptoms:** MCP server starts then immediately stops

**Solutions:**
1. **Check binary permissions:**
   ```bash
   ls -l bin/ranex_mcp
   chmod +x bin/ranex_mcp
   ```

2. **Test binary directly:**
   ```bash
   ./bin/ranex_mcp
   ```
   Should start and wait for connections. Press Ctrl+C to stop.

3. **Check for missing dependencies:**
   ```bash
   ldd bin/ranex_mcp
   ```
   All libraries should be found.

### Old Configuration Showing

**Symptoms:** Old tools or old version showing

**Solutions:**
1. **Clear IDE cache:**
   ```bash
   rm -rf ~/.windsurf/mcp_cache
   # or
   rm -rf ~/.cursor/mcp_cache
   ```

2. **Restart IDE completely**

3. **Verify config file:**
   - Check you're editing the correct file
   - Verify JSON syntax is valid

---

## Verification Checklist

After setup, verify:

- [ ] Binary exists: `ls -lh bin/ranex_mcp`
- [ ] Binary is executable: `chmod +x bin/ranex_mcp`
- [ ] Config file is valid JSON
- [ ] Config uses absolute path (or relative from project root)
- [ ] IDE restarted completely
- [ ] Server name shows: "Ranex AI Governance Framework"
- [ ] Version shows: "0.0.1"
- [ ] 5 tools visible:
  - [ ] Validate File Structure
  - [ ] Validate Intent
  - [ ] Check Function Exists
  - [ ] List Database Aliases
  - [ ] Validate SQL Query

---

## What the Tools Do

### 1. Validate File Structure
Enforces Ranex architectural rules (4-file structure, forbidden folders, etc.)

### 2. Validate Intent
Validates feature manifests to prevent ambiguous requests from AI agents

### 3. Check Function Exists
Checks if a function already exists in the codebase to prevent duplication

### 4. List Database Aliases
Shows configured database connections and aliases

### 5. Validate SQL Query
Validates SQL queries against database schema to prevent errors

---

## Advanced Usage

### Custom Project Root

If your project structure is different:

```json
{
  "env": {
    "RANEX_PROJECT_ROOT": "/path/to/your/project/root"
  }
}
```

### Multiple MCP Servers

You can run multiple MCP servers alongside Ranex:

```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/path/to/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    },
    "other-server": {
      "command": "/path/to/other/server"
    }
  }
}
```

---

## Platform Compatibility

**Current Binary:**
- **Platform:** Linux x86_64
- **Python:** Not required (standalone binary)
- **Rust:** Not required (pre-compiled)

**For Other Platforms:**
- Windows: Not available in Pre-Release-v0.1
- macOS: Not available in Pre-Release-v0.1
- Other Linux architectures: Not available in Pre-Release-v0.1

**Note:** To build for other platforms, you need the Rust source code and toolchain.

---

## Getting Help

- **Documentation:** See `docs/setup/MCP_SETUP.md` for more details
- **Examples:** See `examples/` for code examples
- **API Reference:** See `docs/API_REFERENCE.md`

---

## Summary

✅ **Binary Location:** `Pre-Release-v0.1/bin/ranex_mcp`  
✅ **Size:** ~17MB  
✅ **Status:** Pre-built and ready  
✅ **Platform:** Linux x86_64  
✅ **Version:** 0.0.1  

**Next Steps:**
1. Configure your IDE (WindSurf or Cursor)
2. Restart IDE
3. Verify tools are available
4. Start using Ranex MCP tools!

---

**Last Updated:** 2025-01-27  
**Pre-Release Version:** 0.0.1
