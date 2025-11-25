# Ranex MCP - Quick Reference

**Pre-Release-v0.1** - Quick reference guide for Ranex MCP Server

---

## ⚡ Quick Setup

### Config Template (Copy-Paste)

**For WindSurf or Cursor:**
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

**Important:** Replace `/absolute/path/to/Pre-Release-v0.1/bin/ranex_mcp` with your actual path!

---

## 📍 Config Locations

| IDE | Config Location |
|-----|----------------|
| **WindSurf** | `~/.windsurf/mcp_config.json` (global) or `.windsurf/mcp_config.json` (project) |
| **Cursor** | `~/.cursor/mcp_config.json` (global) or `.cursor/mcp_config.json` (project) |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)<br>`%APPDATA%\Claude\claude_desktop_config.json` (Windows)<br>`~/.config/Claude/claude_desktop_config.json` (Linux) |
| **VS Code + Continue** | `~/.continue/config.json` |

---

## ✅ Verify Installation

1. **Check binary exists:**
   ```bash
   ls -lh Pre-Release-v0.1/bin/ranex_mcp
   ```

2. **Make executable (if needed):**
```bash
   chmod +x Pre-Release-v0.1/bin/ranex_mcp
   ```

3. **Restart IDE completely**

4. **Look for:** "Ranex AI Governance Framework v0.0.1"

5. **Should see:** 11 tools available

---

## 🛠️ All 11 MCP Tools

### Architecture Tools

#### 1. **Validate File Structure**
**Purpose:** Enforce architectural rules (4-file structure, forbidden folders)

**When to use:**
- Before creating new files
- When refactoring project structure
- To ensure compliance with Ranex architecture

**Example:**
```
AI: "Create a new payment feature"
Tool: Validates file structure
Result: ✅ Allowed or ❌ Rejected with violations
```

---

#### 2. **Validate Intent**
**Purpose:** Clarify ambiguous feature requests from AI agents

**When to use:**
- When AI agent requests a new feature
- To prevent ambiguous implementations
- To ensure clear requirements

**Example:**
```
AI: "Build auth system"
Tool: Checks for ambiguity
Result: ✅ Accepted or ❌ Rejected with clarifying questions
```

---

#### 3. **Check Function Exists**
**Purpose:** Prevent code duplication by checking if function already exists

**When to use:**
- Before implementing new functions
- To avoid duplicate code
- To find existing implementations

**Example:**
```
AI: "Create a function to process payments"
Tool: Searches codebase for similar functions
Result: ✅ Function doesn't exist or ⚠️ Similar function found
```

---

#### 4. **Check Circular Imports**
**Purpose:** Detect circular import dependencies

**When to use:**
- When debugging import issues
- Before refactoring imports
- To prevent circular dependencies

**Example:**
```
AI: "Check for circular imports"
Tool: Builds import graph and detects cycles
Result: ✅ No cycles or ❌ Cycles detected with path details
```

---

### Database Tools

#### 5. **List Database Aliases**
**Purpose:** Show configured database connections and aliases

**When to use:**
- When working with database operations
- To see available databases
- To check database configuration

**Example:**
```
AI: "What databases are available?"
Tool: Lists all configured database aliases
Result: ["primary", "secondary"]
```

---

#### 6. **Validate SQL Query**
**Purpose:** Prevent SQL errors by validating queries against database schema

**When to use:**
- Before executing SQL queries
- To validate query syntax
- To check schema compatibility

**Example:**
```
AI: "SELECT * FROM users WHERE id = 1"
Tool: Validates query syntax and schema
Result: ✅ Valid or ❌ Invalid with error details
```

---

#### 7. **Validate Transition**
**Purpose:** Validate state machine transitions

**When to use:**
- When implementing state transitions
- To ensure valid state changes
- To enforce state machine rules

**Example:**
```
AI: "Transition payment from 'Pending' to 'Processing'"
Tool: Checks if transition is allowed
Result: ✅ Valid transition or ❌ Invalid transition
```

---

### Security Tools

#### 8. **Security Scan**
**Purpose:** Static Application Security Testing (SAST)

**When to use:**
- When reviewing code for security vulnerabilities
- Before committing code
- To detect security issues early

**Detects:**
- SQL injection
- XSS vulnerabilities
- Hardcoded secrets
- Insecure random usage
- And more...

**Example:**
```
AI: "Scan this code for security issues"
Tool: Detects security vulnerabilities
Result: List of issues with severity levels
```

---

