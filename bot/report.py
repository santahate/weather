from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import List

from dateutil import tz

from .parser import WeatherData

logger = logging.getLogger(__name__)

_TEMPLATE_PATH = Path(__file__).with_suffix("").parent / "templates" / "report_template.txt"


ALERT_RULES = [
    (lambda d: (d.temperature_c or 0) > 30, "🔥 Сильная жара"),
    (lambda d: any(code.startswith("RA") for code in d.phenomena or []), "☔ Дождь"),
    (lambda d: any("TS" in code for code in d.phenomena or []), "⛈️ Гроза"),
    (lambda d: any(code in {"GR", "GS"} for code in d.phenomena or []), "🌨️ Град"),
    (lambda d: (d.wind_gust_kt or 0) >= 30 or (d.wind_speed_kt or 0) >= 30, "💨 Сильный ветер"),
    (lambda d: "FG" in (d.phenomena or []) or (d.visibility_m or 9999) < 1000, "🌫️ Туман"),
]


def _load_template() -> str:
    txt = _TEMPLATE_PATH.read_text(encoding="utf-8")
    # Convert Jinja-style {{var}} to Python format {var}
    return txt.replace("{{", "{").replace("}}", "}")


def _local_time(dt: datetime, timezone_str: str) -> str:
    target_tz = tz.gettz(timezone_str)
    return dt.astimezone(target_tz).strftime("%H:%M")


def _wind_gust_suffix(gust_kt: int | None) -> str:
    return f", порывы {gust_kt} узл" if gust_kt else ""


def build_alerts(data: WeatherData) -> str:
    alerts: List[str] = [msg for rule, msg in ALERT_RULES if rule(data)]
    return " • ".join(alerts)


def generate_report(data: WeatherData, timezone_str: str, taf_text: str) -> str:
    template = _load_template()

    report = template.format(
        icao=data.icao,
        time_local=_local_time(data.metar_time, timezone_str),
        timezone_region=timezone_str,
        temperature_c=f"{data.temperature_c:+.0f}" if data.temperature_c is not None else "N/A",
        dewpoint_c=f"{data.dewpoint_c:+.0f}" if data.dewpoint_c is not None else "N/A",
        wind_dir_deg=data.wind_dir_deg if data.wind_dir_deg is not None else "VRB",
        wind_speed_kt=data.wind_speed_kt if data.wind_speed_kt is not None else 0,
        wind_gust=_wind_gust_suffix(data.wind_gust_kt),
        cloud=data.cloud or "CAVOK",
        pressure_hpa=data.pressure_hpa or "N/A",
        taf_summary=taf_text,
        taf_text=taf_text,
        alerts=build_alerts(data),
    )
    logger.debug("Generated report: %s", report)
    return report
