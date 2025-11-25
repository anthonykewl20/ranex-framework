import itertools
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional, Set, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ranex_core import (
    ImportValidator,
    LayerEnforcer,
    ProjectPhase,
    SemanticAtlas,
    StateMachine,
    StructureSentinel,
    WorkflowManager,
    DatabaseSchemaProvider,
)

from ranex.templates import (
    get_design_template,
    get_feature_override_template,
    get_requirements_template,
    get_system_context,
)

app = typer.Typer(help="Ranex Governance CLI")
config_app = typer.Typer(help="Manage Ranex configuration")
app.add_typer(config_app, name="config")
console = Console()

SYSTEM_PROMPT = """# .windsurfrules

# AMBIGUITY PROTOCOL (Highest Priority)
1. When the user asks for a feature (e.g., "Build Auth"), you MUST NOT start coding.
2. You MUST first construct a JSON Manifest:
   { "feature_name": "...", "description": "...", "primary_actor": "...", "data_impact": "..." }
3. You MUST call the MCP tool `validate_intent` with this JSON.
4. IF the tool returns "REJECTED":
   - STOP.
   - Ask the user the exact questions provided in the tool response.
   - Do not proceed until you get answers.
5. ONLY when the tool returns "ACCEPTED" may you run `ranex task start`.

# 1. THE PRIME DIRECTIVE
You are the **Ranex Lead Architect**. You DO NOT write generic Python.
You MUST follow the architectural physics defined in `CONTEXT.md`.

# 2. BEHAVIORAL LOCKS
- **Before Coding:** Check `.ranex/workflow.toml`.
  - If phase != "implementation", you are **FORBIDDEN** from writing `.py` files in `app/`.
  - You must write Markdown specs in `docs/specs/` instead.
- **Before Refactoring:** Run `ranex arch` to check for layer violations.
- **After Coding:** Run `ranex scan` to verify compliance.

# 3. KNOWLEDGE RETRIEVAL
- **Architecture:** Read `CONTEXT.md` for the 4-file feature structure.
- **State Logic:** Read `state.yaml` inside the specific feature folder.
- **Shared Logic:** Search `app/commons/` before inventing new utilities.

# 4. ERROR HANDLING
If you see "🛑 TIME LOCK ACTIVE", do not argue.
Immediately stop coding and ask the user: "I must complete the Requirements/Design phase first. Shall we do that?"

# 5. COMMAND SHORTCUTS
- To start a feature: `ranex task start "name"`
- To visualize: `ranex graph`
- To fix structure: `ranex fix`
"""

DEFAULT_CONFIG_TOML = (
    "# RANEX ARCHITECTURE CONFIGURATION\n"
    "[layers]\n"
    "routes = [\"service\", \"commons\"]\n"
    "service = [\"models\", \"commons\"]\n"
    "models = [\"commons\"]\n"
    "commons = []\n\n"
    "[hints]\n"
    "\"routes->models\" = \"💡 FIX STRATEGY: 'Service Pattern'. Move DB logic to service.py.\"\n"
    "\"models->service\" = \"💡 FIX STRATEGY: 'Pure Data'. Models cannot access logic.\"\n"
    "\"commons->features\" = \"💡 FIX STRATEGY: 'Dependency Inversion'. Commons must be agnostic.\"\n"
    "\"forbidden::sqlalchemy\" = \"💡 FIX STRATEGY: Use the service layer to perform DB work.\"\n\n"
    "[features.payment]\n"
    "forbidden_packages = [\"sqlalchemy\", \"pandas\"]\n\n"
    "[features.payment.layers]\n"
    "routes = [\"service\", \"commons\"]\n"
    "service = [\"models\", \"commons\"]\n"
)


def _write_windsurf_rules(base_path: Optional[str] = None) -> str:
    root = base_path or os.getcwd()
    rules_path = os.path.join(root, ".windsurfrules")
    with open(rules_path, "w", encoding="utf-8") as handle:
        handle.write(SYSTEM_PROMPT)
    return rules_path


def _create_mcp_setup_guides(base_path: str) -> None:
    """Create IDE-agnostic MCP setup guides for users."""
    setup_dir = os.path.join(base_path, "docs", "setup")
    os.makedirs(setup_dir, exist_ok=True)
    
    # Main setup guide
    main_guide = """# Ranex MCP Server Setup Guide

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
Or: `%APPDATA%\\Claude\\claude_desktop_config.json` (Windows)  
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
"""
    
    with open(os.path.join(setup_dir, "MCP_SETUP.md"), "w", encoding="utf-8") as f:
        f.write(main_guide)
    
    # Create quick reference card
    quick_ref = """# Ranex MCP - Quick Reference

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
"""
    
    with open(os.path.join(setup_dir, "QUICK_REFERENCE.md"), "w", encoding="utf-8") as f:
        f.write(quick_ref)


def _ensure_config_file(base_path: Optional[str] = None) -> Tuple[str, bool]:
    root = base_path or os.getcwd()
    ranex_dir = os.path.join(root, ".ranex")
    os.makedirs(ranex_dir, exist_ok=True)
    config_toml_path = os.path.join(ranex_dir, "config.toml")
    created = False

    if not os.path.exists(config_toml_path):
        with open(config_toml_path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_CONFIG_TOML)
        created = True

    return config_toml_path, created


@config_app.command("edit")
def config_edit(
    editor: Optional[str] = typer.Option(
        None,
        "--editor",
        help="Editor command to open .ranex/config.toml. Defaults to $EDITOR or nano.",
    )
) -> None:
    """Open the architecture config in your editor."""

    config_path, _ = _ensure_config_file()
    chosen = editor or os.environ.get("EDITOR") or "nano"
    parts = shlex.split(chosen)

    if not parts:
        console.print("[red]No editor specified.[/red]")
        console.print(f"[yellow]Config located at: {config_path}[/yellow]")
        return

    binary = shutil.which(parts[0])
    if binary is None:
        console.print(
            f"[red]Editor '{parts[0]}' not found. Provide a valid command via --editor.[/red]"
        )
        console.print(f"[yellow]Config located at: {config_path}[/yellow]")
        return

    command = [binary, *parts[1:], config_path]
    try:
        subprocess.run(command, check=False)
    except OSError as exc:
        console.print(f"[red]Failed to launch editor: {exc}[/red]")
        console.print(f"[yellow]Config located at: {config_path}[/yellow]")


