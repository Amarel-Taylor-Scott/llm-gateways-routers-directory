"""SQLite telemetry sink for route decisions."""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import asdict
from pathlib import Path

from chronorouter.types import RouteResult, TaskProfile


class SQLiteTelemetry:
    def __init__(self, path: str | Path = "telemetry.db") -> None:
        self.path = Path(path)
        self._init()

    def _init(self) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS route_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at REAL NOT NULL,
                    task_profile TEXT NOT NULL,
                    route_result TEXT NOT NULL
                )
                """
            )

    def log(self, profile: TaskProfile, result: RouteResult) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT INTO route_events (created_at, task_profile, route_result) VALUES (?, ?, ?)",
                (time.time(), json.dumps(asdict(profile), default=str), json.dumps(asdict(result), default=str)),
            )
