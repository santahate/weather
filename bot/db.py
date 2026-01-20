from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Tuple

from .parser import WeatherData

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "weather.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    icao TEXT NOT NULL,
    metar_text TEXT NOT NULL,
    metar_time DATETIME NOT NULL,
    taf_text TEXT NOT NULL,
    taf_issue_time DATETIME NOT NULL,
    pressure_hpa INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (icao, metar_time, taf_issue_time)
);
"""


@contextmanager
def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute(SCHEMA)
    logger.debug("Database initialised at %s", DB_PATH)


def _normalize_text(text: str) -> str:
    return " ".join(text.split())


def already_exists(data: WeatherData) -> bool:
    metar_norm = _normalize_text(data.metar_raw)
    taf_norm = _normalize_text(data.taf_raw)
    with _get_conn() as conn:
        cur = conn.execute(
            "SELECT 1 FROM weather WHERE icao=? AND metar_time=? AND taf_issue_time=? LIMIT 1",
            (
                data.icao,
                data.metar_time.isoformat(timespec="seconds"),
                data.taf_issue_time.isoformat(timespec="seconds"),
            ),
        )
        if cur.fetchone() is not None:
            return True

        cur = conn.execute(
            "SELECT metar_text, taf_text FROM weather WHERE icao=? ORDER BY id DESC LIMIT 1",
            (data.icao,),
        )
        row: Tuple[str, str] | None = cur.fetchone()
        if row is None:
            return False

        return _normalize_text(row[0]) == metar_norm and _normalize_text(row[1]) == taf_norm


def insert_weather(data: WeatherData) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO weather (
                icao, metar_text, metar_time, taf_text, taf_issue_time, pressure_hpa
            ) VALUES (?, ?, ?, ?, ?, ?)""",
            (
                data.icao,
                data.metar_raw,
                data.metar_time.isoformat(timespec="seconds"),
                data.taf_raw,
                data.taf_issue_time.isoformat(timespec="seconds"),
                data.pressure_hpa,
            ),
        )
    logger.debug("Inserted new weather row for %s", data.icao)


def cleanup(days: int = 2) -> None:
    threshold = datetime.now(timezone.utc) - timedelta(days=days)
    with _get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM weather WHERE created_at < ?",
            (threshold.isoformat(timespec="seconds"),),
        )
    logger.debug("Deleted %d old rows", cur.rowcount if cur else 0)


def fetch_pressure_last_hours(hours: int = 12, icao: str | None = None):
    from datetime import timedelta

    start = datetime.now(timezone.utc) - timedelta(hours=hours)
    with _get_conn() as conn:
        cur = conn.execute(
            """
            SELECT metar_time, pressure_hpa FROM weather
            WHERE metar_time >= ? {icao_clause}
            ORDER BY metar_time ASC
            """.format(icao_clause="AND icao=?" if icao else ""),
            (start.isoformat(timespec="seconds"), icao) if icao else (start.isoformat(timespec="seconds"),),
        )
        return cur.fetchall()
