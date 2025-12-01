# MCP Server Setup - Community Edition

## What is MCP?

MCP (Model Context Protocol) allows AI assistants like Claude, Cursor, Windsurf, and others to use Ranex tools directly during code generation.

## Community Edition Tools (10 of 43)

| Tool | Purpose |
|------|---------|
| `validate_file_structure` | Architecture validation |
| `validate_transition` | State machine checks |
| `check_import` | Import security (typosquatting) |
| `security_scan` | SAST scanning (7 patterns) |
| `detect_antipattern` | Code smell detection (5 patterns) |
| `list_db_aliases` | Database configuration |
| `validate_sql` | SQL validation |
| `validate_intent` | Ambiguity detection |
| `check_function_exists` | Semantic search (TF-IDF) |
| `get_active_persona` | View active persona |

---

## Setup for Cursor

### 1. Copy MCP Binary

```bash
# Copy to your project or a global location
cp ranex_mcp /usr/local/bin/
# or
cp ranex_mcp ~/.local/bin/
```

### 2. Configure Cursor

Add to your Cursor settings (`.cursor/mcp.json`):

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

### 3. Restart Cursor

The MCP tools will now be available to Claude.

---

## Setup for Windsurf

Windsurf (by Codeium) supports MCP servers for AI-powered development.

### 1. Copy MCP Binary

```bash
# Copy to a global location
cp ranex_mcp /usr/local/bin/
# or to user directory
cp ranex_mcp ~/.local/bin/
```

### 2. Configure Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

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

**Alternative: Project-level configuration**

Create `.windsurf/mcp.json` in your project root:

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

### 3. Restart Windsurf

Close and reopen Windsurf. The MCP tools will be available to Cascade (Windsurf's AI).

### 4. Verify Setup

In Windsurf, open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`) and look for MCP-related commands, or ask Cascade to use Ranex tools.

---

## Setup for Claude Desktop

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ranex": {
      "command": "/usr/local/bin/ranex_mcp",
      "args": []
    }
  }
}
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RANEX_APP_DIR` | Path to your app directory | `./app` |
| `RANEX_DB_PRIMARY_URL` | Primary database URL | Auto-detect |
| `RANEX_LOG_LEVEL` | Log level (debug, info, warn) | `info` |

---

## Testing the MCP Server

```bash
# Test that the binary runs
./ranex_mcp --help

# The server communicates via stdio, so it won't show output
# unless connected to an MCP client
```

---

## Example: Using in Cursor

Once configured, you can ask Claude:

> "Validate that my order transition from Pending to Shipped is allowed"

Claude will use the `validate_transition` tool:

```
Tool: validate_transition
Feature: orders
From: Pending
To: Shipped

Result: ❌ Invalid transition
  Allowed from Pending: [Confirmed, Cancelled]
```

---

## Upgrade to Team Edition

Team Edition includes all 43 MCP tools:

- ✅ ARBITER test validation (5 tools)
- ✅ Drift detection (5 tools)  
- ✅ RAG semantic search (4 tools)
- ✅ Advanced governance (4 tools)
- ✅ Persona management (4 tools)
- ✅ And more...

Contact: sales@ranex.dev