#### 9. **Detect Antipattern**
**Purpose:** Detect code quality issues and antipatterns

**When to use:**
- When reviewing code quality
- To improve code standards
- To detect common mistakes

**Detects:**
- Mutable default arguments
- Bare except clauses
- Unused imports
- Code complexity warnings
- And more...

**Example:**
```
AI: "Check this code for antipatterns"
Tool: Detects code quality issues
Result: List of antipatterns with suggestions
```

---

#### 10. **Scan Dependencies**
**Purpose:** Scan project dependencies for known vulnerabilities

**When to use:**
- When checking project security
- Before deploying
- To stay updated on vulnerabilities

**Example:**
```
AI: "Check dependencies for vulnerabilities"
Tool: Uses OSV database to check vulnerabilities
Result: List of vulnerable dependencies with CVE information
```

---

### Import Tools

#### 11. **Check Import**
**Purpose:** Validate imports and detect typosquatting

**When to use:**
- When adding new package imports
- To prevent typosquatting attacks
- To validate package names

**Example:**
```
AI: "Import requests library"
Tool: Validates package name and detects typosquatting
Result: ✅ Safe import or ⚠️ Potential typosquatting detected
```

---

## 📋 Tool Usage Summary

| Tool | Category | When to Use | Key Benefit |
|------|----------|-------------|-------------|
| Validate File Structure | Architecture | Before creating files | Ensures compliance |
| Validate Intent | Architecture | When requesting features | Prevents ambiguity |
| Check Function Exists | Architecture | Before implementing | Prevents duplication |
| Check Circular Imports | Architecture | When debugging imports | Prevents cycles |
| List Database Aliases | Database | When working with DB | Shows available DBs |
| Validate SQL Query | Database | Before executing SQL | Prevents SQL errors |
| Validate Transition | Database | When changing states | Ensures valid transitions |
| Security Scan | Security | When reviewing code | Detects vulnerabilities |
| Detect Antipattern | Security | When reviewing code | Improves code quality |
| Scan Dependencies | Security | When checking security | Finds vulnerabilities |
| Check Import | Security | When adding imports | Prevents typosquatting |

---

## 🎯 Common Use Cases

### Use Case 1: Creating a New Feature

1. **Validate Intent** - Clarify the feature request
2. **Validate File Structure** - Ensure proper structure
3. **Check Function Exists** - Avoid duplicates
4. **Security Scan** - Check for security issues
5. **Detect Antipattern** - Ensure code quality

### Use Case 2: Database Operations

1. **List Database Aliases** - See available databases
2. **Validate SQL Query** - Check query before execution
3. **Validate Transition** - Ensure valid state changes

### Use Case 3: Code Review

1. **Security Scan** - Check for vulnerabilities
2. **Detect Antipattern** - Find code quality issues
3. **Scan Dependencies** - Check for vulnerable packages
4. **Check Circular Imports** - Detect import issues

### Use Case 4: Adding Dependencies

1. **Check Import** - Validate package name
2. **Scan Dependencies** - Check for vulnerabilities
3. **Security Scan** - Review code after adding

---

## 🔧 Configuration Examples

### Basic Configuration
```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/path/to/Pre-Release-v0.1/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

### With Database Configuration
```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "/path/to/Pre-Release-v0.1/bin/ranex_mcp",
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}",
        "RANEX_DB_PRIMARY_URL": "postgresql://localhost/mydb"
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
      "command": "/path/to/Pre-Release-v0.1/bin/ranex_mcp",
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

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Binary not found | Use absolute path in config |
| Tools not showing | Restart IDE completely |
| Old version showing | Clear IDE cache and restart |
| Environment vars not working | Use absolute paths |
| Server crashes | Check binary permissions (`chmod +x`) |

---

## 📚 More Information

- **Full Setup Guide:** [MCP_SETUP.md](MCP_SETUP.md)
- **Binary Details:** [bin/README.md](../../bin/README.md)
- **API Reference:** [API_REFERENCE.md](../API_REFERENCE.md)
- **Features:** [FEATURES.md](../FEATURES.md)

---

## ✅ Quick Checklist

- [ ] Binary exists: `Pre-Release-v0.1/bin/ranex_mcp`
- [ ] Config file created
- [ ] Absolute path used in config
- [ ] IDE restarted completely
- [ ] Server shows: "Ranex AI Governance Framework v0.0.1"
- [ ] 11 tools visible

---

**Last Updated:** 2025-01-27  
**Pre-Release Version:** 0.0.1
