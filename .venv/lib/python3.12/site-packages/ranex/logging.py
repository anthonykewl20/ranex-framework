"""
Ranex CLI Logging System.

Provides structured logging for all CLI operations with:
- JSON Lines format for machine parsing
- Command timing and tracking
- Audit trail support
- Log rotation and retention
- Sensitive data filtering

Usage:
    from ranex.logging import get_cli_logger, log_command, CLILogEntry

    @log_command
    def my_command():
        logger = get_cli_logger()
        logger.info("Processing...", details={"step": 1})
"""

from __future__ import annotations

import functools
import getpass
import gzip
import json
import logging
import os
import re
import shutil
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar

# Type variable for decorator
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class CLILogEntry:
    """
    Structured log entry for CLI operations.

    Attributes:
        timestamp: ISO 8601 timestamp
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        command: CLI command name
        message: Human-readable message
        request_id: Unique ID for this request/session
        user: Username of the operator
        project_path: Path to the project being operated on
        duration_ms: Command execution time in milliseconds
        exit_code: Process exit code (0 = success)
        error_code: Ranex error code (if applicable)
        details: Additional structured data
    """
    timestamp: str
    level: str
    command: str
    message: str
    request_id: Optional[str] = None
    user: Optional[str] = None
    project_path: Optional[str] = None
    duration_ms: Optional[float] = None
    exit_code: Optional[int] = None
    error_code: Optional[int] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the record as JSON."""
        return record.getMessage()


# Patterns for sensitive data that should be filtered from logs
SENSITIVE_PATTERNS: List[tuple[str, str]] = [
    # API keys and tokens
    (r'(?i)(api[_-]?key|token|secret|password|auth)["\']?\s*[:=]\s*["\']?[\w\-\.]+', r'\1=***REDACTED***'),
    # Bearer tokens
    (r'(?i)bearer\s+[\w\-\.]+', 'Bearer ***REDACTED***'),
    # AWS credentials
    (r'(?i)(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key)\s*[:=]\s*[\w\+\/]+', r'\1=***REDACTED***'),
    # Private keys
    (r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----', '***PRIVATE_KEY_REDACTED***'),
    # Connection strings with passwords
    (r'(?i)(postgres|mysql|mongodb|redis)://[^:]+:[^@]+@', r'\1://***:***@'),
]


def filter_sensitive_data(data: Any) -> Any:
    """
    Recursively filter sensitive data from log entries.

    Args:
        data: Data to filter (string, dict, list, or other)

    Returns:
        Filtered data with sensitive values redacted
    """
    if isinstance(data, str):
        result = data
        for pattern, replacement in SENSITIVE_PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result
    elif isinstance(data, dict):
        return {k: filter_sensitive_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [filter_sensitive_data(item) for item in data]
    else:
        return data


@dataclass
class LogConfig:
    """Configuration for CLI logging."""
    log_dir: Path = field(default_factory=lambda: Path(".ranex/logs"))
    retention_days: int = 30
    max_file_size_mb: int = 10
    compress_old_logs: bool = True
    filter_sensitive: bool = True
    console_output: bool = False
    log_level: str = "INFO"


class CLILogger:
    """
    Logger for Ranex CLI operations.

    Provides structured JSON logging with:
    - Daily log files
    - Automatic rotation
    - Sensitive data filtering
    - Request ID tracking
    """

    def __init__(self, config: Optional[LogConfig] = None):
        """
        Initialize the CLI logger.

        Args:
            config: Optional logging configuration
        """
        self.config = config or LogConfig()
        self._current_request_id: Optional[str] = None
        self._logger: Optional[logging.Logger] = None
        self._file_handler: Optional[logging.FileHandler] = None
        self._current_log_file: Optional[Path] = None

        # Ensure log directory exists
        self.config.log_dir.mkdir(parents=True, exist_ok=True)

        self._setup_handlers()

    def _get_log_file_path(self) -> Path:
        """Get the path for today's log file."""
        return self.config.log_dir / f"cli_{datetime.now():%Y%m%d}.jsonl"

    def _setup_handlers(self) -> None:
        """Configure logging handlers."""
        self._logger = logging.getLogger("ranex.cli")
        self._logger.setLevel(getattr(logging, self.config.log_level.upper()))

        # Remove existing handlers
        self._logger.handlers.clear()

        # File handler (JSON lines format)
        log_file = self._get_log_file_path()
        self._current_log_file = log_file
        self._file_handler = logging.FileHandler(log_file, encoding="utf-8")
        self._file_handler.setFormatter(JSONFormatter())
        self._logger.addHandler(self._file_handler)

        # Console handler (optional)
        if self.config.console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(console_handler)

    def _check_rotation(self) -> None:
        """Check if log file needs rotation."""
        if self._current_log_file is None:
            return

        # Check if we need a new daily file
        expected_file = self._get_log_file_path()
        if expected_file != self._current_log_file:
            self._rotate_log()

        # Check file size
        if self._current_log_file.exists():
            size_mb = self._current_log_file.stat().st_size / (1024 * 1024)
            if size_mb >= self.config.max_file_size_mb:
                self._rotate_log()

    def _rotate_log(self) -> None:
        """Rotate the current log file."""
        if self._file_handler:
            self._logger.removeHandler(self._file_handler)
            self._file_handler.close()

        # Compress old log if configured
        if self.config.compress_old_logs and self._current_log_file and self._current_log_file.exists():
            self._compress_log(self._current_log_file)

        # Setup new handler
        self._setup_handlers()

        # Clean old logs
        self._cleanup_old_logs()

    def _compress_log(self, log_file: Path) -> None:
        """Compress a log file with gzip."""
        gz_file = log_file.with_suffix(log_file.suffix + ".gz")
        try:
            with open(log_file, 'rb') as f_in:
                with gzip.open(gz_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            log_file.unlink()  # Remove original after compression
        except Exception:
            pass  # Ignore compression errors

    def _cleanup_old_logs(self) -> None:
        """Remove logs older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.config.retention_days)

        for log_file in self.config.log_dir.glob("cli_*.jsonl*"):
            try:
                # Parse date from filename
                date_str = log_file.stem.replace("cli_", "").split(".")[0]
                file_date = datetime.strptime(date_str, "%Y%m%d")

                if file_date < cutoff:
                    log_file.unlink()
            except (ValueError, OSError):
                pass  # Ignore malformed filenames or deletion errors

    def generate_request_id(self) -> str:
        """Generate a unique request ID for this session."""
        self._current_request_id = str(uuid.uuid4())[:8]
        return self._current_request_id

    @property
    def request_id(self) -> Optional[str]:
        """Get the current request ID."""
        return self._current_request_id

    def _create_entry(
        self,
        level: str,
        command: str,
        message: str,
        **kwargs: Any
    ) -> CLILogEntry:
        """Create a log entry with common fields."""
        entry = CLILogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            command=command,
            message=message,
            request_id=self._current_request_id,
            user=kwargs.get("user"),
            project_path=kwargs.get("project_path"),
            duration_ms=kwargs.get("duration_ms"),
            exit_code=kwargs.get("exit_code"),
            error_code=kwargs.get("error_code"),
            details=kwargs.get("details"),
        )
        return entry

    def _log(self, entry: CLILogEntry) -> None:
        """Write a log entry."""
        self._check_rotation()

        # Filter sensitive data if configured
        if self.config.filter_sensitive:
            entry = CLILogEntry(**filter_sensitive_data(entry.to_dict()))

        log_line = entry.to_json()

        level = getattr(logging, entry.level.upper(), logging.INFO)
        self._logger.log(level, log_line)

    def log_command(self, entry: CLILogEntry) -> None:
        """
        Log a CLI command execution.

        Args:
            entry: The log entry to write
        """
        self._log(entry)

    def debug(self, command: str, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        entry = self._create_entry("DEBUG", command, message, **kwargs)
        self._log(entry)

    def info(self, command: str, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        entry = self._create_entry("INFO", command, message, **kwargs)
        self._log(entry)

    def warning(self, command: str, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        entry = self._create_entry("WARNING", command, message, **kwargs)
        self._log(entry)

    def error(self, command: str, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        entry = self._create_entry("ERROR", command, message, **kwargs)
        self._log(entry)

    def get_logs(
        self,
        command: Optional[str] = None,
        level: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve log entries.

        Args:
            command: Filter by command name
            level: Filter by log level
            since: Only entries after this time
            limit: Maximum entries to return

        Returns:
            List of log entries as dictionaries
        """
        results: List[Dict[str, Any]] = []

        # Get all log files, sorted by date (newest first)
        log_files = sorted(
            self.config.log_dir.glob("cli_*.jsonl"),
            key=lambda f: f.stem,
            reverse=True
        )

        for log_file in log_files:
            if len(results) >= limit:
                break

            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if len(results) >= limit:
                            break

                        try:
                            entry = json.loads(line.strip())

                            # Apply filters
                            if command and entry.get("command") != command:
                                continue
                            if level and entry.get("level") != level.upper():
                                continue
                            if since:
                                entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                                if entry_time < since:
                                    continue

                            results.append(entry)
                        except json.JSONDecodeError:
                            continue
            except OSError:
                continue

        return results

    def export_logs(
        self,
        output_path: Path,
        format: str = "json",
        **filters: Any
    ) -> int:
        """
        Export logs to a file.

        Args:
            output_path: Path to output file
            format: Output format ('json' or 'jsonl')
            **filters: Filters to pass to get_logs()

        Returns:
            Number of entries exported
        """
        logs = self.get_logs(**filters)

        with open(output_path, 'w', encoding='utf-8') as f:
            if format == "json":
                json.dump(logs, f, indent=2, default=str)
            else:  # jsonl
                for entry in logs:
                    f.write(json.dumps(entry, default=str) + "\n")

        return len(logs)


# Global logger instance
_logger: Optional[CLILogger] = None


def get_cli_logger(config: Optional[LogConfig] = None) -> CLILogger:
    """
    Get or create the global CLI logger instance.

    Args:
        config: Optional configuration (only used on first call)

    Returns:
        The global CLILogger instance
    """
    global _logger
    if _logger is None:
        _logger = CLILogger(config)
    return _logger


def log_command(func: F) -> F:
    """
    Decorator to log CLI command execution.

    Automatically logs:
    - Command start
    - Duration
    - Exit code
    - Errors (with error codes if RanexError)

    Usage:
        @app.command()
        @handle_errors
        @log_command
        def my_command():
            ...
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Import here to avoid circular imports
        from ranex.errors import RanexError

        logger = get_cli_logger()
        _ = logger.generate_request_id()  # Generate request ID for correlation
        start_time = time.time()
        command_name = func.__name__

        # Get user and project path
        try:
            user = getpass.getuser()
        except Exception:
            user = "unknown"

        project_path = os.getcwd()

        # Log command start
        logger.info(
            command=command_name,
            message=f"Command started: {command_name}",
            user=user,
            project_path=project_path,
        )

        exit_code = 0
        error_code = None
        error_message = None

        try:
            result = func(*args, **kwargs)
            return result
        except RanexError as e:
            exit_code = e.exit_code
            error_code = e.code.value
            error_message = str(e.message)
            raise
        except Exception as e:
            exit_code = 1
            error_message = str(e)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000

            if exit_code == 0:
                logger.info(
                    command=command_name,
                    message=f"Command completed: {command_name}",
                    user=user,
                    project_path=project_path,
                    duration_ms=round(duration_ms, 2),
                    exit_code=exit_code,
                )
            else:
                logger.error(
                    command=command_name,
                    message=f"Command failed: {command_name}",
                    user=user,
                    project_path=project_path,
                    duration_ms=round(duration_ms, 2),
                    exit_code=exit_code,
                    error_code=error_code,
                    details={"error": error_message} if error_message else None,
                )

    return wrapper  # type: ignore


# Export all public symbols
__all__ = [
    # Classes
    "CLILogEntry",
    "CLILogger",
    "LogConfig",
    "JSONFormatter",
    # Functions
    "get_cli_logger",
    "log_command",
    "filter_sensitive_data",
]

