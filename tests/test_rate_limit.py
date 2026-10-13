from app.core.rate_limit import RateLimiter


def test_blocks_after_limit():
    rl = RateLimiter(max_hits=3, window_seconds=60)
    assert all(rl.allow("1.1.1.1", now=t) for t in (0, 1, 2))
    assert not rl.allow("1.1.1.1", now=3)


def test_window_expires():
    rl = RateLimiter(max_hits=1, window_seconds=60)
    assert rl.allow("ip", now=0)
    assert not rl.allow("ip", now=59)
    assert rl.allow("ip", now=60)


def test_keys_are_independent():
    rl = RateLimiter(max_hits=1, window_seconds=60)
    assert rl.allow("a", now=0)
    assert rl.allow("b", now=0)
    assert not rl.allow("a", now=1)
