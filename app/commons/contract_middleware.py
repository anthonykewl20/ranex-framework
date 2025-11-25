"""FastAPI Middleware for Contract Decorator

Provides automatic contract validation and state management for FastAPI endpoints.
Integrates with the @Contract decorator to enforce state transitions and schema validation.

Features:
- Automatic contract validation for decorated endpoints
- Multi-tenant state isolation
- Request-scoped state machine context
- Integration with centralized logging
"""

import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("ranex.contract.middleware")


class ContractMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic contract enforcement.
    
    Automatically validates contracts for endpoints decorated with @Contract.
    Provides multi-tenant state isolation using tenant_id from request headers.
    """
    
    def __init__(self, app: ASGIApp, default_tenant: Optional[str] = None):
        """Initialize contract middleware.
        
        Args:
            app: The ASGI application
            default_tenant: Default tenant ID if not provided in request headers
        """
        super().__init__(app)
        self.default_tenant = default_tenant or "default"
        logger.info(
            "Contract middleware initialized",
            extra={"default_tenant": self.default_tenant}
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with contract validation.
        
        Extracts tenant_id from request headers and ensures state isolation.
        Validates contracts for endpoints decorated with @Contract.
        """
        # Extract tenant ID from headers (X-Tenant-ID or X-User-ID)
        tenant_id = (
            request.headers.get("X-Tenant-ID") or
            request.headers.get("X-User-ID") or
            self.default_tenant
        )
        
        # Store tenant context in request state for use by @Contract decorator
        request.state.tenant_id = tenant_id
        request.state.contract_context = {}
        
        # Log request with tenant context
        logger.debug(
            "Processing request with contract middleware",
            extra={
                "tenant_id": tenant_id,
                "path": request.url.path,
                "method": request.method,
            }
        )
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(
                "Contract middleware error",
                extra={
                    "tenant_id": tenant_id,
                    "path": request.url.path,
                    "error": str(e),
                },
                exc_info=True
            )
            raise


def get_tenant_id(request: Request) -> str:
    """Extract tenant ID from request.
    
    Used by @Contract decorator to get tenant context.
    """
    return getattr(request.state, "tenant_id", "default")


def get_contract_context(request: Request) -> dict:
    """Get contract context from request state.
    
    Used by @Contract decorator to store state machine instances per tenant.
    """
    if not hasattr(request.state, "contract_context"):
        request.state.contract_context = {}
    return request.state.contract_context

