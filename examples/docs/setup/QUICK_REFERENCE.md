# Ranex MCP - Quick Reference

## Config Template (Copy-Paste)

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

## Config Locations

| IDE | Config Location |
|-----|----------------|
| **Windsurf** | `~/.windsurf/mcp_config.json` |
| **Cursor** | `~/.cursor/mcp_config.json` |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **VS Code + Continue** | `~/.continue/config.json` |

## Build Command

```bash
cargo build --release --bin ranex_mcp
```

## Verify Installation

1. Restart IDE
2. Look for "Ranex AI Governance Framework"
3. Should see 5 tools

## 5 Tools

1. Validate File Structure
2. Validate Intent
3. Check Function Exists
4. List Database Aliases
5. Validate SQL Query