@config_app.command("validate")
def config_validate() -> None:
    """Validate the dynamic architecture config for common mistakes."""

    config_path, _ = _ensure_config_file()
    try:
        with open(config_path, "rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        console.print(f"[red]❌ Could not parse {config_path}: {exc}[/red]")
        raise typer.Exit(code=1)

    errors: List[str] = []

    layers = data.get("layers")
    if not isinstance(layers, dict) or not layers:
        errors.append("[layers] table is missing or empty.")

    hints = data.get("hints")
    if not isinstance(hints, dict) or not hints:
        errors.append("[hints] table is missing or empty.")

    features = data.get("features", {})
    if features and not isinstance(features, dict):
        errors.append("[features] must be a table of per-feature configs.")

    if isinstance(features, dict):
        for name, cfg in features.items():
            if not isinstance(cfg, dict):
                errors.append(f"Feature '{name}' must be a table, got {type(cfg).__name__}.")
                continue

            feat_layers = cfg.get("layers")
            if feat_layers and not isinstance(feat_layers, dict):
                errors.append(
                    f"Feature '{name}': layers must be a table mapping layer -> allowed list."
                )

            forbidden = cfg.get("forbidden_packages")
            if forbidden and (not isinstance(forbidden, list) or not all(isinstance(pkg, str) for pkg in forbidden)):
                errors.append(
                    f"Feature '{name}': forbidden_packages must be a list of package names."
                )

    if errors:
        console.print("[red]❌ Config validation failed:[/red]")
        for err in errors:
            console.print(f"   • {err}")
        raise typer.Exit(code=1)

    layer_count = len(layers or {})
    hint_count = len(hints or {})
    feature_count = len(features or {})
    console.print(
        f"[green]✅ Config valid:[/green] {layer_count} layers, {hint_count} hints, {feature_count} feature overrides."
    )


@app.command()
def task(action: str, name: str = typer.Argument(None, help="Feature name when starting a task")) -> None:
    """Manage the development workflow (start → design → build)."""

    console.print("[bold blue]🤖 Ranex Workflow Engine[/bold blue]")
    cwd = os.getcwd()
    wf = WorkflowManager(cwd)

    specs_dir = os.path.join(cwd, "docs", "specs")
    os.makedirs(specs_dir, exist_ok=True)

    action = action.lower()

    if action == "start":
        if not name:
            console.print("[red]Error: Name required. Usage: ranex task start <feature_name>[/red]")
            return

        wf.set_phase(ProjectPhase.Requirements)
        wf.set_task(name)

        filename = f"001_{name}_reqs.md"
        path = os.path.join(specs_dir, filename)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(get_requirements_template(name))

        console.print("[green]✅ Phase 1 Initiated: REQUIREMENTS[/green]")
        console.print(f"   📄 Created: docs/specs/{filename}")
        console.print("   🔒 [bold]Code Generation is LOCKED.[/bold] Fill out the template first.")
        return

    if action == "design":
        current_task = wf.config.active_task
        if not current_task:
            console.print("[red]No active task. Run 'ranex task start <feature>' first.[/red]")
            return

        wf.set_phase(ProjectPhase.Design)

        filename = f"002_{current_task}_design.md"
        path = os.path.join(specs_dir, filename)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(get_design_template(current_task))

        console.print("[green]✅ Phase 2 Initiated: DESIGN & STANDARDS[/green]")
        console.print(f"   📄 Created: docs/specs/{filename}")
        console.print("   🔒 [bold]Code Generation is LOCKED.[/bold] Define config & standards.")
        return

    if action == "build":
        current_task = wf.config.active_task
        if not current_task:
            console.print("[red]No active task. Run 'ranex task start <feature>' first.[/red]")
            return

        wf.set_phase(ProjectPhase.Implementation)
        console.print("[green]✅ Phase 3 Initiated: IMPLEMENTATION[/green]")
        console.print("   🔓 [bold]Code Generation UNLOCKED.[/bold] Build from the approved design.")

        sim_file = _get_active_simulation(cwd, current_task)
        if sim_file:
            full_path = os.path.join(cwd, sim_file)
            if not os.path.exists(full_path):
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                default_yaml = (
                    f'scenario: "Verify {current_task}"\n'
                    "steps:\n"
                    "  - step: \"Health Check\"\n"
                    "    action: GET /\n"
                    "    expect: 200\n"
                )
                with open(full_path, "w", encoding="utf-8") as handle:
                    handle.write(default_yaml)
                console.print(f"[green]   ✨ Scaffolding created: {sim_file}[/green]")
                console.print("   👉 [bold]AI INSTRUCTION:[/bold] Now fill this YAML with real steps.")

        return

    console.print(f"[red]Unknown action: {action}. Use start/design/build.[/red]")


@app.command()
def context(
    output: str = typer.Option(None, help="Save to file (e.g., CONTEXT.md)"),
    feature: Optional[str] = typer.Option(
        None, "--feature", "-f", help="Append per-feature overrides to the system context"
    ),
    onboard: bool = typer.Option(
        False,
        "--onboard",
        help="Automate onboarding by writing docs/onboarding/CONTEXT*.md and checklist",
    ),
) -> None:
    """Generate the 'God Prompt' to align any AI with Ranex Architecture."""

    normalized_feature = _normalize_feature_name(feature) if feature else None

    content = get_system_context()
    if normalized_feature:
        content = "\n\n".join([content, _build_feature_override_section(normalized_feature)])

    destination: Optional[Path] = None
    if onboard:
        destination = _write_onboarding_bundle(content, normalized_feature)
        console.print(f"[green]✅ Automated onboarding bundle ready: {destination}[/green]")
    elif output:
        destination = Path(output)
        _write_context_to_file(content, destination)
        console.print(f"[green]✅ Context saved to {destination}[/green]")
    else:
        console.print(Panel(content, title="Ranex System Context", border_style="yellow"))
        if normalized_feature:
            console.print(f"[cyan]Feature override applied for '{normalized_feature}'.[/cyan]")
        console.print("\n[dim]Tip: Pipe this into your AI or use --output CONTEXT.md[/dim]")
        return

    if normalized_feature:
        console.print(f"[cyan]Feature override applied for '{normalized_feature}'.[/cyan]")


@app.command()
def verify(
    scenario: Optional[str] = typer.Argument(
        None, help="Path to simulation YAML (e.g., tests/simulations/payment_flow.yaml)"
    ),
    auto: bool = typer.Option(False, "--auto", help="Run the simulation linked to current task"),
    preview: bool = typer.Option(False, "--preview", help="Preview only, don't execute"),
    port: int = typer.Option(8001, "--port", help="Port for test server"),
) -> None:
    """Execute 'Holodeck' simulation (live server test) or preview scenario."""

    console.print("[bold blue]🧪 Ranex Verification Harness - The Holodeck[/bold blue]")

    target_scenario = scenario

    if auto:
        cwd = os.getcwd()
        wf = WorkflowManager(cwd)
        current_task = wf.config.active_task

        if not current_task:
            console.print("[red]No active task. Cannot use --auto.[/red]")
            sys.exit(1)

        target_scenario = _get_active_simulation(cwd, current_task)
        if not target_scenario:
            console.print(
                f"[red]No simulation linked in 'docs/specs/002_{current_task}_design.md'.[/red]"
            )
            sys.exit(1)

        console.print(f"[bold blue]🔗 Auto-Detected Simulation: {target_scenario}[/bold blue]")

    if not target_scenario:
        console.print("[red]Error: Provide a simulation path or use --auto[/red]")
        sys.exit(1)

    scenario_path = target_scenario
    if not os.path.isabs(scenario_path):
        scenario_path = os.path.join(os.getcwd(), scenario_path)

    if not os.path.exists(scenario_path):
        console.print(f"[red]Simulation file not found: {scenario_path}[/red]")
        sys.exit(1)

    # Preview mode (old behavior)
    if preview:
        console.print(f"[green]▶ Previewing simulation: {scenario_path}[/green]")
        preview_panel = _render_simulation_preview(scenario_path)
        console.print(preview_panel)
        console.print("[dim]Use without --preview to execute against live server.[/dim]")
        return

    # Execution mode (new behavior - THE HOLODECK)
    from ranex.simulation import SimulationRunner, start_server, stop_server

    server_process = None
    try:
        # Start server
        server_process = start_server(port=port)

        # Run simulation
        runner = SimulationRunner(base_url=f"http://127.0.0.1:{port}")
        success = runner.run_scenario(scenario_path)

        # Print summary
        runner.print_summary()

        if success:
            console.print("\n[bold green]✅ SIMULATION PASSED. The System works in Reality.[/bold green]")
        else:
            console.print("\n[bold red]❌ SIMULATION FAILED. See Forensic Report above.[/bold red]")
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Simulation interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Simulation error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        if server_process:
            stop_server(server_process)


@app.command()
def db(
    action: str = typer.Argument(..., help="Action: inspect | check"),
    query: Optional[str] = typer.Option(None, "--query", help="SQL query to validate"),
    url: Optional[str] = typer.Option(
        None,
        "--url",
        "--connection",
        help="Database connection string (sqlite://, postgres://, mysql://, redis://)",
    ),
) -> None:
    """Database utilities for schema inspection, SQL validation, and Redis key inference."""

    def _inspect_target(conn_str: str) -> None:
        console.print(f"\n[bold magenta]🔌 Connecting to: {conn_str.split('@')[-1]}[/bold magenta]")
        provider = DatabaseSchemaProvider(conn_str)

        if action == "inspect":
            try:
                schema = provider.get_schema_context()
                if not schema.tables:
                    console.print("[yellow]No tables/keys found in schema.[/yellow]")
                    return
                for table, cols in schema.tables.items():
                    console.print(f"  📦 [bold]{table}[/bold]")
                    for col in cols:
                        console.print(f"     - {col.name} ({col.dtype})")
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
            return

        if action == "check":
            if not query:
                console.print("[red]Error: Provide --query to validate SQL.[/red]")
                return
            try:
                result = provider.validate_query(query)
                console.print(f"[green]{result}[/green]")
            except Exception as exc:
                console.print(f"[red]{exc}[/red]")
            return

        console.print(f"[red]Unknown db action: {action}. Use 'inspect' or 'check'.[/red]")

    if not url:
        targets: List[str] = []
        env_db = os.getenv("DATABASE_URL")
        env_redis = os.getenv("REDIS_URL")
        if env_db:
            targets.append(env_db)
        if env_redis:
            targets.append(env_redis)
        if os.path.exists("real_app.db"):
            targets.append("sqlite://real_app.db")

        if not targets:
            console.print(
                "[yellow]⚠️  No databases found (set DATABASE_URL or REDIS_URL, or provide --url).[/yellow]"
            )
            return

        for target in targets:
            _inspect_target(target)
        return

    _inspect_target(url)


def _normalize_feature_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", name.strip().lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "feature"


def _get_active_simulation(cwd: str, task_name: Optional[str]) -> Optional[str]:
    if not task_name:
        return None

    design_path = os.path.join(cwd, "docs", "specs", f"002_{task_name}_design.md")
    if not os.path.exists(design_path):
        return None

    with open(design_path, "r", encoding="utf-8") as handle:
        content = handle.read()

    match = re.search(r"Simulation:\s*`([^`]+)`", content)
    if match:
        return match.group(1).strip()
    return None


def _build_feature_override_section(feature: str) -> str:
    return get_feature_override_template(feature)


def _write_context_to_file(content: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with open(destination, "w", encoding="utf-8") as handle:
        handle.write(content)


def _write_onboarding_bundle(content: str, feature: Optional[str]) -> Path:
    root = Path(os.getcwd())
    onboarding_dir = root / "docs" / "onboarding"
    onboarding_dir.mkdir(parents=True, exist_ok=True)

    suffix = f"_{feature}" if feature else ""
    context_path = onboarding_dir / f"CONTEXT{suffix.upper() if suffix else ''}.md"
    _write_context_to_file(content, context_path)

    checklist_path = onboarding_dir / f"ONBOARDING_CHECKLIST{suffix.upper() if suffix else ''}.md"
    checklist_content = _build_onboarding_checklist(feature or "global", context_path)
    _write_context_to_file(checklist_content, checklist_path)

    return context_path


def _build_onboarding_checklist(feature: str, context_path: Path) -> str:
    pretty_feature = feature.replace("_", " ").title()
    relative_path = context_path.relative_to(Path(os.getcwd()))
    return dedent(
        f"""
        # Ranex Onboarding Checklist — {pretty_feature}

        1. **Read the System Context**
           - Path: `{relative_path}`
           - Paste this into your AI assistant as the governing prompt.

        2. **Acknowledge the Workflow**
           - Run `ranex task start <feature>` to lock into Requirements.
           - Fill out `docs/specs/001_<feature>_reqs.md` and `002_<feature>_design.md`.

        3. **Enable Guardrails**
           - Start MCP server or connect IDE to Ranex core.
           - Ensure `ranex stress` passes before merging.

        4. **Generate Code**
           - Only after `ranex task build` unlocks Implementation.
           - Use commons for shared logic; respect four-file feature boundary.

        5. **Verification**
           - Run `ranex arch` and `ranex scan` to prove compliance.
           - Capture outputs alongside PR for audit.

        6. **Hand-off**
           - Store updated context or overrides if new feature constraints emerge.
        """
    ).strip()


def _render_simulation_preview(path: str) -> Panel:
    try:
        import yaml  # type: ignore

        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        preview = json.dumps(data, indent=2)
        return Panel(preview, title="Simulation Preview", border_style="cyan")
    except Exception:
        with open(path, "r", encoding="utf-8") as handle:
            preview_text = handle.read()
        return Panel(preview_text, title="Simulation Preview (raw)", border_style="yellow")


def _scan_python_imports(root: Path) -> Set[str]:
    """Walk project files and return a set of imported root packages."""

    import_re = re.compile(r"^\s*(?:import|from)\s+([a-zA-Z0-9_\-]+)")
    imports: Set[str] = set()

    for dirpath, dirnames, filenames in os.walk(root):
        if any(skip in dirpath for skip in (".venv", "__pycache__", ".git", ".ranex")):
            continue

        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            filepath = Path(dirpath) / filename
            try:
                with filepath.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        match = import_re.match(line)
                        if match:
                            pkg = match.group(1)
                            imports.add(pkg.split(".")[0])
            except (UnicodeDecodeError, OSError):
                continue

    return imports


def _collect_feature_names() -> List[str]:
    features_root = Path("app/features")
    if not features_root.exists():
        return []
    return [p.name for p in features_root.iterdir() if p.is_dir() and not p.name.startswith("__")]


@app.command()
def init() -> None:
    """Initialize Ranex Governance in this repository."""

    console.print(Panel.fit("🛡️ Initializing Ranex v0.0.1 Governance Layer", style="bold blue"))
    cwd = os.getcwd()

    # Run comprehensive health checks FIRST
    console.print("\n[bold]Step 1: System Health Check[/bold]")
    results = _comprehensive_health_check(verbose=True)
    
    # Check for critical errors (aligned with SHIPPED package)
    critical_checks = ["python", "ranex_core", "mcp_binary"]
    critical_passed = sum(1 for check in critical_checks if results[check])
    
    if critical_passed < len(critical_checks):
        console.print("\n[bold red]❌ Critical dependencies missing![/bold red]")
        console.print("[yellow]Fix the errors above before proceeding.[/yellow]")
        
        if not results["ranex_core"]:
            console.print("\n[bold]Install Ranex:[/bold]")
            console.print("   pip install ranex-core")
        
        sys.exit(1)
    
    console.print("\n[bold green]✅ All critical checks passed![/bold green]")
    
    # Show warnings but continue
    if results["warnings"]:
        console.print(f"\n[yellow]⚠️  {len(results['warnings'])} warnings (non-critical):[/yellow]")
        for warning in results["warnings"][:3]:  # Show first 3
            console.print(f"   • {warning}")
        if len(results["warnings"]) > 3:
            console.print(f"   ... and {len(results['warnings']) - 3} more")
    
    # Continue with initialization
    console.print("\n[bold]Step 2: Creating Project Structure[/bold]")
    
    # Create IDE-agnostic rules file
    _write_windsurf_rules(cwd)
    console.print("[green]✅ Created AI Governance Rules (.windsurfrules)[/green]")

    # Create setup guides instead of IDE-specific configs
    _create_mcp_setup_guides(cwd)
    console.print("[green]✅ Created MCP Setup Guides (docs/setup/)[/green]")

    config_toml_path, created = _ensure_config_file(cwd)
    if created:
        console.print("[green]✅ Created Dynamic Config (.ranex/config.toml)[/green]")
    else:
        console.print("[yellow]ℹ️  Found existing .ranex/config.toml (left unchanged).[/yellow]")

    os.makedirs(os.path.join(cwd, "app", "commons"), exist_ok=True)
    os.makedirs(os.path.join(cwd, "app", "features"), exist_ok=True)
    console.print("[green]✅ Created Standard Directory Structure[/green]")
    
    # Final summary
    console.print("\n[bold green]🎉 Ranex Initialized Successfully![/bold green]")
    
    console.print("\n[bold cyan]📖 Next Steps:[/bold cyan]")
    console.print("   1. Read docs/setup/MCP_SETUP.md for your IDE")
    console.print("   2. Configure MCP server (Windsurf, Cursor, or Claude Desktop)")
    
    if not results["mcp_binary"]:
        console.print("   3. [bold yellow]Build MCP server: cargo build --release --bin ranex_mcp[/bold yellow]")
    else:
        console.print("   3. ✅ MCP server already built")
    
    console.print("   4. Restart your IDE to activate Ranex")
    
    if not results["ranex_core"]:
        console.print("\n[yellow]💡 Tip: Install Python bindings with: pip install -e .[/yellow]")
    
    console.print()


@app.command("update-rules")
def update_rules() -> None:
    """Force-refresh the advanced AI governance rules file."""

    _write_windsurf_rules()
    console.print("[green]✅ Advanced AI Governance Rules updated (.windsurfrules)[/green]")


def _comprehensive_health_check(verbose: bool = True) -> dict:
    """Run comprehensive health checks and return results.
    
    Checks align with SHIPPED package (no Rust/Cargo required for end users).
    """
    results = {
        "python": False,
        "ranex_core": False,
        "mcp_binary": False,
        "dependencies": [],
        "warnings": [],
        "errors": []
    }
    
    if verbose:
        console.print("\n[bold cyan]🔍 Running Health Checks...[/bold cyan]\n")
    
    # Check 1: Python version (CRITICAL - always required)
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 12):
        results["python"] = True
        if verbose:
            console.print(f"[green]✅ Python {python_version}[/green]")
    else:
        results["errors"].append(f"Python {python_version} < 3.12 (required)")
        if verbose:
            console.print(f"[red]❌ Python {python_version} (need ≥3.12)[/red]")
    
    # Check 2: Ranex Core Library (CRITICAL - pre-compiled in shipped package)
    try:
        import ranex_core  # noqa: F401
        results["ranex_core"] = True
        if verbose:
            console.print("[green]✅ Ranex Core: INSTALLED[/green]")
    except ImportError:
        results["errors"].append("Ranex core not installed")
        if verbose:
            console.print("[red]❌ Ranex Core: NOT INSTALLED[/red]")
            console.print("   Install: pip install ranex-core")
    
    # Check 3: MCP Binary (CRITICAL - pre-built in shipped package)
    # Check multiple possible locations
    mcp_locations = [
        os.path.join("target", "release", "ranex_mcp"),  # Dev environment
        "ranex_mcp",  # Shipped package (in PATH or local)
        os.path.join(sys.prefix, "bin", "ranex_mcp"),  # Installed in venv
    ]
    
    mcp_found = False
    for mcp_binary in mcp_locations:
        if os.path.exists(mcp_binary) and os.access(mcp_binary, os.X_OK):
            results["mcp_binary"] = True
            mcp_found = True
            if verbose:
                console.print(f"[green]✅ MCP Server: {mcp_binary}[/green]")
            break
    
    if not mcp_found:
        results["errors"].append("MCP server binary not found")
        if verbose:
            console.print("[red]❌ MCP Server: NOT FOUND[/red]")
            console.print("   Expected in shipped package or run: cargo build --release --bin ranex_mcp")
    
    # Check 4: PyYAML (CRITICAL for simulations)
    try:
        import yaml  # noqa: F401
        if verbose:
            console.print("[green]✅ PyYAML: INSTALLED[/green]")
    except ImportError:
        results["errors"].append("PyYAML required for simulations")
        if verbose:
            console.print("[red]❌ PyYAML: NOT INSTALLED (required for simulations)[/red]")
            console.print("   Install: pip install pyyaml")
    
    # Check 5: Optional Python packages
    optional_packages = [
        "typer",
        "rich",
        "pydantic",
        "fastapi"
    ]
    
    for package in optional_packages:
        try:
            __import__(package.replace("-", "_"))
            results["dependencies"].append(package)
        except ImportError:
            results["warnings"].append(f"Missing Python package: {package}")
            if verbose:
                console.print(f"[yellow]⚠️  Package '{package}': NOT INSTALLED[/yellow]")
    
    if verbose and len(results["dependencies"]) == len(optional_packages):
        console.print(f"[green]✅ Python Dependencies: All {len(optional_packages)} installed[/green]")
    
    # Check 8: Project structure
    required_dirs = ["app/commons", "app/features", ".ranex"]
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        results["warnings"].append(f"Missing directories: {', '.join(missing_dirs)}")
        if verbose:
            console.print(f"[yellow]⚠️  Project Structure: Missing {len(missing_dirs)} directories[/yellow]")
    else:
        if verbose:
            console.print("[green]✅ Project Structure: Complete[/green]")
    
    return results


@app.command()
def doctor() -> None:
    """Check if the Ranex environment is healthy."""

    console.print("[bold]🏥 Ranex System Health Check[/bold]")
    
    results = _comprehensive_health_check(verbose=True)
    
    # Summary
    console.print("\n[bold]📊 Summary:[/bold]")
    
    critical_checks = ["python", "ranex_core", "mcp_binary"]
    critical_passed = sum(1 for check in critical_checks if results[check])
    
    if critical_passed == len(critical_checks):
        console.print(f"[green]✅ Critical: {critical_passed}/{len(critical_checks)} passed[/green]")
    else:
        console.print(f"[red]❌ Critical: {critical_passed}/{len(critical_checks)} passed[/red]")
    
    if results["warnings"]:
        console.print(f"[yellow]⚠️  Warnings: {len(results['warnings'])}[/yellow]")
    
    if results["errors"]:
        console.print(f"[red]❌ Errors: {len(results['errors'])}[/red]")
        for error in results["errors"]:
            console.print(f"   • {error}")
    
    if not results["errors"] and not results["warnings"]:
        console.print("\n[bold green]🎉 System is fully ready for AI Governance![/bold green]")
    elif not results["errors"]:
        console.print("\n[bold yellow]⚠️  System is functional but has warnings.[/bold yellow]")
    else:
        console.print("\n[bold red]❌ System has critical errors. Fix them to proceed.[/bold red]")
        sys.exit(1)


@app.command()
def scan() -> None:
    """Run the Ranex security & architecture scan."""

    console.print("[bold]🛡️ Ranex Sentinel Scanning...[/bold]\n")
    cwd = Path(os.getcwd())
    has_error = False

    table = Table(title="Ranex Scan Summary")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details")

    # 1. Structure
    try:
        sentinel = StructureSentinel(str(cwd))
        sentinel.enforce()
        table.add_row("Structure Sentinel", "[green]PASS[/green]", "All files valid.")
    except Exception as exc:
        has_error = True
        table.add_row("Structure Sentinel", "[red]FAIL[/red]", str(exc))

    # 2. Imports scanned from code
    validator = ImportValidator()
    code_imports = _scan_python_imports(cwd)
    ignore = {
        "os",
        "sys",
        "json",
        "re",
        "typing",
        "datetime",
        "math",
        "pathlib",
        "functools",
        "itertools",
        "shutil",
        "subprocess",
        "time",
        "ranex_core",
    }
    invalid_imports: List[str] = []
    for pkg in sorted(code_imports):
        if pkg in ignore:
            continue
        verdict = validator.check_package(pkg)
        if not verdict.is_safe:
            invalid_imports.append(f"{pkg} ({verdict.reason})")

    if invalid_imports:
        has_error = True
        table.add_row("Import Validator", "[red]FAIL[/red]", "\n".join(invalid_imports))
    else:
        table.add_row(
            "Import Validator",
            "[green]PASS[/green]",
            f"Scanned {len(code_imports)} imports. All safe.",
        )

    # 3. Semantic Atlas
    try:
        atlas = SemanticAtlas()
        indexed = len(atlas.semantic_search("", 0.0))
        table.add_row("Semantic Atlas", "[green]PASS[/green]", f"Indexed {indexed} functions.")
    except Exception as exc:
        has_error = True
        table.add_row("Semantic Atlas", "[red]FAIL[/red]", str(exc))

    console.print(table)

    if has_error:
        console.print("\n[red]❌ Scan failed. See details above.[/red]")
        raise typer.Exit(code=1)

    console.print("\n[green]✅ Scan Passed. System Secure.[/green]")


@app.command()
def graph(feature: str = typer.Option(None, help="Specific feature to graph")) -> None:
    """Generate a Mermaid.js diagram of the current business logic."""

    console.print(Panel.fit("📊 Generating Living Architecture Diagram...", style="bold blue"))
    cwd = os.getcwd()
    features_dir = os.path.join(cwd, "app/features")

    target_features: List[str] = []
    if feature:
        target_features.append(feature)
    else:
        if os.path.exists(features_dir):
            for entry in os.listdir(features_dir):
                if os.path.isdir(os.path.join(features_dir, entry)) and not entry.startswith("_"):
                    target_features.append(entry)

    if not target_features:
        console.print("[red]No features found to graph.[/red]")
        return

    mermaid_code = "graph TD\n"

    for feat in target_features:
        try:
            sm = StateMachine(feat)
            mermaid_code += f"    subgraph {feat.upper()}\n"
            mermaid_code += f"    {feat}_Start((Start)) --> {feat}_{sm.rules.initial}\n"
            for start_state, targets in sm.rules.transitions.items():
                for target in targets:
                    mermaid_code += f"    {feat}_{start_state} --> {feat}_{target}\n"
            mermaid_code += "    end\n"
            console.print(f"[green]✅ Loaded Logic for '{feat}'[/green]")
        except Exception as exc:
            console.print(f"[yellow]⚠️  Could not load '{feat}': {exc}[/yellow]")

    output_file = "architecture.mermaid"
    with open(output_file, "w", encoding="utf-8") as handle:
        handle.write(mermaid_code)

    console.print(f"\n[bold]✨ Diagram Generated: {output_file}[/bold]")
    console.print(
        "Paste the content below into [link=https://mermaid.live]Mermaid.live[/link]:\n"
    )
    print("--- BEGIN COPY ---")
    print(mermaid_code)
    print("--- END COPY ---")


@app.command()
def fix() -> None:
    """Auto-correct architectural violations (Quarantine illegal folders AND files)."""

    console.print("[bold]🔧 Ranex Auto-Remediator Starting...[/bold]\n")

    cwd = os.getcwd()
    fixed_count = 0
    forbidden_dirs = ["utils", "helpers", "lib", "core"]
    allowed_feature_files = ["__init__.py", "routes.py", "service.py", "models.py", "state.yaml"]

    quarantine_dir = os.path.join(cwd, ".ranex/quarantine")
    os.makedirs(quarantine_dir, exist_ok=True)

    def quarantine_file(src_path: str, original_name: str, source_context: str) -> int:
        timestamp = int(time.time())
        safe_name = f"{timestamp}{source_context}{original_name}"
        dst = os.path.join(quarantine_dir, safe_name)
        shutil.move(src_path, dst)
        console.print(f"   ↳ ☣️  Quarantined '{original_name}' -> '{safe_name}'")
        return 1

    def remediate_folder(parent_path: str, folder_name: str, prefix: str = "") -> int:
        bad_path = os.path.join(parent_path, folder_name)
        count = 0
        if os.path.exists(bad_path):
            console.print(f"[yellow]⚠️  Found illegal folder: {bad_path}[/yellow]")
            for item in os.listdir(bad_path):
                src = os.path.join(bad_path, item)
                if os.path.isfile(src) and src.endswith(".py") and not item.startswith("__"):
                    count += quarantine_file(src, item, prefix.rstrip("_"))
            try:
                shutil.rmtree(bad_path)
                console.print("   ↳ 🗑️  Deleted illegal folder.")
            except Exception:
                pass
        return count

    app_dir = os.path.join(cwd, "app")
    if os.path.exists(app_dir):
        for bad in forbidden_dirs:
            fixed_count += remediate_folder(app_dir, bad, prefix="root")

    features_dir = os.path.join(cwd, "app/features")
    if os.path.exists(features_dir):
        for feature in os.listdir(features_dir):
            feat_path = os.path.join(features_dir, feature)
            if not os.path.isdir(feat_path) or feature.startswith("__"):
                continue
            for bad in forbidden_dirs:
                fixed_count += remediate_folder(feat_path, bad, prefix=feature)

            for item in os.listdir(feat_path):
                item_path = os.path.join(feat_path, item)
                if (
                    os.path.isfile(item_path)
                    and item.endswith(".py")
                    and not item.startswith("__")
                    and item not in allowed_feature_files
                ):
                    console.print(
                        f"[yellow]⚠️  Found illegal file in feature '{feature}': {item}[/yellow]"
                    )
                    fixed_count += quarantine_file(item_path, item, feature)

    if fixed_count > 0:
        console.print(
            f"\n[green]✅ Remediation Complete. {fixed_count} objects quarantined in .ranex/quarantine/[/green]"
        )
        console.print("[dim]Run 'ranex scan' to verify system health.[/dim]")
    else:
        console.print("\n[green]✨ No violations found.[/green]")


@app.command()
def arch() -> None:
    """Verify architectural layering between routes/service/models/commons."""

    console.print("[bold blue]📐 Checking Architectural Physics...[/bold blue]")

    enforcer = LayerEnforcer()
    report = enforcer.scan(os.getcwd())

    if report.valid:
        console.print("[green]✅ Architecture Valid. Layers are respected.[/green]")
    else:
        console.print("[bold red]❌ ARCHITECTURE VIOLATION DETECTED[/bold red]")
        for violation in report.violations:
            console.print(violation)
        sys.exit(1)


@app.command()
def bench(
    mode: str = typer.Option("both", help="Which Atlas to benchmark: old, new, or both")
) -> None:
    """Benchmark Atlas performance (old regex vs new graph-based).
    
    Reference: https://docs.python.org/3/library/timeit.html
    """
    import statistics
    import os
    
    console.print("[bold]📊 Atlas Performance Benchmark[/bold]\n")
    
    results = {}
    
    if mode in ["old", "both"]:
        console.print("[cyan]Testing OLD Atlas (regex-based)...[/cyan]")
        
        # Run multiple iterations for statistical accuracy
        iterations = 5
        warmup = 2
        scan_times = []
        search_times = []
        function_count = 0
        
        for i in range(warmup + iterations):
            start = time.perf_counter()
            try:
                atlas = SemanticAtlas()
                scan_time = time.perf_counter() - start
                
                start = time.perf_counter()
                results_search = atlas.semantic_search("validate email", 0.85)
                search_time = time.perf_counter() - start
                
                if i >= warmup:  # Only count after warmup
                    scan_times.append(scan_time)
                    search_times.append(search_time)
                    if function_count == 0:
                        all_functions = atlas.semantic_search("", 0.0)
                        function_count = len(all_functions)
            except Exception as exc:
                console.print(f"[red]❌ Benchmark failed: {exc}[/red]")
                import traceback
                traceback.print_exc()
                sys.exit(1)
        
        if scan_times:
            results["old"] = {
                "scan_mean": statistics.mean(scan_times),
                "scan_std": statistics.stdev(scan_times) if len(scan_times) > 1 else 0,
                "search_mean": statistics.mean(search_times),
                "search_std": statistics.stdev(search_times) if len(search_times) > 1 else 0,
                "functions_indexed": function_count,
            }
            
            console.print(f"  Scan time: {results['old']['scan_mean']:.3f}s ± {results['old']['scan_std']:.3f}s")
            console.print(f"  Search time: {results['old']['search_mean']*1000:.1f}ms ± {results['old']['search_std']*1000:.1f}ms")
            console.print(f"  Functions indexed: {results['old']['functions_indexed']}\n")
    
    if mode in ["new", "both"]:
        console.print("[cyan]Testing NEW Atlas (graph-based)...[/cyan]")
        
        # Ensure graph-atlas feature is available
        try:
            # Set environment variable to enable graph atlas
            os.environ["RANEX_USE_GRAPH_ATLAS"] = "true"
            
            iterations = 5
            warmup = 2
            scan_times = []
            cycle_times = []
            node_count = 0
            edge_count = 0
            
            for i in range(warmup + iterations):
                start = time.perf_counter()
                try:
                    atlas = SemanticAtlas()
                    # Call build_graph_index via Python wrapper
                    graph_result = atlas.build_graph_index_py()
                    
                    # Convert PyObject to Python dict
                    graph_dict = dict(graph_result) if graph_result else {}
                    
                    if graph_dict.get("success"):
                        scan_time = time.perf_counter() - start
                        node_count = graph_dict.get("node_count", 0)
                        edge_count = graph_dict.get("edge_count", 0)
                        
                        # Measure cycle detection time
                        if i >= warmup:
                            scan_times.append(scan_time)
                            # Cycle detection would be here if exposed
                            cycle_times.append(0.0)  # Placeholder
                    else:
                        error_msg = graph_dict.get("error", "Unknown error")
                        console.print(f"[yellow]⚠️  Graph build failed: {error_msg}[/yellow]")
                        console.print("[yellow]Skipping new Atlas benchmark (graph-atlas feature may not be enabled)[/yellow]\n")
                        break
                        
                except (AttributeError, TypeError) as e:
                    console.print("[yellow]⚠️  build_graph_index_py not available (graph-atlas feature not enabled)[/yellow]")
                    console.print("[yellow]Skipping new Atlas benchmark[/yellow]\n")
                    break
                except Exception as exc:
                    console.print(f"[yellow]⚠️  Error benchmarking new Atlas: {exc}[/yellow]")
                    console.print("[yellow]Skipping new Atlas benchmark[/yellow]\n")
                    break
            
            if scan_times:
                results["new"] = {
                    "scan_mean": statistics.mean(scan_times),
                    "scan_std": statistics.stdev(scan_times) if len(scan_times) > 1 else 0,
                    "cycle_mean": statistics.mean(cycle_times) if cycle_times else 0.0,
                    "cycle_std": statistics.stdev(cycle_times) if len(cycle_times) > 1 else 0.0,
                    "nodes": node_count,
                    "edges": edge_count,
                }
                
                console.print(f"  Scan time: {results['new']['scan_mean']:.3f}s ± {results['new']['scan_std']:.3f}s")
                if results['new']['cycle_mean'] > 0:
                    console.print(f"  Cycle detection: {results['new']['cycle_mean']*1000:.1f}ms ± {results['new']['cycle_std']*1000:.1f}ms")
                console.print(f"  Files indexed: {results['new']['nodes']}")
                console.print(f"  Import edges: {results['new']['edges']}\n")
        
        finally:
            # Clean up environment
            os.environ.pop("RANEX_USE_GRAPH_ATLAS", None)
    
    if mode == "both" and "old" in results and "new" in results:
        # Comparison table
        from rich.table import Table
        
        table = Table(title="Performance Comparison", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Old (regex)", style="yellow")
        table.add_column("New (graph)", style="green")
        table.add_column("Improvement", style="bold")
        
        scan_improvement = ((results["old"]["scan_mean"] - results["new"]["scan_mean"]) / results["old"]["scan_mean"]) * 100
        table.add_row(
            "Scan Time",
            f"{results['old']['scan_mean']:.3f}s",
            f"{results['new']['scan_mean']:.3f}s",
            f"{scan_improvement:+.1f}%"
        )
        
        console.print(table)
        
        # Verify requirement: new >= old performance
        if results["new"]["scan_mean"] <= results["old"]["scan_mean"]:
            console.print("[bold green]✅ New Atlas meets performance requirement (new ≤ old)[/bold green]")
        else:
            console.print("[bold red]❌ New Atlas is SLOWER - performance regression![/bold red]")
            console.print(f"[red]   Old: {results['old']['scan_mean']:.3f}s, New: {results['new']['scan_mean']:.3f}s[/red]")
            sys.exit(1)
        
        # Export results to JSON for CI/CD
        import json
        results_path = Path("benchmark_results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        console.print(f"\n[dim]Results saved to {results_path}[/dim]")
    
    elif mode == "old" and "old" in results:
        # Write baseline to file
        baseline_path = Path("PERFORMANCE_BASELINE.md")
        with open(baseline_path, "w", encoding="utf-8") as f:
            f.write(f"""# Atlas Performance Baseline

## Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Current Implementation (Regex-Based)

### Performance Metrics:
- **Scan Time:** {results['old']['scan_mean']:.3f}s ± {results['old']['scan_std']:.3f}s
- **Search Time:** {results['old']['search_mean']*1000:.1f}ms ± {results['old']['search_std']*1000:.1f}ms
- **Functions Indexed:** {results['old']['functions_indexed']}

### Test Parameters:
- **Search Query:** "validate email"
- **Threshold:** 0.85
- **Iterations:** 5 (after 2 warmup)

### System Info:
- **Python Version:** {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
- **Codebase:** app/ directory scan

---

## Acceptance Criteria for New Graph-Based Atlas:
- ✅ Scan time ≤ {results['old']['scan_mean']:.3f}s (no regression)
- ✅ Search time ≤ {results['old']['search_mean']*1000:.1f}ms (no regression)
- ✅ Function count ≥ {results['old']['functions_indexed']} (same or better coverage)
- ✅ Additional features: cycle detection, import tracking

---

**Note:** This baseline was generated automatically by `ranex bench --mode old`.
Run `ranex bench --mode both` to compare old vs new implementations.
""")
        console.print(f"[green]✅ Baseline documented in {baseline_path}[/green]")


@app.command()
def stress(feature: str = typer.Option("payment", help="Feature to stress test")) -> None:
    """Run a logic gauntlet (matrix + speed run) against the Rust core."""

    console.print(f"[bold red]⚔️  INITIATING THE GAUNTLET: {feature.upper()} ⚔️[/bold red]\n")

    try:
        sm = StateMachine(feature)
    except Exception as exc:
        console.print(f"[red]❌ Could not load feature '{feature}': {exc}[/red]")
        return

    console.print("[1] THE LOGIC MAZE: Testing ALL state permutations...")
    states = sm.rules.states or list(sm.rules.transitions.keys())

    if not states:
        console.print("[yellow]⚠️ No states defined for this feature.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("FROM \\ TO")
    for state in states:
        table.add_column(state)

    valid_count = 0
    blocked_count = 0
    for start_state in states:
        row = [start_state]
        for target_state in states:
            try:
                sm.validate_transition(start_state, target_state)
                row.append("[green]✅[/green]")
                valid_count += 1
            except Exception:
                row.append("[dim]🛡️[/dim]")
                blocked_count += 1
        table.add_row(*row)

    console.print(table)
    console.print(f"📊 Logic Report: {valid_count} Valid Paths, {blocked_count} Blocked Paths.\n")

    console.print("[2] THE SPEED RUN: Hammering Rust Core (1,000,000 ops)...")
    valid_transition = None
    for start_state, targets in sm.rules.transitions.items():
        if targets:
            valid_transition = (start_state, targets[0])
            break

    if not valid_transition:
        console.print("[yellow]⚠️ No valid transitions to run the speed test.[/yellow]")
        return

    start, end = valid_transition
    start_time = time.time()
    for _ in range(1_000_000):
        sm.validate_transition(start, end)
    duration = time.time() - start_time
    ops = 1_000_000 / duration if duration > 0 else float("inf")

    console.print(f"⚡ Completed in {duration:.4f}s")
    console.print(f"[bold green]🚀 THROUGHPUT: {ops:,.0f} checks/sec[/bold green]")


if __name__ == "__main__":
    app()
