"""
Ranex CLI Error Handling System.

Provides structured error codes, exit codes, and error handling utilities
for consistent error reporting across all CLI commands.

Usage:
    from ranex.errors import RanexError, ErrorCode, handle_errors

    @handle_errors
    def my_command():
        if something_wrong:
            raise RanexError(
                code=ErrorCode.VALIDATION_FAILED,
                message="Something went wrong",
                hint="Try running 'ranex fix' first"
            )
"""

from __future__ import annotations

import functools
import os
import traceback
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional, TypeVar

import typer
from rich.console import Console

# Type variable for decorator
F = TypeVar("F", bound=Callable[..., Any])

# Shared console instance
_console: Optional[Console] = None


def get_console() -> Console:
    """Get or create the shared console instance."""
    global _console
    if _console is None:
        _console = Console(stderr=True)
    return _console


class ExitCode(IntEnum):
    """
    Standard exit codes for Ranex CLI.

    Based on sysexits.h conventions for consistent behavior across
    Unix-like systems.
    """
    SUCCESS = 0
    GENERAL_ERROR = 1
    VALIDATION_FAILED = 2
    USAGE_ERROR = 64          # EX_USAGE - command line usage error
    DATA_ERROR = 65           # EX_DATAERR - data format error
    NO_INPUT = 66             # EX_NOINPUT - input file not found
    NO_USER = 67              # EX_NOUSER - user not found
    NO_HOST = 68              # EX_NOHOST - host not found
    UNAVAILABLE = 69          # EX_UNAVAILABLE - service unavailable
    SOFTWARE_ERROR = 70       # EX_SOFTWARE - internal software error
    OS_ERROR = 71             # EX_OSERR - system error
    OS_FILE = 72              # EX_OSFILE - critical OS file missing
    CANT_CREATE = 73          # EX_CANTCREAT - can't create output
    IO_ERROR = 74             # EX_IOERR - I/O error
    TEMP_FAILURE = 75         # EX_TEMPFAIL - temporary failure
    PROTOCOL_ERROR = 76       # EX_PROTOCOL - remote protocol error
    PERMISSION_DENIED = 77    # EX_NOPERM - permission denied
    CONFIG_ERROR = 78         # EX_CONFIG - configuration error
    INTERRUPTED = 130         # Ctrl+C (128 + SIGINT)


class ErrorCode(IntEnum):
    """
    Unique error codes for Ranex CLI.

    Error codes are organized by category:
    - 1000-1099: General errors
    - 1100-1199: Integrity/attestation errors
    - 1200-1299: Validation errors
    - 1300-1399: Configuration errors
    - 1400-1499: Workflow errors
    - 1500-1599: Database errors
    - 1600-1699: Persona errors
    - 1700-1799: File/IO errors
    - 1800-1899: Network errors
    """
    # General (1000-1099)
    UNKNOWN_ERROR = 1000
    COMMAND_NOT_FOUND = 1001
    INVALID_ARGUMENT = 1002
    OPERATION_CANCELLED = 1003
    TIMEOUT = 1004
    NOT_IMPLEMENTED = 1005

    # Integrity (1100-1199)
    INTEGRITY_VIOLATION = 1100
    ATTESTATION_INVALID = 1101
    HASH_MISMATCH = 1102
    SIGNATURE_INVALID = 1103
    ATTESTATION_NOT_FOUND = 1104
    ATTESTATION_EXPIRED = 1105

    # Validation (1200-1299)
    VALIDATION_FAILED = 1200
    STRUCTURE_VIOLATION = 1201
    IMPORT_VIOLATION = 1202
    ARCHITECTURE_VIOLATION = 1203
    STATE_TRANSITION_INVALID = 1204
    SCHEMA_VIOLATION = 1205
    FORBIDDEN_PACKAGE = 1206
    LAYER_VIOLATION = 1207

    # Configuration (1300-1399)
    CONFIG_NOT_FOUND = 1300
    CONFIG_INVALID = 1301
    CONFIG_PERMISSION = 1302
    CONFIG_PARSE_ERROR = 1303
    CONFIG_MISSING_FIELD = 1304
    CONFIG_TYPE_ERROR = 1305

    # Workflow (1400-1499)
    WORKFLOW_LOCKED = 1400
    PHASE_TRANSITION_INVALID = 1401
    TASK_NOT_FOUND = 1402
    TASK_ALREADY_EXISTS = 1403
    WORKFLOW_NOT_INITIALIZED = 1404
    DESIGN_REQUIRED = 1405
    REQUIREMENTS_REQUIRED = 1406

    # Database (1500-1599)
    DATABASE_CONNECTION_FAILED = 1500
    DATABASE_QUERY_INVALID = 1501
    DATABASE_NOT_FOUND = 1502
    DATABASE_PERMISSION = 1503
    DATABASE_SCHEMA_ERROR = 1504

    # Persona (1600-1699)
    PERSONA_NOT_FOUND = 1600
    PERSONA_INVALID = 1601
    PERSONA_ALREADY_EXISTS = 1602
    PERSONA_PARSE_ERROR = 1603
    PERSONA_NOT_SET = 1604

    # File/IO (1700-1799)
    FILE_NOT_FOUND = 1700
    FILE_PERMISSION = 1701
    FILE_EXISTS = 1702
    DIRECTORY_NOT_FOUND = 1703
    DIRECTORY_NOT_EMPTY = 1704
    IO_ERROR = 1705

    # Network (1800-1899)
    NETWORK_ERROR = 1800
    CONNECTION_REFUSED = 1801
    CONNECTION_TIMEOUT = 1802
    SSL_ERROR = 1803


