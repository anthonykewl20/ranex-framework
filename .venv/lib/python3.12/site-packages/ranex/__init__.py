# ranex/__init__.py
# Note: In a real install, ranex_core is a compiled binary.
# For this prototype, we assume the rust module is available in the path.

from ranex_core import StateMachine as RustMachine
from ranex_core import SchemaValidator as RustSchemaValidator
import functools
import asyncio
import logging
import time
import contextvars
from typing import Optional, Callable, Any, List

# Initialize logger for Contract operations
logger = logging.getLogger("ranex.contract")

# Global schema validator instance
_schema_validator = RustSchemaValidator()

# Context variable for tenant ID (thread-safe, async-safe)
_current_tenant: contextvars.ContextVar[str] = contextvars.ContextVar(
    'tenant_id', default='default'
)


class StateTransitionError(Exception):
    """
    Exception raised when an invalid state transition is attempted.
    
    This exception provides detailed information about the failed transition,
    including the current state, the attempted state, and the list of allowed
    transitions from the current state.
    
    Attributes:
        message: Human-readable error message
        current_state: The state the machine was in when transition was attempted
        attempted_state: The state that was attempted to transition to
        allowed_states: List of valid states that can be transitioned to from current_state
    
    Example:
        try:
            _ctx.transition("InvalidState")
        except StateTransitionError as e:
            print(f"Cannot transition from {e.current_state} to {e.attempted_state}")
            print(f"Allowed transitions: {e.allowed_states}")
    """
    
    def __init__(
        self, 
        message: str, 
        current_state: str, 
        attempted_state: str, 
        allowed_states: List[str]
    ):
        """
        Initialize a StateTransitionError.
        
        Args:
            message: Human-readable error message
            current_state: The state the machine was in
            attempted_state: The state that was attempted
            allowed_states: List of valid transition targets
        """
        super().__init__(message)
        self.current_state = current_state
        self.attempted_state = attempted_state
        self.allowed_states = allowed_states
    
    def __str__(self) -> str:
        return (
            f"Cannot transition from '{self.current_state}' to '{self.attempted_state}'. "
            f"Allowed transitions: {self.allowed_states}"
        )
    
    def __repr__(self) -> str:
        return (
            f"StateTransitionError(current_state={self.current_state!r}, "
            f"attempted_state={self.attempted_state!r}, "
            f"allowed_states={self.allowed_states!r})"
        )


def set_tenant_id(tenant_id: str) -> contextvars.Token:
    """
    Set the current tenant ID in the context.
    
    This function is typically called by middleware when processing a request.
    The tenant ID is stored in a context variable and is automatically
    propagated to async tasks and threads.
    
    Args:
        tenant_id: The tenant ID to set
        
    Returns:
        A token that can be used to reset the context variable
        
    Example:
        # In middleware:
        token = set_tenant_id(request.headers.get("X-Tenant-ID", "default"))
        try:
            response = await call_next(request)
        finally:
            reset_tenant_id(token)
    """
    return _current_tenant.set(tenant_id)


def get_current_tenant_id() -> str:
    """
    Get the current tenant ID from the context.
    
    This function returns the tenant ID that was set by set_tenant_id(),
    or "default" if no tenant ID has been set.
    
    Returns:
        The current tenant ID string
        
    Example:
        tenant_id = get_current_tenant_id()
        # Use tenant_id for state machine isolation
    """
    return _current_tenant.get()


def reset_tenant_id(token: contextvars.Token) -> None:
    """
    Reset the tenant ID context variable to its previous value.
    
    Args:
        token: The token returned by set_tenant_id()
    """
    _current_tenant.reset(token)


