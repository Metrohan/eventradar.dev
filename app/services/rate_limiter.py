import ipaddress
from collections import OrderedDict, deque
from threading import Lock
from time import monotonic
from typing import Callable


def client_key(host: str) -> str:
    """Limiter key for a client address: IPv6 clients are grouped by their /64.

    A single IPv6 subscriber controls a whole /64, so keying on the full address
    would let one client mint unlimited keys (budget bypass and table filling).
    """
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return host
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
        return str(addr.ipv4_mapped)
    if isinstance(addr, ipaddress.IPv6Address):
        return str(ipaddress.IPv6Network((addr, 64), strict=False))
    return host


class FixedWindowRateLimiter:
    """Bounded, per-process limiter for low-volume endpoints.

    The name is historical: counting is a sliding window, not a fixed one.
    """

    def __init__(
        self,
        limit: int,
        window_seconds: float,
        clock: Callable[[], float] = monotonic,
        max_keys: int = 10000,
    ):
        if limit < 1 or window_seconds <= 0 or max_keys < 1:
            raise ValueError("Rate limiter bounds must be positive")
        self._limit = limit
        self._window_seconds = window_seconds
        self._clock = clock
        self._max_keys = max_keys
        self._requests: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = Lock()

    def check(self, key: str) -> float | None:
        with self._lock:
            now = self._clock()
            cutoff = now - self._window_seconds
            # Keys are ordered by their last accepted request. Never evict an
            # active budget: capacity exhaustion fails closed for new clients.
            while self._requests:
                oldest = next(iter(self._requests.values()))
                if oldest[-1] > cutoff:
                    break
                self._requests.popitem(last=False)
            if key not in self._requests:
                if len(self._requests) >= self._max_keys:
                    oldest = next(iter(self._requests.values()))
                    return max(0.0, oldest[-1] + self._window_seconds - now)
                self._requests[key] = deque()
            requests = self._requests[key]
            while requests and requests[0] <= cutoff:
                requests.popleft()
            if len(requests) >= self._limit:
                return max(0.0, self._window_seconds - (now - requests[0]))
            requests.append(now)
            self._requests.move_to_end(key)
            return None

    def reset(self) -> None:
        with self._lock:
            self._requests.clear()
