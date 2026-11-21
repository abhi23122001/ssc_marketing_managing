# -*- coding: utf-8 -*-
"""Central Autonomous Background Scheduler for SHAH Group AI OS.

Runs as a persistent background daemon thread alongside the server.
Executes scheduled intelligence jobs (Daily Research, Marketing Briefs,
Proactive Alert Scans, Operations & P&L Reports) without requiring user prompts
or an open browser.
"""
from __future__ import annotations

import logging
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from foundation.store import Store
from foundation.domains import ai_intelligence

logger = logging.getLogger("shah_ai.scheduler")

# Local timezone helper (Asia/Kolkata, UTC+5:30)
KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))

_SCHEDULER_THREAD: Optional[threading.Thread] = None
_STOP_EVENT = threading.Event()


def now_kolkata() -> datetime:
    return datetime.now(KOLKATA_TZ)


def now_iso() -> str:
    return now_kolkata().strftime("%Y-%m-%dT%H:%M:%S%z")


def compute_next_run(frequency: str, schedule_time: str) -> str:
    """Computes next ISO execution timestamp in Asia/Kolkata timezone."""
    now = now_kolkata()
    freq = (frequency or "daily").lower()

    if freq == "hourly" or schedule_time == "every_hour":
        next_dt = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        return next_dt.strftime("%Y-%m-%dT%H:%M:%S%z")

    if freq == "daily":
        try:
            parts = schedule_time.strip().split(":")
            h, m = int(parts[0]), int(parts[1])
        except Exception:
            h, m = 6, 0
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target.strftime("%Y-%m-%dT%H:%M:%S%z")

    if freq == "weekly":
        # Next week
        target = now + timedelta(days=7)
        return target.strftime("%Y-%m-%dT%H:%M:%S%z")

    if freq == "monthly":
        # Next month (approx 30 days)
        target = now + timedelta(days=30)
        return target.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Default fallback: 24 hours
    return (now + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S%z")


def check_and_run_due_jobs(store: Store) -> int:
    """Checks for due jobs in ai_scheduler_jobs and executes them."""
    ai_intelligence.ensure_ai_intelligence_schema(store.conn)
    current_time_iso = now_iso()

    jobs = store.fetchall(
        "SELECT * FROM ai_scheduler_jobs WHERE is_enabled=1"
    )
    executed_count = 0

    for job in jobs:
        next_run = job.get("next_run_at")
        is_due = False
        if not next_run:
            is_due = True
        elif next_run <= current_time_iso:
            is_due = True

        if is_due:
            job_key = job["job_key"]
            try:
                res = ai_intelligence.run_scheduler_job(store, job_key)
                next_time = compute_next_run(job.get("frequency", "daily"), job.get("schedule_time", "06:00"))
                store.conn.execute(
                    "UPDATE ai_scheduler_jobs SET next_run_at=? WHERE job_key=?",
                    (next_time, job_key)
                )
                store.conn.commit()
                executed_count += 1
            except Exception as e:
                logger.error(f"Error running scheduler job {job_key}: {e}")

    return executed_count


def _scheduler_loop(store: Store, poll_interval_sec: int = 30) -> None:
    """Main daemon loop running every poll_interval_sec."""
    logger.info("SHAH Group AI OS Background Scheduler loop started.")
    # On first boot, run proactive alert scan and check due jobs
    try:
        check_and_run_due_jobs(store)
    except Exception as e:
        logger.error(f"Initial scheduler cycle error: {e}")

    while not _STOP_EVENT.is_set():
        try:
            check_and_run_due_jobs(store)
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
        # Sleep in small slices to respond promptly to stop event
        for _ in range(poll_interval_sec * 2):
            if _STOP_EVENT.is_set():
                break
            time.sleep(0.5)


def start_scheduler(store: Store, poll_interval_sec: int = 30) -> threading.Thread:
    """Starts the persistent background scheduler thread if not already running."""
    global _SCHEDULER_THREAD, _STOP_EVENT
    if _SCHEDULER_THREAD is not None and _SCHEDULER_THREAD.is_alive():
        return _SCHEDULER_THREAD

    _STOP_EVENT.clear()
    _SCHEDULER_THREAD = threading.Thread(
        target=_scheduler_loop,
        args=(store, poll_interval_sec),
        name="ShahGroupAIScheduler",
        daemon=True
    )
    _SCHEDULER_THREAD.start()
    return _SCHEDULER_THREAD


def stop_scheduler() -> None:
    """Signals the scheduler daemon to shut down cleanly."""
    global _STOP_EVENT, _SCHEDULER_THREAD
    _STOP_EVENT.set()
    if _SCHEDULER_THREAD is not None:
        _SCHEDULER_THREAD.join(timeout=3.0)
        _SCHEDULER_THREAD = None
