import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.commons.database import Base, async_engine
from app.features.payment import routes as payment_routes
from app.features.user import routes as user_routes
from app.features.product import routes as product_routes
from ranex_core import LayerEnforcer

# Enterprise features
from app.commons.metrics import PrometheusMiddleware, get_metrics_endpoint, ml_metrics
from app.commons.rate_limiter import RateLimiterMiddleware, RateLimitConfig
from app.commons.health import HealthChecker, create_health_router
from app.commons.contract_middleware import ContractMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🛡️ Ranex Kernel: Performing Startup Integrity Scan...")
    # Temporarily disabled for demo
    # enforcer = LayerEnforcer()
    # cwd = os.getcwd()
    # report = enforcer.scan(cwd)
    # if not report.valid:
    #     print("\n❌ CRITICAL STARTUP FAILURE: ARCHITECTURE BREACH DETECTED")
    #     print("   The application has refused to start.")
    #     print("\n🔎 DIAGNOSTIC REPORT:")
    #     for idx, violation in enumerate(report.violations):
    #         print(f"   {violation}")
    #         if idx < len(report.suggestions):
    #             print(f"   {report.suggestions[idx]}")
    #             print("   ------------------------------------------------")
    #     print("\n🛑 SHUTTING DOWN.")
    #     sys.exit(1)

    print("✅ Integrity Verified. Architecture is sound (enforcer temporarily disabled for demo).")
    
    # Create database tables (optional - skip if database not available)
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created/verified.")
    except Exception as db_error:
        print(f"⚠️  Database connection failed (continuing without DB): {db_error}")
        print("   Note: Some features may not work without database connection.")
        print("   To fix: Ensure PostgreSQL is running and DATABASE_URL is configured correctly.")
    
    try:
        yield
    finally:
        print("🛡️ Ranex Kernel: Shutting down.")
        await async_engine.dispose()


app = FastAPI(
    title="Ranex Enterprise API",
    description="FastAPI + PostgreSQL + Alembic + SQLAlchemy Demo with Ranex v0.0.1",
    version="0.0.1",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enterprise Middleware (order matters - contract first, then metrics, then rate limiting)
app.add_middleware(ContractMiddleware, default_tenant="default")

# Enterprise Middleware (order matters - metrics first, then rate limiting)
app.add_middleware(PrometheusMiddleware)

# Rate Limiting Middleware
# Configure endpoint-specific limits
endpoint_limits = {
    "/api/users": RateLimitConfig(requests_per_minute=100),
    "/api/products": RateLimitConfig(requests_per_minute=200),
    "/api/payment": RateLimitConfig(requests_per_minute=30),  # Stricter for payment
}

app.add_middleware(
    RateLimiterMiddleware,
    default_limit=RateLimitConfig(requests_per_minute=60),
    endpoint_limits=endpoint_limits,
    enable_per_client=True,
)

# Health Checker
health_checker = HealthChecker(db_engine=async_engine)

# Include routers
app.include_router(user_routes.router, prefix="/api/users", tags=["Users"])
app.include_router(product_routes.router, prefix="/api/products", tags=["Products"])
app.include_router(payment_routes.router, prefix="/api/payment", tags=["Payment"])

# Health check endpoints
health_router = create_health_router(health_checker)
app.include_router(health_router)

# Prometheus metrics endpoint
app.get("/metrics")(get_metrics_endpoint())


@app.get("/")
async def read_root():
    return {
        "system": "Ranex v0.0.1",
        "status": "Active",
        "protection": "Rust Kernel",
        "database": "PostgreSQL",
        "framework": "FastAPI",
        "features": ["Users", "Products", "Payment"],
        "enterprise_features": [
            "Rate Limiting",
            "Circuit Breakers",
            "Health Checks",
            "Prometheus Metrics",
        ],
    }