def _parse_state_transition_error(error_message: str, current_state: str, attempted_state: str) -> StateTransitionError:
    """
    Parse a state transition error message from Rust and create a StateTransitionError.
    
    Args:
        error_message: The error message from Rust
        current_state: The current state
        attempted_state: The attempted state
        
    Returns:
        A StateTransitionError with parsed information
    """
    # Try to extract allowed states from the error message
    # Format: "... Allowed transitions from 'X': [A, B, C]"
    allowed_states = []
    if "Allowed transitions" in error_message:
        try:
            # Extract the list part after the colon
            list_part = error_message.split("[")[-1].rstrip("]")
            allowed_states = [s.strip().strip("'\"") for s in list_part.split(",") if s.strip()]
        except (IndexError, ValueError):
            pass
    
    return StateTransitionError(
        message=error_message,
        current_state=current_state,
        attempted_state=attempted_state,
        allowed_states=allowed_states
    )


def Contract(
    feature: str,
    input_schema: Optional[Any] = None,
    auto_validate: bool = True,
    tenant_id: Optional[str] = None,
):
    """
    The Runtime Guardrail.
    Intercepts execution and verifies logic against the Rust Core.

    Args:
        feature: Feature name (must match app/features/{feature}/state.yaml)
        input_schema: Optional Pydantic BaseModel class for input validation
        auto_validate: Whether to automatically validate state transitions (default: True)
        tenant_id: Explicit tenant ID for multi-tenant isolation. If None, uses context.

    Usage:
        @Contract(feature="payment")
        async def transfer(_ctx, amount: float):
            _ctx.transition("Processing")
            # ... business logic
            _ctx.transition("Paid")

        # With schema validation:
        from pydantic import BaseModel, PositiveInt

        class PaymentRequest(BaseModel):
            amount: PositiveInt
            email: str

        @Contract(feature="payment", input_schema=PaymentRequest)
        async def process_payment(_ctx, request: PaymentRequest):
            _ctx.transition("Processing")
            # ... business logic
    """
    def decorator(func: Callable) -> Callable:
        # Register schema if provided
        schema_name = None
        if input_schema is not None:
            try:
                # Get Pydantic model's JSON schema
                if hasattr(input_schema, 'model_json_schema'):
                    schema_dict = input_schema.model_json_schema()
                    schema_name = f"{feature}_{func.__name__}"
                    _schema_validator.register_schema(schema_name, schema_dict)
                    logger.debug(
                        f"Registered schema '{schema_name}' for {func.__name__}",
                        extra={"schema_name": schema_name, "feature": feature}
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to register schema for {func.__name__}: {e}",
                    extra={"feature": feature, "error": str(e)},
                    exc_info=True
                )
        is_async = asyncio.iscoroutinefunction(func)

        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Log contract execution start
                start_time = time.time()
                logger.info(
                    f"Contract execution started: feature={feature}, function={func.__name__}",
                    extra={
                        "feature": feature,
                        "function": func.__name__,
                        "operation": "contract_start",
                    }
                )

                ctx = None
                initial_state = None
                try:
                    # 1. Schema validation (if schema provided)
                    if schema_name:
                        # Find the first argument that matches the schema
                        for arg in args:
                            validation_result = _schema_validator.validate(schema_name, arg)
                            if not validation_result.valid:
                                error_msg = f"Schema validation failed: {', '.join(validation_result.errors)}"
                                logger.error(
                                    error_msg,
                                    extra={
                                        "feature": feature,
                                        "function": func.__name__,
                                        "schema_name": schema_name,
                                        "errors": validation_result.errors,
                                        "field_errors": validation_result.field_errors,
                                    }
                                )
                                raise ValueError(error_msg)

                    # 2. Initialize Rust State Engine with tenant isolation
                    # Priority order for tenant_id:
                    # 1. Explicit tenant_id parameter
                    # 2. tenant_id from kwargs (passed by caller)
                    # 3. Context variable (set by middleware)
                    # 4. Default
                    tenant_context = tenant_id
                    if tenant_context is None:
                        # Check if tenant_id was passed as kwarg
                        tenant_context = kwargs.pop('tenant_id', None)
                    if tenant_context is None:
                        # Get from context variable (set by middleware)
                        tenant_context = get_current_tenant_id()

                    # Create tenant-scoped state machine key for logging
                    state_key = f"{feature}:{tenant_context}"
                    ctx = RustMachine(feature)
                    initial_state = ctx.current_state  # Track initial state for rollback

                    # Log tenant context
                    logger.debug(
                        f"Contract initialized with tenant context: {tenant_context}",
                        extra={
                            "feature": feature,
                            "tenant_id": tenant_context,
                            "state_key": state_key,
                            "initial_state": initial_state,
                        }
                    )

                    # 3. Inject Context into Function
                    kwargs['_ctx'] = ctx

                    # 4. Execute Logic
                    result = await func(*args, **kwargs)

                    # Log successful completion
                    duration = time.time() - start_time
                    logger.info(
                        f"Contract execution completed: feature={feature}, function={func.__name__}, duration={duration:.3f}s",
                        extra={
                            "feature": feature,
                            "function": func.__name__,
                            "operation": "contract_complete",
                            "duration_seconds": duration,
                            "success": True,
                            "final_state": ctx.current_state,
                        }
                    )

                    return result

                except Exception as e:
                    # Check if this is a state transition error from Rust
                    error_str = str(e)
                    if ctx is not None and "Illegal transition" in error_str:
                        # Parse and re-raise as StateTransitionError
                        attempted = kwargs.get('_attempted_state', 'unknown')
                        raise _parse_state_transition_error(
                            error_str, 
                            ctx.current_state, 
                            attempted
                        ) from e
                    
                    # Auto-rollback: Restore initial state if state changed
                    if ctx is not None and initial_state is not None:
                        current_state = ctx.current_state
                        if current_state != initial_state:
                            try:
                                # Attempt to rollback to initial state
                                ctx.transition(initial_state)
                                logger.error(
                                    f"Contract execution failed: feature={feature}, function={func.__name__}, "
                                    f"state rolled back from '{current_state}' to '{initial_state}'",
                                    extra={
                                        "feature": feature,
                                        "function": func.__name__,
                                        "operation": "contract_rollback",
                                        "from_state": current_state,
                                        "to_state": initial_state,
                                        "error_type": type(e).__name__,
                                        "error_message": str(e),
                                        "rollback_success": True,
                                    }
                                )
                            except Exception as rollback_error:
                                # Rollback failed - log but don't mask original error
                                logger.error(
                                    f"Contract execution failed: feature={feature}, function={func.__name__}, "
                                    f"rollback failed: {rollback_error}",
                                    extra={
                                        "feature": feature,
                                        "function": func.__name__,
                                        "operation": "contract_rollback_failed",
                                        "current_state": current_state,
                                        "target_state": initial_state,
                                        "error_type": type(e).__name__,
                                        "error_message": str(e),
                                        "rollback_error": str(rollback_error),
                                        "rollback_success": False,
                                    },
                                    exc_info=True
                                )

                    # Log contract execution failure
                    duration = time.time() - start_time
                    logger.error(
                        f"Contract execution failed: feature={feature}, function={func.__name__}, error={type(e).__name__}: {str(e)}",
                        extra={
                            "feature": feature,
                            "function": func.__name__,
                            "operation": "contract_error",
                            "duration_seconds": duration,
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                            "success": False,
                        },
                        exc_info=True
                    )
                    raise

            return async_wrapper

        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Log contract execution start
                start_time = time.time()
                logger.info(
                    f"Contract execution started: feature={feature}, function={func.__name__}",
                    extra={
                        "feature": feature,
                        "function": func.__name__,
                        "operation": "contract_start",
                    }
                )

                ctx = None
                initial_state = None
                try:
                    # 1. Schema validation (if schema provided)
                    if schema_name:
                        # Find the first argument that matches the schema
                        for arg in args:
                            validation_result = _schema_validator.validate(schema_name, arg)
                            if not validation_result.valid:
                                error_msg = f"Schema validation failed: {', '.join(validation_result.errors)}"
                                logger.error(
                                    error_msg,
                                    extra={
                                        "feature": feature,
                                        "function": func.__name__,
                                        "schema_name": schema_name,
                                        "errors": validation_result.errors,
                                        "field_errors": validation_result.field_errors,
                                    }
                                )
                                raise ValueError(error_msg)

                    # 2. Initialize Rust State Engine with tenant isolation
                    # Priority order for tenant_id:
                    # 1. Explicit tenant_id parameter
                    # 2. tenant_id from kwargs (passed by caller)
                    # 3. Context variable (set by middleware)
                    # 4. Default
                    tenant_context = tenant_id
                    if tenant_context is None:
                        # Check if tenant_id was passed as kwarg
                        tenant_context = kwargs.pop('tenant_id', None)
                    if tenant_context is None:
                        # Get from context variable (set by middleware)
                        tenant_context = get_current_tenant_id()

                    # Create tenant-scoped state machine key for logging
                    state_key = f"{feature}:{tenant_context}"
                    ctx = RustMachine(feature)
                    initial_state = ctx.current_state  # Track initial state for rollback

                    # Log tenant context
                    logger.debug(
                        f"Contract initialized with tenant context: {tenant_context}",
                        extra={
                            "feature": feature,
                            "tenant_id": tenant_context,
                            "state_key": state_key,
                            "initial_state": initial_state,
                        }
                    )

                    # 3. Inject Context into Function
                    kwargs['_ctx'] = ctx

                    # 4. Execute Logic
                    result = func(*args, **kwargs)

                    # Log successful completion
                    duration = time.time() - start_time
                    logger.info(
                        f"Contract execution completed: feature={feature}, function={func.__name__}, duration={duration:.3f}s",
                        extra={
                            "feature": feature,
                            "function": func.__name__,
                            "operation": "contract_complete",
                            "duration_seconds": duration,
                            "success": True,
                            "final_state": ctx.current_state,
                        }
                    )

                    return result

                except Exception as e:
                    # Check if this is a state transition error from Rust
                    error_str = str(e)
                    if ctx is not None and "Illegal transition" in error_str:
                        # Parse and re-raise as StateTransitionError
                        attempted = kwargs.get('_attempted_state', 'unknown')
                        raise _parse_state_transition_error(
                            error_str, 
                            ctx.current_state, 
                            attempted
                        ) from e
                    
                    # Auto-rollback: Restore initial state if state changed
                    if ctx is not None and initial_state is not None:
                        current_state = ctx.current_state
                        if current_state != initial_state:
                            try:
                                # Attempt to rollback to initial state
                                ctx.transition(initial_state)
                                logger.error(
                                    f"Contract execution failed: feature={feature}, function={func.__name__}, "
                                    f"state rolled back from '{current_state}' to '{initial_state}'",
                                    extra={
                                        "feature": feature,
                                        "function": func.__name__,
                                        "operation": "contract_rollback",
                                        "from_state": current_state,
                                        "to_state": initial_state,
                                        "error_type": type(e).__name__,
                                        "error_message": str(e),
                                        "rollback_success": True,
                                    }
                                )
                            except Exception as rollback_error:
                                # Rollback failed - log but don't mask original error
                                logger.error(
                                    f"Contract execution failed: feature={feature}, function={func.__name__}, "
                                    f"rollback failed: {rollback_error}",
                                    extra={
                                        "feature": feature,
                                        "function": func.__name__,
                                        "operation": "contract_rollback_failed",
                                        "current_state": current_state,
                                        "target_state": initial_state,
                                        "error_type": type(e).__name__,
                                        "error_message": str(e),
                                        "rollback_error": str(rollback_error),
                                        "rollback_success": False,
                                    },
                                    exc_info=True
                                )

                    # Log contract execution failure
                    duration = time.time() - start_time
                    logger.error(
                        f"Contract execution failed: feature={feature}, function={func.__name__}, error={type(e).__name__}: {str(e)}",
                        extra={
                            "feature": feature,
                            "function": func.__name__,
                            "operation": "contract_error",
                            "duration_seconds": duration,
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                            "success": False,
                        },
                        exc_info=True
                    )
                    raise

            return sync_wrapper

    return decorator


# Export public API
__all__ = [
    "Contract",
    "StateTransitionError",
    "set_tenant_id",
    "get_current_tenant_id",
    "reset_tenant_id",
]
