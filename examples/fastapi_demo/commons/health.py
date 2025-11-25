"""
Enhanced Health Checks for Enterprise Deployment

Provides comprehensive health check endpoints:
- Liveness probe: Is the application running?
- Readiness probe: Can the application serve traffic?
- Startup probe: Has the application finished starting?
- Health check with detailed component status
"""

import time
from typing import Dict, List, Optional, Any
from enum import Enum
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncEngine
import logging

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"  # Partially functional


class ComponentHealth:
    """Health status of a component."""
    
    def __init__(
        self,
        name: str,
        status: HealthStatus,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
        }


class HealthChecker:
    """
    Health checker for application components.
    
    Checks:
    - Database connectivity
    - Redis connectivity (if configured)
    - ML model availability (if configured)
    - System resources
    """
    
    def __init__(
        self,
        db_engine: Optional[AsyncEngine] = None,
        redis_client: Optional[Any] = None,
        ml_model_loader: Optional[callable] = None,
    ):
        self.db_engine = db_engine
        self.redis_client = redis_client
        self.ml_model_loader = ml_model_loader
        self.start_time = time.time()
    
    async def check_database(self) -> ComponentHealth:
        """Check database connectivity."""
        if not self.db_engine:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message="Database engine not configured",
            )
        
        try:
            async with self.db_engine.begin() as conn:
                await conn.execute("SELECT 1")
            
            return ComponentHealth(
                name="database",
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
            )
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                details={"error": str(e)},
            )
    
    async def check_redis(self) -> ComponentHealth:
        """Check Redis connectivity."""
        if not self.redis_client:
            return ComponentHealth(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis not configured (optional)",
            )
        
        try:
            await self.redis_client.ping()
            return ComponentHealth(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
            )
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return ComponentHealth(
                name="redis",
                status=HealthStatus.DEGRADED,
                message=f"Redis connection failed: {str(e)}",
                details={"error": str(e)},
            )
    
    async def check_ml_models(self) -> ComponentHealth:
        """Check ML model availability."""
        if not self.ml_model_loader:
            return ComponentHealth(
                name="ml_models",
                status=HealthStatus.HEALTHY,
                message="ML models not configured (optional)",
            )
        
        try:
            # Try to load/check model
            model_available = await self.ml_model_loader()
            if model_available:
                return ComponentHealth(
                    name="ml_models",
                    status=HealthStatus.HEALTHY,
                    message="ML models available",
                )
            else:
                return ComponentHealth(
                    name="ml_models",
                    status=HealthStatus.DEGRADED,
                    message="ML models not loaded",
                )
        except Exception as e:
            logger.warning(f"ML model health check failed: {e}")
            return ComponentHealth(
                name="ml_models",
                status=HealthStatus.DEGRADED,
                message=f"ML model check failed: {str(e)}",
                details={"error": str(e)},
            )
    
    async def check_system_resources(self) -> ComponentHealth:
        """Check system resource availability."""
        try:
            import psutil
            
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Check CPU usage (1 second average)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Determine status
            if memory_percent > 90 or cpu_percent > 90:
                status_val = HealthStatus.DEGRADED
                message = "High resource usage"
            else:
                status_val = HealthStatus.HEALTHY
                message = "Resources available"
            
            return ComponentHealth(
                name="system_resources",
                status=status_val,
                message=message,
                details={
                    "memory_percent": memory_percent,
                    "cpu_percent": cpu_percent,
                    "memory_available_mb": memory.available / (1024 * 1024),
                },
            )
        except ImportError:
            return ComponentHealth(
                name="system_resources",
                status=HealthStatus.HEALTHY,
                message="Resource monitoring not available (psutil not installed)",
            )
        except Exception as e:
            logger.warning(f"System resource check failed: {e}")
            return ComponentHealth(
                name="system_resources",
                status=HealthStatus.DEGRADED,
                message=f"Resource check failed: {str(e)}",
            )
    
    async def check_all(self) -> List[ComponentHealth]:
        """Check all components."""
        checks = [
            await self.check_database(),
            await self.check_redis(),
            await self.check_ml_models(),
            await self.check_system_resources(),
        ]
        return checks
    
    def get_overall_status(self, components: List[ComponentHealth]) -> HealthStatus:
        """Determine overall status from components."""
        has_unhealthy = any(c.status == HealthStatus.UNHEALTHY for c in components)
        has_degraded = any(c.status == HealthStatus.DEGRADED for c in components)
        
        if has_unhealthy:
            return HealthStatus.UNHEALTHY
        elif has_degraded:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


def create_health_router(health_checker: HealthChecker) -> APIRouter:
    """
    Create FastAPI router with health check endpoints.
    
    Endpoints:
    - GET /health - Detailed health check
    - GET /health/live - Liveness probe (always 200 if app is running)
    - GET /health/ready - Readiness probe (200 if ready to serve traffic)
    - GET /health/startup - Startup probe (200 if startup complete)
    """
    router = APIRouter()
    
    @router.get("/health")
    async def health_check():
        """Detailed health check with component status."""
        components = await health_checker.check_all()
        overall_status = health_checker.get_overall_status(components)
        
        response_data = {
            "status": overall_status.value,
            "uptime_seconds": int(time.time() - health_checker.start_time),
            "components": [c.to_dict() for c in components],
        }
        
        # Determine HTTP status code
        http_status = status.HTTP_200_OK
        if overall_status == HealthStatus.UNHEALTHY:
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif overall_status == HealthStatus.DEGRADED:
            http_status = status.HTTP_200_OK  # Still serve traffic, but degraded
        
        return JSONResponse(content=response_data, status_code=http_status)
    
    @router.get("/health/live")
    async def liveness_probe():
        """
        Liveness probe for Kubernetes.
        
        Returns 200 if application is running (even if unhealthy).
        Kubernetes will restart the pod if this fails.
        """
        return {"status": "alive"}
    
    @router.get("/health/ready")
    async def readiness_probe():
        """
        Readiness probe for Kubernetes.
        
        Returns 200 only if application is ready to serve traffic.
        Kubernetes will stop sending traffic if this fails.
        """
        components = await health_checker.check_all()
        overall_status = health_checker.get_overall_status(components)
        
        # Critical components must be healthy for readiness
        critical_components = ["database"]
        critical_healthy = all(
            c.status == HealthStatus.HEALTHY
            for c in components
            if c.name in critical_components
        )
        
        if critical_healthy and overall_status != HealthStatus.UNHEALTHY:
            return {"status": "ready"}
        else:
            return JSONResponse(
                content={"status": "not_ready", "reason": "Critical components unhealthy"},
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
    
    @router.get("/health/startup")
    async def startup_probe():
        """
        Startup probe for Kubernetes.
        
        Returns 200 when application has finished starting.
        Kubernetes will wait before marking pod as ready.
        """
        # Check if startup is complete (e.g., database initialized)
        components = await health_checker.check_all()
        db_healthy = any(
            c.name == "database" and c.status == HealthStatus.HEALTHY
            for c in components
        )
        
        if db_healthy:
            return {"status": "started"}
        else:
            return JSONResponse(
                content={"status": "starting"},
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
    
    return router


