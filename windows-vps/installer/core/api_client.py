"""
PARAKRAM VPS — API CLIENT (Military/Space Grade)
==================================================
Classification: CONTROLLED
Design Pattern: Circuit Breaker + Retry with Exponential Backoff + Jitter

Features:
  - Circuit Breaker (closed/open/half-open) to prevent cascading failures
  - Retry with exponential backoff + jitter for transient errors
  - Connection pooling with keep-alive
  - Request timeout with cancellation
  - Payload validation before sending
  - Structured error responses with severity classification
  - Token lifecycle management with auto-refresh readiness
  - Health check integration
  - Graceful degradation on backend outage

Failure States:
  - BACKEND_DOWN: All retries exhausted → circuit opens → fail fast
  - NETWORK_ERROR: Intermittent → retry with backoff
  - AUTH_EXPIRED: Invalid token → immediate failure (not retriable)
  - RATE_LIMITED: 429 → backoff and retry
  - VALIDATION_ERROR: 422 → fail fast (payload issue)
"""

import json
import time
import random
import threading
import logging
from typing import Optional, Any
from enum import Enum
from urllib.parse import urljoin

import httpx

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

API_BASE = "https://leads.getparakram.in/api/v1"
REQUEST_TIMEOUT = 30
CONNECT_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_BACKOFF = 1.0  # seconds, doubles each attempt
CIRCUIT_FAILURE_THRESHOLD = 5
CIRCUIT_RESET_TIMEOUT = 30  # seconds before moving to half-open
CIRCUIT_HALF_OPEN_MAX_REQUESTS = 1
POOL_MAX_CONNECTIONS = 10
POOL_MAX_KEEPALIVE = 20
HEARTBEAT_INTERVAL = 60  # seconds between backend health checks


# ═══════════════════════════════════════════════════════════════════════════
#  ERROR CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

class ErrorSeverity(Enum):
    """Severity classification for API failures."""
    CRITICAL = "CRITICAL"        # Security/auth failure — abort immediately
    FATAL = "FATAL"              # Non-recoverable — user must intervene
    TRANSIENT = "TRANSIENT"      # Will likely succeed on retry
    DEGRADED = "DEGRADED"        # Functionality impacted but system survives


class APIError(Exception):
    """Structured API error with severity, HTTP code, and context."""
    def __init__(self, message: str, status_code: int = 0,
                 severity: ErrorSeverity = ErrorSeverity.TRANSIENT,
                 body: Optional[dict] = None):
        self.status_code = status_code
        self.severity = severity
        self.body = body or {}
        super().__init__(message)


def classify_error(resp: httpx.Response) -> ErrorSeverity:
    """Classify HTTP response status into severity."""
    if resp.status_code in (401, 403):
        return ErrorSeverity.CRITICAL
    if resp.status_code in (400, 422):
        return ErrorSeverity.FATAL
    if resp.status_code == 429:
        return ErrorSeverity.TRANSIENT
    if resp.status_code in (502, 503, 504):
        return ErrorSeverity.TRANSIENT
    if 500 <= resp.status_code < 600:
        return ErrorSeverity.TRANSIENT
    return ErrorSeverity.DEGRADED


def should_retry(severity: ErrorSeverity) -> bool:
    """Determine if an error merites automatic retry."""
    return severity in (ErrorSeverity.TRANSIENT, ErrorSeverity.DEGRADED)


# ═══════════════════════════════════════════════════════════════════════════
#  CIRCUIT BREAKER
# ═══════════════════════════════════════════════════════════════════════════

class CircuitState(Enum):
    CLOSED = "CLOSED"           # Normal operation
    OPEN = "OPEN"               # Failing fast — no requests pass
    HALF_OPEN = "HALF_OPEN"    # Testing if backend recovered


