"""
ML Inference Integration with Enterprise Metrics

Provides decorators and utilities for tracking ML inference operations
with Prometheus metrics and circuit breaker protection.
"""

import time
from typing import Optional, Callable, Any
from functools import wraps
import logging

from app.commons.metrics import ml_metrics
from app.commons.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    circuit_breaker_manager,
)

logger = logging.getLogger(__name__)


def track_ml_inference(
    model_name: str,
    model_version: str = "unknown",
    circuit_breaker_name: Optional[str] = None,
    circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
):
    """
    Decorator to track ML inference with metrics and circuit breaker.
    
    Usage:
        @track_ml_inference("vulnerability_classifier", "1.0.0")
        async def predict(code: str):
            return model.predict(code)
    
    Args:
        model_name: Name of the ML model
        model_version: Version of the ML model
        circuit_breaker_name: Name for circuit breaker (defaults to model_name)
        circuit_breaker_config: Circuit breaker configuration
    """
    def decorator(func: Callable) -> Callable:
        cb_name = circuit_breaker_name or model_name
        breaker = circuit_breaker_manager.get_breaker(cb_name, circuit_breaker_config)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            confidence = None
            error_type = None
            success = True
            
            try:
                # Execute with circuit breaker protection
                result = await breaker.call(func, *args, **kwargs)
                
                # Extract confidence if result has it
                if hasattr(result, "confidence"):
                    confidence = result.confidence
                elif isinstance(result, dict) and "confidence" in result:
                    confidence = result["confidence"]
                
                return result
                
            except Exception as e:
                success = False
                error_type = type(e).__name__
                raise
                
            finally:
                # Record metrics
                duration = time.time() - start_time
                ml_metrics.record_inference_context(
                    model_name=model_name,
                    model_version=model_version,
                    duration=duration,
                    confidence=confidence,
                    success=success,
                    error_type=error_type,
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            confidence = None
            error_type = None
            success = True
            
            try:
                # Execute with circuit breaker protection
                result = breaker.call(func, *args, **kwargs)
                
                # Extract confidence if result has it
                if hasattr(result, "confidence"):
                    confidence = result.confidence
                elif isinstance(result, dict) and "confidence" in result:
                    confidence = result["confidence"]
                
                return result
                
            except Exception as e:
                success = False
                error_type = type(e).__name__
                raise
                
            finally:
                # Record metrics
                duration = time.time() - start_time
                ml_metrics.record_inference_context(
                    model_name=model_name,
                    model_version=model_version,
                    duration=duration,
                    confidence=confidence,
                    success=success,
                    error_type=error_type,
                )
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class MLInferenceTracker:
    """
    Context manager for tracking ML inference operations.
    
    Usage:
        tracker = MLInferenceTracker("model_v1", "1.0.0")
        with tracker:
            result = model.predict(data)
        tracker.record_confidence(result.confidence)
    """
    
    def __init__(
        self,
        model_name: str,
        model_version: str = "unknown",
        circuit_breaker_name: Optional[str] = None,
    ):
        self.model_name = model_name
        self.model_version = model_version
        self.circuit_breaker_name = circuit_breaker_name or model_name
        self.breaker = circuit_breaker_manager.get_breaker(self.circuit_breaker_name)
        self.start_time: Optional[float] = None
        self.confidence: Optional[float] = None
        self.success = True
        self.error_type: Optional[str] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is not None:
            self.success = False
            self.error_type = exc_type.__name__
        
        ml_metrics.record_inference_context(
            model_name=self.model_name,
            model_version=self.model_version,
            duration=duration,
            confidence=self.confidence,
            success=self.success,
            error_type=self.error_type,
        )
        
        return False  # Don't suppress exceptions
    
    def record_confidence(self, confidence: float):
        """Record prediction confidence score."""
        self.confidence = confidence