# Mapping from error code ranges to exit codes
_EXIT_CODE_MAPPING: List[tuple[range, ExitCode]] = [
    (range(1100, 1200), ExitCode.DATA_ERROR),        # Integrity
    (range(1200, 1300), ExitCode.VALIDATION_FAILED), # Validation
    (range(1300, 1400), ExitCode.CONFIG_ERROR),      # Configuration
    (range(1400, 1500), ExitCode.USAGE_ERROR),       # Workflow
    (range(1500, 1600), ExitCode.UNAVAILABLE),       # Database
    (range(1600, 1700), ExitCode.NO_INPUT),          # Persona
    (range(1700, 1800), ExitCode.IO_ERROR),          # File/IO
    (range(1800, 1900), ExitCode.UNAVAILABLE),       # Network
]


def _get_exit_code_for_error(error_code: ErrorCode) -> ExitCode:
    """Map an error code to an appropriate exit code."""
    for code_range, exit_code in _EXIT_CODE_MAPPING:
        if error_code.value in code_range:
            return exit_code
    return ExitCode.GENERAL_ERROR


@dataclass
class RanexError(Exception):
    """
    Structured error for Ranex CLI.

    Provides consistent error reporting with:
    - Unique error codes for programmatic handling
    - Human-readable messages
    - Optional details for debugging
    - Hints for resolution

    Attributes:
        code: The unique error code
        message: Human-readable error message
        details: Additional context (shown with --verbose)
        hint: Suggestion for how to fix the error
    """
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = field(default=None)
    hint: Optional[str] = field(default=None)

    def __post_init__(self) -> None:
        # Initialize the Exception base class
        super().__init__(self.message)

    @property
    def exit_code(self) -> int:
        """Get the appropriate exit code for this error."""
        return _get_exit_code_for_error(self.code)

    @property
    def error_id(self) -> str:
        """Get the formatted error ID (e.g., 'RANEX-1200')."""
        return f"RANEX-{self.code.value}"

    def format(self, verbose: bool = False) -> str:
        """
        Format the error for display.

        Args:
            verbose: Include details if True

        Returns:
            Formatted error string
        """
        parts = [f"[{self.error_id}] {self.message}"]

        if verbose and self.details:
            for key, value in self.details.items():
                parts.append(f"  {key}: {value}")

        if self.hint:
            parts.append(f"\nHint: {self.hint}")

        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "error_id": self.error_id,
            "code": self.code.value,
            "code_name": self.code.name,
            "message": self.message,
            "details": self.details,
            "hint": self.hint,
            "exit_code": self.exit_code,
        }


# Global verbose flag (set by CLI)
_verbose_mode: bool = False
_json_errors_mode: bool = False


def set_verbose_mode(verbose: bool) -> None:
    """Enable or disable verbose error output."""
    global _verbose_mode
    _verbose_mode = verbose


def set_json_errors_mode(json_errors: bool) -> None:
    """Enable or disable JSON error output."""
    global _json_errors_mode
    _json_errors_mode = json_errors


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return _verbose_mode or os.environ.get("RANEX_VERBOSE", "").lower() in ("1", "true", "yes")


def is_json_errors() -> bool:
    """Check if JSON errors mode is enabled."""
    return _json_errors_mode or os.environ.get("RANEX_JSON_ERRORS", "").lower() in ("1", "true", "yes")


