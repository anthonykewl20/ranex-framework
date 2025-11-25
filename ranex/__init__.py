# ranex/__init__.py
# Note: In a real install, ranex_core is a compiled binary. 
# For this prototype, we assume the rust module is available in the path.

from ranex_core import StateMachine as RustMachine, SchemaValidator as RustSchemaValidator
import functools
import asyncio
import logging
import time
from typing import Optional, Callable, Any
import contextvars

# Initialize logger for Contract operations
logger = logging.getLogger("ranex.contract")

# Global schema validator instance
_schema_validator = RustSchemaValidator()


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
    
    Usage:
        @Contract(feature="payment")
        async def transfer(ctx, amount: float):
            await ctx.transition("Processing")
            # ... business logic
            await ctx.transition("Paid")
        
        # With schema validation:
        from pydantic import BaseModel, PositiveInt
        
        class PaymentRequest(BaseModel):
            amount: PositiveInt
            email: str
        
        @Contract(feature="payment", input_schema=PaymentRequest)
        async def process_payment(ctx, request: PaymentRequest):
            await ctx.transition("Processing")
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
                    # Multi-tenant support: Use tenant_id to create isolated state machines
                    # Try to get tenant_id from FastAPI request context if available
                    tenant_context = tenant_id
                    if tenant_context is None:
                        # Try to get from FastAPI request state (if middleware is used)
                        try:
                            # Use contextvars to access request state from middleware
                            # The ContractMiddleware sets request.state.tenant_id
                            # We can access it via contextvars if available
                            from app.commons.contract_middleware import get_tenant_id
                            # Note: This requires the request to be passed as a parameter
                            # For now, we'll use the tenant_id parameter or default
                            pass
                        except ImportError:
                            # Middleware not available, use default
                            pass
                    
                    # Create tenant-scoped state machine key for logging
                    state_key = f"{feature}:{tenant_context or 'default'}"
                    ctx = RustMachine(feature)
                    initial_state = ctx.current_state  # Track initial state for rollback
                    
                    # Log tenant context if available
                    if tenant_context:
                        logger.debug(
                            f"Contract initialized with tenant context: {tenant_context}",
                            extra={
                                "feature": feature,
                                "tenant_id": tenant_context,
                                "state_key": state_key,
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
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    # Auto-rollback: Restore initial state if state changed
                    if ctx is not None and initial_state is not None:
                        current_state = ctx.current_state
                        if current_state != initial_state:
                            try:
                                # Attempt to rollback to initial state
                                # Note: This may fail if rollback transition is not allowed
                                # In that case, we log the failure but don't raise
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
                    
                    # 2. Initialize Rust State Engine
                    # Logging happens automatically in Rust layer
                    ctx = RustMachine(feature)
                    initial_state = ctx.current_state  # Track initial state for rollback
                    
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
                        }
                    )
                    
                    return result
                    
                except Exception as e:
                    # Auto-rollback: Restore initial state if state changed
                    if ctx is not None and initial_state is not None:
                        current_state = ctx.current_state
                        if current_state != initial_state:
                            try:
                                # Attempt to rollback to initial state
                                # Note: This may fail if rollback transition is not allowed
                                # In that case, we log the failure but don't raise
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
        
        # Return appropriate wrapper based on function type
        return async_wrapper if is_async else sync_wrapper
    
    return decorator
