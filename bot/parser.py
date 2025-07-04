from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from metar import Metar

import re

logger = logging.getLogger(__name__)


@dataclass
class WeatherData:
    icao: str
    metar_time: datetime
    taf_issue_time: datetime
    pressure_hpa: int | None
    metar_raw: str
    taf_raw: str

    # decoded attrs
    temperature_c: float | None = None
    dewpoint_c: float | None = None
    wind_dir_deg: int | None = None
    wind_speed_kt: int | None = None
    wind_gust_kt: int | None = None
    visibility_m: int | None = None
    cloud: str | None = None
    phenomena: list[str] | None = None


def _parse_metar(metar_raw: str) -> Metar.Metar:
    try:
        return Metar.Metar(metar_raw, strict=False)  # newer python-metar supports strict arg
    except TypeError:
        # fallback for older versions (<1.5) where 'strict' not supported
        return Metar.Metar(metar_raw)


_TAF_TIME_RE = re.compile(r"^(\d{6})Z")


def _extract_taf_issue_time(taf_raw: str) -> datetime:
    """Extract TAF issue time from raw string (first 6 digits indicate DDHHMMZ)."""
    match = _TAF_TIME_RE.search(taf_raw.strip())
    if not match:
        # fallback: use current UTC time
        return datetime.now(timezone.utc)
    time_token = match.group(1)
    day = int(time_token[:2])
    hour = int(time_token[2:4])
    minute = int(time_token[4:6])
    now = datetime.now(timezone.utc)
    # Handle month rollover if needed
    year = now.year
    month = now.month
    if day > now.day + 7:  # simplistic approach when day is ahead, means previous month
        # Go back one month
        if month == 1:
            month = 12
            year -= 1
        else:
            month -= 1
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


# ---------------- Sky decoding ------------------

_COVER_MAP = {
    "SKC": "ясно",
    "CLR": "ясно",
    "FEW": "небольшая облачность",
    "SCT": "рассеянная облачность",
    "BKN": "облачно",
    "OVC": "сплошная облачность",
}


def _decode_sky(sky_list) -> str | None:
    parts: list[str] = []
    for item in sky_list:
        try:
            cover = item[0]
            height_ft = item[1].value() if hasattr(item[1], "value") else item[1]
            cloud_type = item[2] if len(item) > 2 else None
        except Exception:
            parts.append(str(item))
            continue

        desc = _COVER_MAP.get(cover, cover)
        if height_ft:
            meters = int(round(float(height_ft) * 0.3048))
            desc = f"{desc} {meters} м"
        if cloud_type in {"CB", "TCU"}:
            desc += " (кучево-дождевые облака)" if cloud_type == "CB" else " (башенные кучевые облака)"
        parts.append(desc)

    return ", ".join(parts) if parts else None


def decode_metar_taf(icao: str, metar_raw: str, taf_raw: str) -> WeatherData:
    """Decode raw METAR/TAF strings into structured WeatherData object."""

    m = _parse_metar(metar_raw)

    # Fallback to UTC if tz not specified
    metar_time = m.time.replace(tzinfo=timezone.utc)
    taf_issue_time = _extract_taf_issue_time(taf_raw)

    pressure_hpa: int | None
    if hasattr(m, "pressure") and m.pressure:
        pressure_hpa = int(round(m.pressure.value()))
    elif hasattr(m, "altim") and m.altim:
        # altimeter given in inches Hg; convert to hPa (1 inHg = 33.8639 hPa)
        try:
            pressure_hpa = int(round(m.altim.value() * 33.8639))
        except Exception:  # noqa: BLE001
            pressure_hpa = None
    else:
        # Fallback regex search QNH/ALT in raw METAR
        match_q = re.search(r"\bQ(\d{4})\b", metar_raw)
        if match_q:
            pressure_hpa = int(match_q.group(1))
        else:
            match_a = re.search(r"\bA(\d{4})\b", metar_raw)
            if match_a:
                inhg = int(match_a.group(1)) / 100
                pressure_hpa = int(round(inhg * 33.8639))
            else:
                pressure_hpa = None

    wd = WeatherData(
        icao=icao,
        metar_time=metar_time,
        taf_issue_time=taf_issue_time,
        pressure_hpa=pressure_hpa,
        metar_raw=metar_raw,
        taf_raw=taf_raw,
        temperature_c=m.temp.value() if m.temp else None,
        dewpoint_c=m.dewpt.value() if m.dewpt else None,
        wind_dir_deg=int(m.wind_dir.value()) if m.wind_dir else None,
        wind_speed_kt=int(m.wind_speed.value()) if m.wind_speed else None,
        wind_gust_kt=int(m.wind_gust.value()) if m.wind_gust else None,
        visibility_m=m.vis.value() if m.vis else None,
        cloud=_decode_sky(m.sky) if m.sky else None,
        phenomena=[str(p) for p in m.weather] if m.weather else None,
    )
    logger.debug("Decoded METAR/TAF: %s", wd)
    return wd
