"""Простое ограничение частоты запросов в памяти процесса (скользящее окно).

Подходит для одного процесса uvicorn. При нескольких процессах/серверах нужен общий
счётчик (например, Redis).
"""
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, max_hits: int, window_seconds: float) -> None:
        self.max_hits = max_hits
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        q = self._hits[key]
        while q and now - q[0] >= self.window:
            q.popleft()
        if len(q) >= self.max_hits:
            return False
        q.append(now)
        # Не даём словарю расти бесконечно от разовых IP.
        if len(self._hits) > 10_000:
            self._cleanup(now)
        return True

    def _cleanup(self, now: float) -> None:
        for key in [k for k, q in self._hits.items() if not q or now - q[-1] >= self.window]:
            del self._hits[key]


# 10 попыток входа в минуту с одного IP.
login_limiter = RateLimiter(max_hits=10, window_seconds=60)
