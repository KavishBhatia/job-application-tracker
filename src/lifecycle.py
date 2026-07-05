import asyncio
import os
import signal
import time
from typing import Optional


def auto_shutdown_enabled() -> bool:
    return os.getenv("AUTO_SHUTDOWN_ON_CLOSE", "").strip().lower() in ("1", "true", "yes")


def _kill_this_process() -> None:
    os.kill(os.getpid(), signal.SIGTERM)


class HeartbeatMonitor:
    def __init__(self, timeout_seconds: float, shutdown_callback=None):
        self.timeout_seconds = timeout_seconds
        self.shutdown_callback = shutdown_callback or _kill_this_process
        self.last_heartbeat: Optional[float] = None

    def record(self, now: Optional[float] = None) -> None:
        self.last_heartbeat = now if now is not None else time.monotonic()

    def is_expired(self, now: float) -> bool:
        if self.last_heartbeat is None:
            return False
        return (now - self.last_heartbeat) >= self.timeout_seconds

    def check_and_maybe_shutdown(self, now: float) -> bool:
        if self.is_expired(now):
            self.shutdown_callback()
            return True
        return False

    async def run(self, check_interval_seconds: float = 2.0) -> None:
        self.record()
        while True:
            await asyncio.sleep(check_interval_seconds)
            if self.check_and_maybe_shutdown(time.monotonic()):
                return


HEARTBEAT_TIMEOUT_SECONDS = 20.0

monitor = HeartbeatMonitor(timeout_seconds=HEARTBEAT_TIMEOUT_SECONDS)
