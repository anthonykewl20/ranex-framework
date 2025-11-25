"""
Rate Limiting Middleware for Enterprise API Protection

Implements token bucket algorithm for rate limiting:
- Per-endpoint rate limits
- Per-client (IP) rate limits
- Configurable burst capacity
- Redis-backed for distributed systems (optional)
"""

import time
from typing import Optional, Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available. Rate limiting will use in-memory storage (not distributed).")


class TokenBucket:
    """
    Token bucket rate limiter.
    
    Algorithm:
    - Bucket has capacity tokens
    - Tokens refill at rate tokens_per_second
    - Request consumes 1 token
    - If no tokens available, request is rejected
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,  # tokens per second
        redis_client: Optional[redis.Redis] = None,
        redis_key_prefix: str = "rate_limit:",
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.redis_client = redis_client
        self.redis_key_prefix = redis_key_prefix
        
        # In-memory fallback (per-process, not distributed)
        self._buckets: Dict[str, Tuple[float, float]] = {}  # key -> (tokens, last_refill_time)

    async def _get_tokens_redis(self, key: str) -> Tuple[float, float]:
        """Get tokens from Redis."""
        if not self.redis_client:
            raise RuntimeError("Redis client not configured")
        
        redis_key = f"{self.redis_key_prefix}{key}"
        
        # Use Redis Lua script for atomic operations
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now
        
        -- Refill tokens
        local elapsed = now - last_refill
        tokens = math.min(capacity, tokens + (elapsed * refill_rate))
        
        -- Update bucket
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 3600)  -- Expire after 1 hour
        
        return {tokens, now}
        """
        
        result = await self.redis_client.eval(
            lua_script,
            1,
            redis_key,
            str(self.capacity),
            str(self.refill_rate),
            str(time.time()),
        )
        
        return (float(result[0]), float(result[1]))

    async def _consume_token_redis(self, key: str) -> bool:
        """Consume a token from Redis bucket."""
        redis_key = f"{self.redis_key_prefix}{key}"
        
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now
        
        -- Refill tokens
        local elapsed = now - last_refill
        tokens = math.min(capacity, tokens + (elapsed * refill_rate))
        
        -- Consume token if available
        if tokens >= 1.0 then
            tokens = tokens - 1.0
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)
            return 1
        else
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)
            return 0
        end
        """
        
        result = await self.redis_client.eval(
            lua_script,
            1,
            redis_key,
            str(self.capacity),
            str(self.refill_rate),
            str(time.time()),
        )
        
        return bool(result)

    def _get_tokens_memory(self, key: str) -> Tuple[float, float]:
        """Get tokens from in-memory bucket."""
        now = time.time()
        
        if key not in self._buckets:
            self._buckets[key] = (self.capacity, now)
            return (self.capacity, now)
        
        tokens, last_refill = self._buckets[key]
        
        # Refill tokens
        elapsed = now - last_refill
        tokens = min(self.capacity, tokens + (elapsed * self.refill_rate))
        
        self._buckets[key] = (tokens, now)
        return (tokens, now)

    def _consume_token_memory(self, key: str) -> bool:
        """Consume a token from in-memory bucket."""
        tokens, _ = self._get_tokens_memory(key)
        
        if tokens >= 1.0:
            tokens -= 1.0
            self._buckets[key] = (tokens, time.time())
            return True
        return False

    async def consume(self, key: str) -> Tuple[bool, int]:
        """
        Consume a token from the bucket.
        
        Returns:
            (allowed, remaining_tokens)
        """
        if self.redis_client:
            try:
                allowed = await self._consume_token_redis(key)
                tokens, _ = await self._get_tokens_redis(key)
                return (allowed, int(tokens))
            except Exception as e:
                logger.error(f"Redis rate limit error: {e}, falling back to memory")
                # Fallback to memory
                allowed = self._consume_token_memory(key)
                tokens, _ = self._get_tokens_memory(key)
                return (allowed, int(tokens))
        else:
            allowed = self._consume_token_memory(key)
            tokens, _ = self._get_tokens_memory(key)
            return (allowed, int(tokens))


class RateLimitConfig:
    """Rate limit configuration for an endpoint."""

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_capacity: Optional[int] = None,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_minute / 60.0
        self.burst_capacity = burst_capacity or requests_per_minute


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.
    
    Supports:
    - Per-endpoint rate limits
    - Per-client (IP) rate limits
    - Configurable limits
    - Redis-backed distributed rate limiting (optional)
    """

    def __init__(
        self,
        app,
        default_limit: RateLimitConfig = RateLimitConfig(requests_per_minute=60),
        endpoint_limits: Optional[Dict[str, RateLimitConfig]] = None,
        redis_client: Optional[redis.Redis] = None,
        enable_per_client: bool = True,
    ):
        super().__init__(app)
        self.default_limit = default_limit
        self.endpoint_limits = endpoint_limits or {}
        self.redis_client = redis_client
        self.enable_per_client = enable_per_client
        
        # Create token buckets
        self._buckets: Dict[str, TokenBucket] = {}
        self._init_buckets()

    def _init_buckets(self):
        """Initialize token buckets for configured endpoints."""
        # Default bucket
        default_bucket = TokenBucket(
            capacity=self.default_limit.burst_capacity,
            refill_rate=self.default_limit.requests_per_second,
            redis_client=self.redis_client,
        )
        self._buckets["default"] = default_bucket
        
        # Endpoint-specific buckets
        for endpoint, config in self.endpoint_limits.items():
            bucket = TokenBucket(
                capacity=config.burst_capacity,
                refill_rate=config.requests_per_second,
                redis_client=self.redis_client,
                redis_key_prefix=f"rate_limit:{endpoint}:",
            )
            self._buckets[endpoint] = bucket

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (IP address)."""
        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        if request.client:
            return request.client.host
        
        return "unknown"

    def _get_bucket_key(self, endpoint: str, client_id: Optional[str] = None) -> str:
        """Get bucket key for rate limiting."""
        if self.enable_per_client and client_id:
            return f"{endpoint}:{client_id}"
        return endpoint

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for metrics endpoint
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Get endpoint path
        endpoint = request.url.path
        
        # Get rate limit config for this endpoint
        config = self.endpoint_limits.get(endpoint, self.default_limit)
        bucket_key = endpoint
        
        # Add client ID if per-client limiting is enabled
        if self.enable_per_client:
            client_id = self._get_client_id(request)
            bucket_key = self._get_bucket_key(endpoint, client_id)
        
        # Get or create bucket
        bucket = self._buckets.get(endpoint, self._buckets["default"])
        
        # Consume token
        allowed, remaining = await bucket.consume(bucket_key)
        
        # Add rate limit headers
        response = await call_next(request) if allowed else None
        
        if not allowed:
            # Rate limit exceeded
            from app.commons.metrics import rate_limit_requests_total, rate_limit_remaining
            
            rate_limit_requests_total.labels(
                endpoint=endpoint,
                result="rejected",
            ).inc()
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {config.requests_per_minute} requests per minute",
                    "retry_after": 60,  # seconds
                },
                headers={
                    "X-RateLimit-Limit": str(config.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + 60),
                    "Retry-After": "60",
                },
            )
        
        # Request allowed
        from app.commons.metrics import rate_limit_requests_total, rate_limit_remaining
        
        rate_limit_requests_total.labels(
            endpoint=endpoint,
            result="allowed",
        ).inc()
        
        rate_limit_remaining.labels(
            endpoint=endpoint,
            identifier=bucket_key,
        ).set(remaining)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(config.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response


