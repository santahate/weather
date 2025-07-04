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


def generate_chart(rows: Iterable[Tuple[str, int | None, float | None, int | None]]) -> Path:
    """Generate chart with pressure, temperature and humidity via QuickChart.io."""

    times_fmt: list[str] = []
    pressures: list[int] = []
    temps: list[float] = []
    humids: list[int] = []

    for iso_time, pressure, temp, humid in rows:
        try:
            dt = datetime.fromisoformat(iso_time)
            times_fmt.append(dt.strftime("%H:%M"))
            pressures.append(pressure if pressure is not None else None)
            temps.append(temp if temp is not None else None)
            humids.append(humid if humid is not None else None)
        except Exception:
            logger.warning("Invalid datetime row: %s", iso_time)

    if not any(pressures):
        raise ValueError("No pressure data to plot")

    if len(times_fmt) == 1:
        # Simple chart: pressure + temp on single axis
        chart_config = {
            "type": "line",
            "data": {
                "labels": times_fmt,
                "datasets": [
                    {
                        "label": "Pressure (hPa)",
                        "data": pressures,
                        "borderColor": "#3e95cd",
                        "fill": False,
                    },
                    {
                        "label": "Temp (C)",
                        "data": temps,
                        "borderColor": "#ff6384",
                        "fill": False,
                    },
                ],
            },
            "options": {
                "plugins": {"legend": {"display": True}},
            },
        }
    else:
        chart_config = {
            "type": "line",
            "data": {
                "labels": times_fmt,
                "datasets": [
                    {
                        "label": "Pressure (hPa)",
                        "data": pressures,
                        "borderColor": "#3e95cd",
                        "yAxisID": "y",
                        "fill": False,
                    },
                    {
                        "label": "Temp (C)",
                        "data": temps,
                        "borderColor": "#ff6384",
                        "yAxisID": "y1",
                        "fill": False,
                    },
                    {
                        "label": "RH (%)",
                        "data": humids,
                        "borderColor": "#4caf50",
                        "yAxisID": "y1",
                        "fill": False,
                    },
                ],
            },
            "options": {
                "scales": {
                    "y": {"title": {"display": True, "text": "hPa"}, "position": "left"},
                    "y1": {"position": "right", "grid": {"drawOnChartArea": False}},
                },
                "plugins": {"legend": {"display": True}},
            },
        }

    url = "https://quickchart.io/chart"
    payload = {"c": json.dumps(chart_config)}
    logger.debug("Requesting QuickChart with payload length %d", len(payload["c"]))
    resp = requests.get(url, params=payload, timeout=10)
    resp.raise_for_status()

    OUTPUT_FILE.write_bytes(resp.content)
    logger.debug("Chart saved to %s", OUTPUT_FILE)
    return OUTPUT_FILE
