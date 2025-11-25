"""
Circuit Breaker Pattern for Enterprise Resilience

Implements circuit breaker to prevent cascading failures:
- Opens circuit after failure threshold
- Half-open state for recovery testing
- Automatic recovery after timeout
- Configurable failure thresholds
"""

import time
from enum import Enum
from typing import Optional, Callable, Any, Dict
from dataclasses import dataclass, field
import asyncio
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    
    failure_threshold: int = 5  # Open circuit after N failures
    success_threshold: int = 2  # Close circuit after N successes (half-open -> closed)
    timeout_seconds: float = 60.0  # Time before attempting recovery (open -> half-open)
    expected_exception: type = Exception  # Exception type to catch


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker."""
    
    failures: int = 0
    successes: int = 0
    total_requests: int = 0
    state_changes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    opened_at: Optional[float] = None


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    
    def __init__(self, service_name: str, retry_after: Optional[float] = None):
        self.service_name = service_name
        self.retry_after = retry_after
        message = f"Circuit breaker is OPEN for service '{service_name}'"
        if retry_after:
            message += f". Retry after {retry_after:.1f} seconds"
        super().__init__(message)


class CircuitBreaker:
    """
    Circuit breaker implementation.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failing, reject all requests immediately
    - HALF_OPEN: Testing recovery, allow limited requests
    
    Transitions:
    - CLOSED -> OPEN: After failure_threshold failures
    - OPEN -> HALF_OPEN: After timeout_seconds
    - HALF_OPEN -> CLOSED: After success_threshold successes
    - HALF_OPEN -> OPEN: After any failure
    """

    def __init__(
        self,
        service_name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ):
        self.service_name = service_name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
        
        # Import metrics (avoid circular import)
        try:
            from app.commons.metrics import (
                circuit_breaker_state,
                circuit_breaker_failures_total,
                circuit_breaker_requests_rejected_total,
            )
            self._metrics_available = True
            self._circuit_breaker_state = circuit_breaker_state
            self._circuit_breaker_failures = circuit_breaker_failures_total
            self._circuit_breaker_rejected = circuit_breaker_requests_rejected_total
        except ImportError:
            self._metrics_available = False
            logger.warning("Metrics not available for circuit breaker")

    def _update_metrics(self):
        """Update Prometheus metrics."""
        if not self._metrics_available:
            return
        
        state_value = {
            CircuitState.CLOSED: 0,
            CircuitState.OPEN: 1,
            CircuitState.HALF_OPEN: 2,
        }[self.state]
        
        self._circuit_breaker_state.labels(service_name=self.service_name).set(state_value)

    def _transition_to_open(self):
        """Transition circuit to OPEN state."""
        if self.state != CircuitState.OPEN:
            logger.warning(
                f"Circuit breaker '{self.service_name}' opened after {self.stats.failures} failures"
            )
            self.state = CircuitState.OPEN
            self.stats.opened_at = time.time()
            self.stats.state_changes += 1
            self._update_metrics()

    def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state."""
        if self.state != CircuitState.HALF_OPEN:
            logger.info(
                f"Circuit breaker '{self.service_name}' entering HALF_OPEN state (testing recovery)"
            )
            self.state = CircuitState.HALF_OPEN
            self.stats.successes = 0  # Reset success counter
            self.stats.state_changes += 1
            self._update_metrics()

    def _transition_to_closed(self):
        """Transition circuit to CLOSED state."""
        if self.state != CircuitState.CLOSED:
            logger.info(
                f"Circuit breaker '{self.service_name}' closed after {self.stats.successes} successes"
            )
            self.state = CircuitState.CLOSED
            self.stats.failures = 0  # Reset failure counter
            self.stats.state_changes += 1
            self._update_metrics()

    def _should_attempt_recovery(self) -> bool:
        """Check if circuit should attempt recovery (OPEN -> HALF_OPEN)."""
        if self.state != CircuitState.OPEN:
            return False
        
        if self.stats.opened_at is None:
            return False
        
        elapsed = time.time() - self.stats.opened_at
        return elapsed >= self.config.timeout_seconds

    async def call(
        self,
        func: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original exception from function
        """
        async with self._lock:
            # Check if circuit should attempt recovery
            if self._should_attempt_recovery():
                self._transition_to_half_open()
            
            # Reject if circuit is open
            if self.state == CircuitState.OPEN:
                if self._metrics_available:
                    self._circuit_breaker_rejected.labels(
                        service_name=self.service_name,
                    ).inc()
                
                retry_after = None
                if self.stats.opened_at:
                    elapsed = time.time() - self.stats.opened_at
                    retry_after = max(0, self.config.timeout_seconds - elapsed)
                
                raise CircuitBreakerError(self.service_name, retry_after)
            
            # Execute function
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Success
                self.stats.successes += 1
                self.stats.total_requests += 1
                self.stats.last_success_time = time.time()
                
                # Transition from HALF_OPEN to CLOSED if threshold met
                if (
                    self.state == CircuitState.HALF_OPEN
                    and self.stats.successes >= self.config.success_threshold
                ):
                    self._transition_to_closed()
                
                return result
                
            except self.config.expected_exception as e:
                # Failure
                self.stats.failures += 1
                self.stats.total_requests += 1
                self.stats.last_failure_time = time.time()
                
                if self._metrics_available:
                    error_type = type(e).__name__
                    self._circuit_breaker_failures.labels(
                        service_name=self.service_name,
                        error_type=error_type,
                    ).inc()
                
                # Transition to OPEN if threshold met
                if self.stats.failures >= self.config.failure_threshold:
                    self._transition_to_open()
                
                # Transition from HALF_OPEN to OPEN on any failure
                if self.state == CircuitState.HALF_OPEN:
                    self._transition_to_open()
                
                # Re-raise original exception
                raise

    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        async def _reset():
            async with self._lock:
                self.state = CircuitState.CLOSED
                self.stats = CircuitBreakerStats()
                self._update_metrics()
                logger.info(f"Circuit breaker '{self.service_name}' manually reset")
        
        # Run in event loop if available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule for later
                asyncio.create_task(_reset())
            else:
                loop.run_until_complete(_reset())
        except RuntimeError:
            # No event loop, create new one
            asyncio.run(_reset())

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "service_name": self.service_name,
            "state": self.state.value,
            "failures": self.stats.failures,
            "successes": self.stats.successes,
            "total_requests": self.stats.total_requests,
            "state_changes": self.stats.state_changes,
            "last_failure_time": self.stats.last_failure_time,
            "last_success_time": self.stats.last_success_time,
            "opened_at": self.stats.opened_at,
        }


class CircuitBreakerManager:
    """Manager for multiple circuit breakers."""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(
        self,
        service_name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ) -> CircuitBreaker:
        """Get or create circuit breaker for service."""
        if service_name not in self._breakers:
            self._breakers[service_name] = CircuitBreaker(service_name, config)
        return self._breakers[service_name]
    
    def reset_all(self):
        """Reset all circuit breakers."""
        for breaker in self._breakers.values():
            breaker.reset()


# Global manager instance
circuit_breaker_manager = CircuitBreakerManager()


