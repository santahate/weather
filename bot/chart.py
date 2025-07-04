import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

import requests

logger = logging.getLogger(__name__)


OUTPUT_FILE = Path("pressure_last12h.png")


def _build_chart_config(times: list[str], pressures: list[int]) -> dict:
    return {
        "type": "line",
        "data": {
            "labels": times,
            "datasets": [
                {
                    "label": "Pressure (hPa)",
                    "data": pressures,
                    "fill": False,
                    "borderColor": "#3e95cd",
                    "tension": 0.1,
                }
            ],
        },
        "options": {
            "plugins": {"legend": {"display": False}},
            "scales": {
                "x": {"title": {"display": True, "text": "Time"}},
                "y": {"title": {"display": True, "text": "hPa"}},
            },
        },
    }


def generate_pressure_chart(rows: Iterable[Tuple[str, int | None]]) -> Path:
    """Generate pressure chart PNG via QuickChart.io service and save locally."""

    times_fmt: list[str] = []
    pressures: list[int] = []

    for iso_time, pressure in rows:
        if pressure is None:
            continue
        try:
            dt = datetime.fromisoformat(iso_time)
            times_fmt.append(dt.strftime("%H:%M"))
            pressures.append(pressure)
        except Exception:
            logger.warning("Invalid datetime row: %s", iso_time)

    if not pressures:
        raise ValueError("No pressure data to plot")

    chart_config = _build_chart_config(times_fmt, pressures)
    url = "https://quickchart.io/chart"
    payload = {"c": json.dumps(chart_config)}
    logger.debug("Requesting QuickChart with payload length %d", len(payload["c"]))
    resp = requests.get(url, params=payload, timeout=10)
    resp.raise_for_status()

    OUTPUT_FILE.write_bytes(resp.content)
    logger.debug("Pressure chart saved to %s", OUTPUT_FILE)
    return OUTPUT_FILE
