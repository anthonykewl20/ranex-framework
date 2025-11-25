# Ranex MCP Server Setup Guide

**Pre-Release-v0.1** - Complete setup guide for Ranex MCP Server

---

## 🎯 Quick Start

The MCP binary is **already built and included** in Pre-Release-v0.1. You don't need to build it!

1. **Verify binary exists:**
   ```bash
   cd Pre-Release-v0.1
   ls -lh bin/ranex_mcp
   ```

2. **Configure your IDE** (see sections below)

3. **Restart your IDE completely**

4. **Verify** - You should see 11 Ranex tools available

---

## 📦 What's Included

- **Binary:** `Pre-Release-v0.1/bin/ranex_mcp` (~17MB)
- **Version:** 0.0.1
- **Platform:** Linux x86_64
- **Status:** ✅ Pre-built and ready

---

## 🔧 WindSurf Setup

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

**Alternative (relative path from project root):**
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
3. You should see **11 tools** available (see [Tools List](#-available-tools))

---

## 🔧 Cursor Setup

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

**Alternative (relative path from project root):**
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
3. You should see **11 tools** available (see [Tools List](#-available-tools))

---

## 🔧 Claude Desktop Setup

### Location:
Edit: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)  
Or: `%APPDATA%\Claude\claude_desktop_config.json` (Windows)  
Or: `~/.config/Claude/claude_desktop_config.json` (Linux)

### Configuration:
```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/absolute/path/to/Pre-Release-v0.1/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "/absolute/path/to/your/project"
      }
    }
  }
}
```

**Note:** Claude Desktop requires absolute paths (no `${workspaceFolder}`)

### Verify:
1. Restart Claude Desktop
2. Check MCP status
3. Should see Ranex tools available

---

## 🔧 VS Code with Continue Setup

### Location:
Edit: `~/.continue/config.json`

### Configuration:
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

---

## 🎯 What You Should See

After setup, your IDE should show:

### Server Info:
- **Name:** Ranex AI Governance Framework
- **Version:** 0.0.1
- **Description:** Full architecture details

### 11 Available Tools:
See [Available Tools](#-available-tools) section below for complete list.

---

## 🛠️ Available Tools

### 1. **Validate File Structure**
**Purpose:** Enforce architectural rules (4-file structure, forbidden folders)

**When to use:** Before creating new files or when refactoring

**Example usage:**
- AI agent: "Create a new payment feature"
- Tool validates: File structure complies with Ranex architecture
- Result: ✅ Allowed or ❌ Rejected with specific violations

---

### 2. **Validate Intent**
**Purpose:** Clarify ambiguous feature requests from AI agents

**When to use:** When AI agent requests a new feature

**Example usage:**
- AI agent: "Build auth system"
- Tool validates: Checks for ambiguity in the request
- Result: ✅ Accepted or ❌ Rejected with clarifying questions

---

### 3. **Check Function Exists**
**Purpose:** Prevent code duplication by checking if function already exists

**When to use:** Before implementing new functions

**Example usage:**
- AI agent: "Create a function to process payments"
- Tool checks: Searches codebase for similar functions
- Result: ✅ Function doesn't exist or ⚠️ Similar function found

---

### 4. **List Database Aliases**
**Purpose:** Show configured database connections and aliases

**When to use:** When working with database operations

**Example usage:**
- AI agent: "What databases are available?"
- Tool lists: All configured database aliases
- Result: List of database aliases (e.g., `primary`, `secondary`)

---

### 5. **Validate SQL Query**
**Purpose:** Prevent SQL errors by validating queries against database schema

**When to use:** Before executing SQL queries

**Example usage:**
- AI agent: "SELECT * FROM users WHERE id = 1"
- Tool validates: Checks query syntax and schema compatibility
- Result: ✅ Valid or ❌ Invalid with error details

---

### 6. **Validate Transition**
**Purpose:** Validate state machine transitions

**When to use:** When implementing state transitions in features

**Example usage:**
- AI agent: "Transition payment from 'Pending' to 'Processing'"
- Tool validates: Checks if transition is allowed
- Result: ✅ Valid transition or ❌ Invalid transition

---

### 7. **Check Import**
**Purpose:** Validate imports and detect typosquatting

**When to use:** When adding new package imports

**Example usage:**
- AI agent: "Import requests library"
- Tool checks: Validates package name and detects typosquatting
- Result: ✅ Safe import or ⚠️ Potential typosquatting detected

---

### 8. **Security Scan**
**Purpose:** Static Application Security Testing (SAST)

**When to use:** When reviewing code for security vulnerabilities

**Example usage:**
- AI agent: "Scan this code for security issues"
- Tool scans: Detects SQL injection, XSS, hardcoded secrets, etc.
- Result: List of security issues with severity levels

---

### 9. **Detect Antipattern**
**Purpose:** Detect code quality issues and antipatterns

**When to use:** When reviewing code quality

**Example usage:**
- AI agent: "Check this code for antipatterns"
- Tool detects: Mutable defaults, bare excepts, unused imports, etc.
- Result: List of antipatterns with suggestions

---

### 10. **Scan Dependencies**
**Purpose:** Scan project dependencies for known vulnerabilities

**When to use:** When checking project security

**Example usage:**
- AI agent: "Check dependencies for vulnerabilities"
- Tool scans: Uses OSV database to check for known vulnerabilities
- Result: List of vulnerable dependencies with CVE information

---

### 11. **Check Circular Imports**
**Purpose:** Detect circular import dependencies

**When to use:** When debugging import issues or refactoring

**Example usage:**
- AI agent: "Check for circular imports"
- Tool checks: Builds import graph and detects cycles
- Result: ✅ No cycles or ❌ Cycles detected with path details

---

## 🐛 Troubleshooting

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

### Tools Not Showing Up?

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

### Old Configuration Showing?

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

### Environment Variables Not Working?

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

---

## 📚 Advanced Configuration

### Multiple Databases:
```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/path/to/bin/ranex_mcp",
  "env": {
    "RANEX_PROJECT_ROOT": "${workspaceFolder}",
    "RANEX_DB_ALIASES": "primary,secondary",
    "RANEX_DB_PRIMARY_URL": "postgresql://localhost/mydb",
    "RANEX_DB_SECONDARY_URL": "sqlite://cache.db"
      }
    }
  }
}
```

### Custom Database:
```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/path/to/bin/ranex_mcp",
  "env": {
    "RANEX_PROJECT_ROOT": "${workspaceFolder}",
    "RANEX_DB_PRIMARY_URL": "mysql://user:pass@localhost/db"
      }
    }
  }
}
```

**Note:** Database auto-detection works for most cases. Only specify if you have custom setup.

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `RANEX_PROJECT_ROOT` | Path to your project root | Yes | `.` (current directory) |
| `RANEX_DB_ALIASES` | Comma-separated database aliases | No | `primary` |
| `RANEX_DB_PRIMARY_URL` | Primary database connection URL | No | Auto-detected |
| `RANEX_DB_{ALIAS}_URL` | Database URL for specific alias | No | - |

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Binary exists: `ls -lh Pre-Release-v0.1/bin/ranex_mcp`
- [ ] Binary is executable: `chmod +x bin/ranex_mcp`
- [ ] Config file is valid JSON
- [ ] Config uses absolute path (or relative from project root)
- [ ] IDE restarted completely
- [ ] Server name shows: "Ranex AI Governance Framework"
- [ ] Version shows: "0.0.1"
- [ ] 11 tools visible:
  - [ ] Validate File Structure
  - [ ] Validate Intent
  - [ ] Check Function Exists
  - [ ] List Database Aliases
  - [ ] Validate SQL Query
  - [ ] Validate Transition
  - [ ] Check Import
  - [ ] Security Scan
  - [ ] Detect Antipattern
  - [ ] Scan Dependencies
  - [ ] Check Circular Imports

---

## 🎉 Success!

If you see all 11 tools, you're ready to use Ranex!

**Next:** Start coding and let Ranex enforce your architecture automatically.

**See also:**
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference guide
- [bin/README.md](../../bin/README.md) - Binary details
- [API_REFERENCE.md](../API_REFERENCE.md) - Complete API documentation

---

**Need help?** Check the main documentation or open an issue.

**Last Updated:** 2025-01-27  
**Pre-Release Version:** 0.0.1
