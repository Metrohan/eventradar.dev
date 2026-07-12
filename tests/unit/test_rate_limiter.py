from app.services.rate_limiter import FixedWindowRateLimiter


def test_rate_limiter_blocks_until_window_expires():
    now = [100.0]
    limiter = FixedWindowRateLimiter(2, 10, clock=lambda: now[0])

    assert limiter.check("client") is None
    assert limiter.check("client") is None
    assert limiter.check("client") == 10

    now[0] = 111
    assert limiter.check("client") is None


def test_rate_limiter_isolates_clients():
    limiter = FixedWindowRateLimiter(1, 60, clock=lambda: 100.0)

    assert limiter.check("first") is None
    assert limiter.check("first") == 60
    assert limiter.check("second") is None
