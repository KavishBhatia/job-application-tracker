import asyncio

from src.lifecycle import HeartbeatMonitor, auto_shutdown_enabled


def test_is_expired_false_without_heartbeat():
    monitor = HeartbeatMonitor(timeout_seconds=10)
    assert monitor.is_expired(now=1000) is False


def test_is_expired_false_within_timeout():
    monitor = HeartbeatMonitor(timeout_seconds=10)
    monitor.record(now=100)
    assert monitor.is_expired(now=105) is False


def test_is_expired_true_after_timeout():
    monitor = HeartbeatMonitor(timeout_seconds=10)
    monitor.record(now=100)
    assert monitor.is_expired(now=111) is True


def test_check_and_maybe_shutdown_calls_callback_when_expired():
    calls = []
    monitor = HeartbeatMonitor(timeout_seconds=5, shutdown_callback=lambda: calls.append(True))
    monitor.record(now=0)
    result = monitor.check_and_maybe_shutdown(now=10)
    assert result is True
    assert calls == [True]


def test_check_and_maybe_shutdown_does_nothing_when_not_expired():
    calls = []
    monitor = HeartbeatMonitor(timeout_seconds=5, shutdown_callback=lambda: calls.append(True))
    monitor.record(now=0)
    result = monitor.check_and_maybe_shutdown(now=1)
    assert result is False
    assert calls == []


def test_run_triggers_shutdown_after_no_heartbeat_within_timeout():
    calls = []
    monitor = HeartbeatMonitor(timeout_seconds=0.05, shutdown_callback=lambda: calls.append(True))
    asyncio.run(monitor.run(check_interval_seconds=0.01))
    assert calls == [True]


def test_run_does_not_shutdown_while_heartbeats_keep_arriving():
    calls = []
    monitor = HeartbeatMonitor(timeout_seconds=0.05, shutdown_callback=lambda: calls.append(True))

    async def keep_alive_then_stop():
        task = asyncio.create_task(monitor.run(check_interval_seconds=0.01))
        for _ in range(5):
            await asyncio.sleep(0.02)
            monitor.record()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(keep_alive_then_stop())
    assert calls == []


def test_auto_shutdown_enabled_reads_env_flag(monkeypatch):
    monkeypatch.delenv("AUTO_SHUTDOWN_ON_CLOSE", raising=False)
    assert auto_shutdown_enabled() is False

    monkeypatch.setenv("AUTO_SHUTDOWN_ON_CLOSE", "true")
    assert auto_shutdown_enabled() is True

    monkeypatch.setenv("AUTO_SHUTDOWN_ON_CLOSE", "0")
    assert auto_shutdown_enabled() is False
