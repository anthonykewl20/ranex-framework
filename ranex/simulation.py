"""
Ranex Simulation Engine - "The Holodeck"

Replaces brittle unit tests with real-world flow verification.
Executes YAML scenarios against a live server with real HTTP requests and database state.
"""

import yaml
import httpx
import time
import subprocess
import sys
import os
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class SimulationRunner:
    """Executes YAML simulation scenarios against a live server."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=10.0)
        self.context: Dict[str, Any] = {}  # Stores captured vars (tokens, ids)
        self.step_results: List[Dict] = []
        
    def load_scenario(self, path: str) -> Dict:
        """Load YAML scenario file."""
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def resolve_vars(self, data: Any) -> Any:
        """Replaces {token} with actual values from context."""
        if isinstance(data, str):
            for key, val in self.context.items():
                placeholder = f"{{{key}}}"
                if placeholder in data:
                    data = data.replace(placeholder, str(val))
            return data
        if isinstance(data, dict):
            return {k: self.resolve_vars(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self.resolve_vars(item) for item in data]
        return data
    
    def run_step(self, step: Dict, step_num: int) -> bool:
        """Execute a single simulation step."""
        name = step.get("step", f"Step {step_num}")
        action = step.get("action", "")
        
        # Parse action (e.g., "POST /api/auth/register")
        parts = action.split(" ", 1)
        if len(parts) != 2:
            console.print(f"[red]❌ Invalid action format: {action}[/red]")
            return False
        
        method, endpoint = parts
        endpoint = self.resolve_vars(endpoint)
        
        payload = self.resolve_vars(step.get("payload", {}))
        headers = self.resolve_vars(step.get("headers", {}))
        expected_status = step.get("expect", 200)
        
        console.print(f"   👉 [bold]{name}[/bold] ({method} {endpoint})...", end=" ")
        
        # Execute HTTP request
        try:
            response = self.client.request(
                method,
                endpoint,
                json=payload if payload else None,
                headers=headers
            )
        except httpx.ConnectError as e:
            console.print(f"[red]FAILED (Connection Error)[/red]")
            self._record_failure(step_num, name, "Connection Error", str(e))
            return False
        except Exception as e:
            console.print(f"[red]FAILED (Network Error: {e})[/red]")
            self._record_failure(step_num, name, "Network Error", str(e))
            return False
        
        # Check status code
        if response.status_code != expected_status:
            console.print(f"[red]FAILED (Got {response.status_code}, Expected {expected_status})[/red]")
            self._generate_forensic_report(step_num, name, step, response, expected_status)
            return False
        
        # Capture variables from response
        if "capture" in step:
            try:
                data = response.json()
                for var_name, json_path in step["capture"].items():
                    # Simple extraction (flat or 1-level deep)
                    val = data.get(json_path)
                    if val:
                        self.context[var_name] = val
                        console.print(f"\n      📝 Captured {var_name} = {val}", end="")
            except Exception as e:
                console.print(f"\n      [yellow]⚠️  Failed to capture variables: {e}[/yellow]", end="")
        
        console.print(" [green]✅ OK[/green]")
        self._record_success(step_num, name, response)
        return True
    
    def _record_success(self, step_num: int, name: str, response: httpx.Response):
        """Record successful step."""
        self.step_results.append({
            "step": step_num,
            "name": name,
            "status": "PASS",
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds()
        })
    
    def _record_failure(self, step_num: int, name: str, error_type: str, error_msg: str):
        """Record failed step."""
        self.step_results.append({
            "step": step_num,
            "name": name,
            "status": "FAIL",
            "error_type": error_type,
            "error_msg": error_msg
        })
    
    def _generate_forensic_report(
        self,
        step_num: int,
        name: str,
        step: Dict,
        response: httpx.Response,
        expected_status: int
    ):
        """Generate detailed forensic crash report."""
        console.print("\n")
        console.print(Panel.fit(
            "🔬 FORENSIC CRASH REPORT",
            style="bold red"
        ))
        
        # Create forensic table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Step", f"#{step_num}: {name}")
        table.add_row("Action", step.get("action", "N/A"))
        table.add_row("Expected Status", str(expected_status))
        table.add_row("Actual Status", f"[red]{response.status_code}[/red]")
        
        # Show payload if present
        if step.get("payload"):
            import json
            payload_str = json.dumps(step["payload"], indent=2)
            table.add_row("Payload", payload_str)
        
        # Show headers if present
        if step.get("headers"):
            headers_str = "\n".join(f"{k}: {v}" for k, v in step["headers"].items())
            table.add_row("Headers", headers_str)
        
        # Show response
        try:
            response_json = response.json()
            response_str = json.dumps(response_json, indent=2)
            table.add_row("Server Response", response_str)
        except:
            table.add_row("Server Response", response.text[:500])
        
        console.print(table)
        console.print()
        
        # Record failure
        self._record_failure(
            step_num,
            name,
            f"Status {response.status_code}",
            response.text[:200]
        )
    
    def run_scenario(self, file_path: str) -> bool:
        """Execute complete simulation scenario."""
        scenario = self.load_scenario(file_path)
        scenario_name = scenario.get("scenario", "Unknown Scenario")
        
        console.print(f"\n[bold blue]🎬 SCENARIO: {scenario_name}[/bold blue]")
        console.print(f"[dim]File: {file_path}[/dim]\n")
        
        # Run setup if present
        if "setup" in scenario:
            console.print("[bold]📋 Setup Phase[/bold]")
            for setup_cmd in scenario["setup"]:
                console.print(f"   • {setup_cmd}")
            console.print()
        
        # Run steps
        console.print("[bold]🚀 Execution Phase[/bold]")
        steps = scenario.get("steps", [])
        
        for idx, step in enumerate(steps, 1):
            if not self.run_step(step, idx):
                console.print(f"\n[red]❌ Simulation stopped at step {idx}[/red]")
                return False
        
        return True
    
    def print_summary(self):
        """Print execution summary."""
        passed = sum(1 for r in self.step_results if r["status"] == "PASS")
        failed = sum(1 for r in self.step_results if r["status"] == "FAIL")
        total = len(self.step_results)
        
        console.print("\n" + "=" * 70)
        console.print("[bold]📊 SIMULATION SUMMARY[/bold]")
        console.print("=" * 70)
        
        if failed == 0:
            console.print(f"[green]✅ All {total} steps passed[/green]")
        else:
            console.print(f"[yellow]Steps: {passed} passed, {failed} failed, {total} total[/yellow]")
        
        # Show timing if available
        total_time = sum(
            r.get("response_time", 0)
            for r in self.step_results
            if r["status"] == "PASS"
        )
        if total_time > 0:
            console.print(f"[dim]Total response time: {total_time:.2f}s[/dim]")


def start_server(port: int = 8001) -> subprocess.Popen:
    """Start uvicorn server in background."""
    console.print(f"[yellow]🚀 Booting 'The Holodeck' (Live Environment on port {port})...[/yellow]")
    
    # Check if app/main.py exists
    if not os.path.exists("app/main.py"):
        console.print("[red]❌ app/main.py not found. Cannot start server.[/red]")
        sys.exit(1)
    
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to boot
    console.print("[dim]Waiting for server to boot...[/dim]")
    time.sleep(3)
    
    # Check if server is running
    try:
        import httpx
        response = httpx.get(f"http://127.0.0.1:{port}/", timeout=2)
        console.print(f"[green]✅ Server ready (status: {response.status_code})[/green]\n")
    except:
        console.print("[yellow]⚠️  Server may not be fully ready, proceeding anyway...[/yellow]\n")
    
    return process


def stop_server(process: subprocess.Popen):
    """Stop the server process."""
    console.print("\n[dim]🛑 Holodeck shutdown...[/dim]")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
