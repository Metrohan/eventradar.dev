from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from typing import Callable


class FixedWindowRateLimiter:
    """Small in-process limiter for low-volume public form endpoints."""

    def __init__(
        self,
        limit: int,
        window_seconds: float,
        clock: Callable[[], float] = monotonic,
    ):
        self._limit = limit
        self._window_seconds = window_seconds
        self._clock = clock
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> float | None:
        now = self._clock()
        cutoff = now - self._window_seconds
        with self._lock:
            requests = self._requests[key]
            while requests and requests[0] <= cutoff:
                requests.popleft()
            if len(requests) >= self._limit:
                return max(0.0, self._window_seconds - (now - requests[0]))
            requests.append(now)
            return None

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()