def handle_errors(func: F) -> F:
    """
    Decorator for consistent CLI error handling.

    Wraps a CLI command function to catch and format errors consistently.

    - RanexError: Formatted with error code and hint
    - typer.Exit: Passed through unchanged
    - KeyboardInterrupt: Clean exit with message
    - Other exceptions: Logged with traceback (in verbose mode)

    Usage:
        @app.command()
        @handle_errors
        def my_command():
            ...
    """
    import json

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        console = get_console()
        try:
            return func(*args, **kwargs)
        except RanexError as e:
            if is_json_errors():
                # Output as JSON for machine parsing
                print(json.dumps(e.to_dict()), file=console.file)
            else:
                console.print(f"[red]❌ {e.format(verbose=is_verbose())}[/red]")
            raise typer.Exit(code=e.exit_code)
        except typer.Exit:
            # Let typer handle its own exits
            raise
        except KeyboardInterrupt:
            if is_json_errors():
                error_data = {
                    "error_id": "RANEX-1003",
                    "code": ErrorCode.OPERATION_CANCELLED.value,
                    "code_name": "OPERATION_CANCELLED",
                    "message": "Interrupted by user",
                    "exit_code": ExitCode.INTERRUPTED,
                }
                print(json.dumps(error_data), file=console.file)
            else:
                console.print("\n[yellow]⚠️  Interrupted by user[/yellow]")
            raise typer.Exit(code=ExitCode.INTERRUPTED)
        except Exception as e:
            # Unexpected error
            if is_json_errors():
                error_data = {
                    "error_id": "RANEX-1000",
                    "code": ErrorCode.UNKNOWN_ERROR.value,
                    "code_name": "UNKNOWN_ERROR",
                    "message": f"Unexpected error: {e}",
                    "details": {"traceback": traceback.format_exc()} if is_verbose() else None,
                    "exit_code": ExitCode.GENERAL_ERROR,
                }
                print(json.dumps(error_data), file=console.file)
            else:
                console.print(f"[red]❌ [{ErrorCode.UNKNOWN_ERROR.name}] Unexpected error: {e}[/red]")
                if is_verbose():
                    console.print("[dim]" + traceback.format_exc() + "[/dim]")
                else:
                    console.print("[dim]Run with RANEX_VERBOSE=1 for details[/dim]")
            raise typer.Exit(code=ExitCode.GENERAL_ERROR)

    return wrapper  # type: ignore


# Convenience error constructors
def validation_error(
    message: str,
    *,
    code: ErrorCode = ErrorCode.VALIDATION_FAILED,
    details: Optional[Dict[str, Any]] = None,
    hint: Optional[str] = None,
) -> RanexError:
    """Create a validation error."""
    return RanexError(code=code, message=message, details=details, hint=hint)


def config_error(
    message: str,
    *,
    code: ErrorCode = ErrorCode.CONFIG_INVALID,
    details: Optional[Dict[str, Any]] = None,
    hint: Optional[str] = None,
) -> RanexError:
    """Create a configuration error."""
    return RanexError(code=code, message=message, details=details, hint=hint)


def workflow_error(
    message: str,
    *,
    code: ErrorCode = ErrorCode.WORKFLOW_LOCKED,
    details: Optional[Dict[str, Any]] = None,
    hint: Optional[str] = None,
) -> RanexError:
    """Create a workflow error."""
    return RanexError(code=code, message=message, details=details, hint=hint)


def file_error(
    message: str,
    *,
    code: ErrorCode = ErrorCode.FILE_NOT_FOUND,
    path: Optional[str] = None,
    hint: Optional[str] = None,
) -> RanexError:
    """Create a file/IO error."""
    details = {"path": path} if path else None
    return RanexError(code=code, message=message, details=details, hint=hint)


def persona_error(
    message: str,
    *,
    code: ErrorCode = ErrorCode.PERSONA_NOT_FOUND,
    persona_id: Optional[str] = None,
    hint: Optional[str] = None,
) -> RanexError:
    """Create a persona error."""
    details = {"persona_id": persona_id} if persona_id else None
    return RanexError(code=code, message=message, details=details, hint=hint)


def integrity_error(
    message: str,
    *,
    code: ErrorCode = ErrorCode.INTEGRITY_VIOLATION,
    files: Optional[List[str]] = None,
    hint: Optional[str] = None,
) -> RanexError:
    """Create an integrity error."""
    details = {"files": files} if files else None
    return RanexError(code=code, message=message, details=details, hint=hint)


def database_error(
    message: str,
    *,
    code: ErrorCode = ErrorCode.DATABASE_CONNECTION_FAILED,
    details: Optional[Dict[str, Any]] = None,
    hint: Optional[str] = None,
) -> RanexError:
    """Create a database error."""
    return RanexError(code=code, message=message, details=details, hint=hint)


# Export all public symbols
__all__ = [
    # Enums
    "ExitCode",
    "ErrorCode",
    # Main error class
    "RanexError",
    # Decorator
    "handle_errors",
    # Utilities
    "get_console",
    "set_verbose_mode",
    "is_verbose",
    # Error constructors
    "validation_error",
    "config_error",
    "workflow_error",
    "file_error",
    "persona_error",
    "integrity_error",
    "database_error",
]

