#!/usr/bin/env python3
"""
Ranex Framework - FastAPI Middleware Demo

This demo showcases Ranex middleware for FastAPI applications.
It demonstrates:
1. Contract middleware
2. Rate limiting
3. Health checks
4. Prometheus metrics

Run: python examples/fastapi_middleware_demo.py
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ranex import Contract


app = FastAPI(title="Ranex FastAPI Middleware Demo")


# Example: Contract Middleware
# This would typically be added via app.add_middleware()
# For demo purposes, we show the concept

@app.middleware("http")
async def contract_middleware(request: Request, call_next):
    """
    Contract middleware example.
    
    In production, use ContractMiddleware from ranex.commons.contract_middleware
    """
    # Extract tenant ID from headers
    tenant_id = request.headers.get("X-Tenant-ID", "default")
    
    # Add tenant context to request state
    request.state.tenant_id = tenant_id
    
    # Process request
    response = await call_next(request)
    
    # Add contract headers
    response.headers["X-Contract-Validated"] = "true"
    
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ranex-fastapi-demo",
        "version": "0.0.1"
    }


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    
    In production, use PrometheusMiddleware from ranex.commons.metrics
    """
    return {
        "requests_total": 100,
        "requests_per_second": 10.5,
        "error_rate": 0.02
    }


@app.get("/")
@Contract(feature="demo")
async def root(_ctx):
    """Root endpoint with contract enforcement."""
    return {
        "message": "Ranex FastAPI Middleware Demo",
        "features": [
            "Contract middleware",
            "Rate limiting",
            "Health checks",
            "Prometheus metrics"
        ]
    }


def demo_fastapi_middleware():
    """Demonstrate FastAPI middleware capabilities."""
    print("=" * 70)
    print("Ranex Framework - FastAPI Middleware Demo")
    print("=" * 70)
    print()
    
    print("✅ FastAPI application created with middleware")
    print()
    
    print("📝 Available Middleware:")
    print("-" * 70)
    print("1. Contract Middleware:")
    print("   • Multi-tenant support")
    print("   • Request context tracking")
    print("   • Contract validation")
    print()
    print("2. Rate Limiter Middleware:")
    print("   • Request rate limiting")
    print("   • Per-tenant limits")
    print("   • Configurable thresholds")
    print()
    print("3. Health Check Middleware:")
    print("   • Application health monitoring")
    print("   • Dependency checks")
    print("   • Readiness probes")
    print()
    print("4. Prometheus Metrics Middleware:")
    print("   • Request metrics")
    print("   • Performance monitoring")
    print("   • ML inference tracking")
    print()
    
    print("📝 Integration Example:")
    print("-" * 70)
    print("""
from fastapi import FastAPI
from ranex.commons.contract_middleware import ContractMiddleware
from ranex.commons.rate_limiter import RateLimiterMiddleware
from ranex.commons.health import HealthChecker, create_health_router
from ranex.commons.metrics import PrometheusMiddleware

app = FastAPI()

# Add middleware
app.add_middleware(ContractMiddleware)
app.add_middleware(RateLimiterMiddleware, requests_per_minute=100)
app.add_middleware(PrometheusMiddleware)

# Add health check router
health_router = create_health_router()
app.include_router(health_router)
""")
    print()
    
    print("📝 Benefits:")
    print("-" * 70)
    print("  • Enterprise-grade middleware")
    print("  • Multi-tenant support")
    print("  • Rate limiting and protection")
    print("  • Health monitoring")
    print("  • Performance metrics")
    print("  • Production-ready")
    print()
    
    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("  • Try examples/fastapi_contract_demo.py for contract integration")
    print("  • See examples/fastapi_demo/ for complete application")
    print("  • Read docs/ENTERPRISE_FEATURES.md for middleware details")


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    print("Visit http://localhost:8000/docs for API documentation")
    print("Health check: http://localhost:8000/health")
    print("Metrics: http://localhost:8000/metrics")
    print("Press Ctrl+C to stop")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)

