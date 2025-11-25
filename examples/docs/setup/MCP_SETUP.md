# Ranex MCP Server Setup Guide

**Choose your IDE and follow the instructions below.**

---

## 🎯 Quick Start

1. **Build the MCP server:**
   ```bash
   cargo build --release --bin ranex_mcp
   ```

2. **Configure your IDE** (see sections below)

3. **Restart your IDE**

4. **Verify** - You should see 5 Ranex tools available

---

## 🔧 Windsurf Setup

### Location:
Create or edit: `~/.windsurf/mcp_config.json` (global) or `.windsurf/mcp_config.json` (project)

### Configuration:
```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "cargo",
      "args": ["run", "--release", "--bin", "ranex_mcp"],
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

### Verify:
1. Restart Windsurf
2. Open MCP panel
3. Look for "Ranex AI Governance Framework"
4. Should see 5 tools with professional names

---

## 🔧 Cursor Setup

### Location:
Create or edit: `~/.cursor/mcp_config.json` (global) or `.cursor/mcp_config.json` (project)

### Configuration:
```json
{
  "mcpServers": {
    "ranex-core": {
      "command": "cargo",
      "args": ["run", "--release", "--bin", "ranex_mcp"],
      "env": {
        "RANEX_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

### Verify:
1. Restart Cursor
2. Open MCP settings
3. Look for "Ranex AI Governance Framework"
4. Should see 5 tools available

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
      "command": "cargo",
      "args": ["run", "--release", "--bin", "ranex_mcp"],
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
      "command": "cargo",
      "args": ["run", "--release", "--bin", "ranex_mcp"],
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

### 5 Tools:
1. **Validate File Structure** - Enforce architectural rules
2. **Validate Intent** - Clarify ambiguous requests
3. **Check Function Exists** - Prevent code duplication
4. **List Database Aliases** - Show database connections
5. **Validate SQL Query** - Prevent SQL errors

---

## 🐛 Troubleshooting

### Tools not showing up?
1. Check MCP server built: `ls target/release/ranex_mcp`
2. Check config file syntax (valid JSON)
3. Restart IDE completely (not just reload)
4. Check IDE logs for MCP errors

### Old configuration showing?
1. Delete cache: `rm -rf ~/.{windsurf,cursor,codeium}/mcp_cache`
2. Rebuild server: `cargo build --release --bin ranex_mcp`
3. Restart IDE

### Environment variables not working?
- Use `${workspaceFolder}` for IDE-based tools
- Use absolute paths for Claude Desktop
- Check IDE supports variable substitution

---

## 📚 Advanced Configuration

### Multiple Databases:
```json
{
  "env": {
    "RANEX_PROJECT_ROOT": "${workspaceFolder}",
    "RANEX_DB_ALIASES": "primary,secondary",
    "RANEX_DB_PRIMARY_URL": "postgresql://localhost/mydb",
    "RANEX_DB_SECONDARY_URL": "sqlite://cache.db"
  }
}
```

### Custom Database:
```json
{
  "env": {
    "RANEX_PROJECT_ROOT": "${workspaceFolder}",
    "RANEX_DB_PRIMARY_URL": "mysql://user:pass@localhost/db"
  }
}
```

**Note:** Database auto-detection works for most cases. Only specify if you have custom setup.

---

## ✅ Verification Checklist

After setup, verify:

- [ ] MCP server binary exists: `target/release/ranex_mcp`
- [ ] Config file is valid JSON
- [ ] IDE restarted completely
- [ ] Server name shows: "Ranex AI Governance Framework"
- [ ] 5 tools visible with professional names
- [ ] Tool names are Title Case (not lowercase)
- [ ] Configuration shows `${workspaceFolder}` (not hardcoded path)

---

## 🎉 Success!

If you see all 5 tools with professional names, you're ready to use Ranex!

**Next:** Start coding and let Ranex enforce your architecture automatically.

---

**Need help?** Check the main documentation or open an issue.