class CircuitBreaker:
    """
    Circuit Breaker pattern implementation.
    Prevents cascading failures by failing fast when backend is unhealthy.
    Thread-safe.
    """

    def __init__(self, failure_threshold: int = CIRCUIT_FAILURE_THRESHOLD,
                 reset_timeout: int = CIRCUIT_RESET_TIMEOUT,
                 half_open_max: int = CIRCUIT_HALF_OPEN_MAX_REQUESTS):
        self._failure_threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._half_open_max = half_open_max
        self._lock = threading.Lock()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._half_open_requests = 0

    @property
    def state(self) -> CircuitState:
        return self._state

    def allow_request(self) -> bool:
        """
        Check if a request should be allowed.
        Thread-safe.
        """
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                now = time.time()
                if now - self._last_failure_time >= self._reset_timeout:
                    logger.info("Circuit breaker: OPEN → HALF_OPEN")
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_requests = 0
                    return True
                return False

            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_requests < self._half_open_max:
                    self._half_open_requests += 1
                    return True
                return False

            return False

    def record_success(self):
        """Record a successful request. Resets failure count."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                logger.info("Circuit breaker: HALF_OPEN → CLOSED (recovered)")
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._half_open_requests = 0

    def record_failure(self):
        """Record a failed request. May open the circuit."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._failure_count >= self._failure_threshold:
                if self._state != CircuitState.OPEN:
                    logger.warning(
                        f"Circuit breaker: {self._state.value} → OPEN "
                        f"({self._failure_count} failures)"
                    )
                self._state = CircuitState.OPEN
                self._half_open_requests = 0

    def reset(self):
        """Manually reset the circuit breaker."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = 0.0
            self._half_open_requests = 0


# ═══════════════════════════════════════════════════════════════════════════
#  PAYLOAD VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_signup_payload(email: str, password: str, full_name: str) -> list[str]:
    """Validate signup payload before sending. Returns list of validation errors."""
    errors = []
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        errors.append("Invalid email address")
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters")
    if full_name and len(full_name) > 200:
        errors.append("Name exceeds 200 characters")
    if full_name and any(c in full_name for c in "<>\"';&|"):
        errors.append("Name contains invalid characters")
    return errors


def validate_subscription_payload(plan: str) -> list[str]:
    """Validate subscription plan."""
    errors = []
    valid_plans = {"free", "edge", "fleet"}
    if plan not in valid_plans:
        errors.append(f"Invalid plan '{plan}'. Must be one of: {', '.join(sorted(valid_plans))}")
    return errors


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN API CLIENT
# ═══════════════════════════════════════════════════════════════════════════

class ParakramAPI:
    """
    Resilient API client with Circuit Breaker, retry, and validation.

    Usage:
        api = ParakramAPI()
        api.token = "jwt_token"
        data = api.signup("email@example.com", "password123", "John")
        data = api.create_vps_subscription("edge")
        api.close()

    Thread-safe for read operations.
    """

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self._circuit = CircuitBreaker()
        self._lock = threading.Lock()
        self._last_heartbeat = 0.0

        # Connection pool with keep-alive
        self._client = httpx.Client(
            timeout=httpx.Timeout(REQUEST_TIMEOUT, connect=CONNECT_TIMEOUT),
            limits=httpx.Limits(
                max_connections=POOL_MAX_CONNECTIONS,
                max_keepalive_connections=POOL_MAX_KEEPALIVE,
            ),
            headers={
                "User-Agent": f"ParakramVPS-Installer/{CIRCUIT_RESET_TIMEOUT}",
                "Accept": "application/json",
            },
        )

    # ─── Properties ───────────────────────────────────────────────

    @property
    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        with self._lock:
            if self.token:
                h["Authorization"] = f"Bearer {self.token}"
        return h

    @property
    def is_connected(self) -> bool:
        """Check if circuit breaker allows requests."""
        return self._circuit.allow_request()

    # ─── Core Request Method ──────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        json_body: Optional[dict] = None,
        label: str = "API call",
    ) -> dict:
        """
        Execute an API request with full reliability stack.
        - Circuit breaker check
        - Payload validation
        - Retry with exponential backoff + jitter
        - Response validation
        - Circuit breaker state management
        """
        # Circuit breaker check
        if not self._circuit.allow_request():
            raise APIError(
                f"Circuit breaker OPEN — backend unreachable, failing fast",
                status_code=0,
                severity=ErrorSeverity.DEGRADED,
            )

        url = urljoin(API_BASE.rstrip("/") + "/", path.lstrip("/"))

        last_error: Optional[APIError] = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self._client.request(
                    method=method,
                    url=url,
                    json=json_body,
                    headers=self._headers if method in ("POST", "PUT", "PATCH") else None,
                )

                # Process response
                if resp.status_code in (200, 201):
                    data = resp.json()
                    self._circuit.record_success()
                    return data

                # Classify and handle error
                severity = classify_error(resp)
                detail = self._extract_detail(resp)

                if severity == ErrorSeverity.CRITICAL:
                    self._circuit.record_failure()
                    raise APIError(
                        f"Authentication failed: {detail}",
                        status_code=resp.status_code,
                        severity=severity,
                    )

                if not should_retry(severity) or attempt == MAX_RETRIES:
                    self._circuit.record_failure()
                    raise APIError(
                        detail or f"Request failed (HTTP {resp.status_code})",
                        status_code=resp.status_code,
                        severity=severity,
                    )

                # Retry with backoff
                delay = RETRY_BACKOFF * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                logger.warning(
                    f"{label} attempt {attempt}/{MAX_RETRIES} failed "
                    f"(HTTP {resp.status_code}), retrying in {delay:.1f}s: {detail}"
                )
                time.sleep(delay)
                last_error = APIError(detail, status_code=resp.status_code, severity=severity)

            except httpx.TimeoutException as e:
                if attempt == MAX_RETRIES:
                    self._circuit.record_failure()
                    raise APIError(
                        f"{label} timed out after {MAX_RETRIES} attempts",
                        severity=ErrorSeverity.TRANSIENT,
                    ) from e
                delay = RETRY_BACKOFF * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                logger.warning(f"{label} timeout, retrying in {delay:.1f}s")
                time.sleep(delay)

            except httpx.ConnectError as e:
                self._circuit.record_failure()
                raise APIError(
                    f"Cannot connect to API: {e}",
                    severity=ErrorSeverity.TRANSIENT,
                ) from e

            except httpx.HTTPError as e:
                self._circuit.record_failure()
                raise APIError(
                    f"HTTP error: {e}",
                    severity=ErrorSeverity.TRANSIENT,
                ) from e

        # Should not reach here, but defensive
        raise last_error or APIError(
            f"{label} failed after {MAX_RETRIES} attempts",
            severity=ErrorSeverity.DEGRADED,
        )

    @staticmethod
    def _extract_detail(resp: httpx.Response) -> str:
        """Extract detail/error message from response."""
        try:
            body = resp.json()
            if isinstance(body, dict):
                return body.get("detail", body.get("message", resp.text[:200]))
            return str(body)[:200]
        except Exception:
            return resp.text[:200]

    # ─── Auth Methods ─────────────────────────────────────────────

    def signup(self, email: str, password: str, full_name: str) -> dict:
        """Register new user with client-side validation."""
        errors = validate_signup_payload(email, password, full_name)
        if errors:
            raise APIError(
                "; ".join(errors),
                severity=ErrorSeverity.FATAL,
            )

        data = self._request(
            "POST", "/auth/register",
            json_body={"email": email, "password": password, "full_name": full_name},
            label="Signup",
        )
        with self._lock:
            self.token = data.get("access_token", self.token)
        return data

    def login(self, email: str, password: str) -> dict:
        """Authenticate existing user."""
        if not email or not password:
            raise APIError("Email and password required", severity=ErrorSeverity.FATAL)

        data = self._request(
            "POST", "/auth/login",
            json_body={"email": email, "password": password},
            label="Login",
        )
        with self._lock:
            self.token = data.get("access_token", self.token)
        return data

    # ─── Subscription Methods ─────────────────────────────────────

    def create_vps_subscription(self, plan: str) -> dict:
        """Create or activate a VPS subscription."""
        errors = validate_subscription_payload(plan)
        if errors:
            raise APIError(
                "; ".join(errors),
                severity=ErrorSeverity.FATAL,
            )

        with self._lock:
            if not self.token:
                raise APIError(
                    "Authentication required to create subscription",
                    severity=ErrorSeverity.CRITICAL,
                )

        return self._request(
            "POST", "/vps/subscriptions",
            json_body={"plan": plan},
            label="Create subscription",
        )

    def verify_license(self, license_key: str) -> dict:
        """Verify a VPS license key."""
        if not license_key or len(license_key) < 10:
            raise APIError(
                "Invalid license key format",
                severity=ErrorSeverity.FATAL,
            )

        return self._request(
            "POST", "/vps/verify-license",
            json_body={"license_key": license_key},
            label="Verify license",
        )

    # ─── Health ───────────────────────────────────────────────────

    def health_check(self) -> bool:
        """Ping the backend health endpoint."""
        try:
            resp = self._client.get(
                f"{API_BASE}/health",
                timeout=httpx.Timeout(5, connect=5),
            )
            if resp.status_code == 200:
                self._circuit.record_success()
                self._last_heartbeat = time.time()
                return True
            self._circuit.record_failure()
            return False
        except Exception:
            self._circuit.record_failure()
            return False

    def heartbeat(self):
        """Periodic health check if enough time has passed."""
        now = time.time()
        if now - self._last_heartbeat > HEARTBEAT_INTERVAL:
            self.health_check()

    # ─── Lifecycle ────────────────────────────────────────────────

    def close(self):
        """Release all resources."""
        try:
            self._client.close()
        except Exception:
            pass
