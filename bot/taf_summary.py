from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone

from dateutil import tz

logger = logging.getLogger(__name__)


_WEATHER_CODES = {
    "RA": "дождь",
    "-RA": "слабый дождь",
    "+RA": "сильный дождь",
    "SHRA": "кратковременный дождь",
    "-SHRA": "кратковременный слабый дождь",
    "TS": "гроза",
    "FG": "туман",
    "SN": "снег",
    "SHSN": "кратковременный снегопад",
}

_CLOUD_CODES = {
    "FEW": "небольшая облачность",
    "SCT": "рассеянная облачность",
    "BKN": "облачность 5-7 октантов",
    "OVC": "сплошная облачность",
    "CB": "кучево-дождевые облака",
}

_WIND_RE = re.compile(r"(?P<dir>\d{3}|VRB)(?P<spd>\d{2})(G(?P<gst>\d{2}))?KT")
_TIME_RANGE_RE = re.compile(r"(\d{4})/(\d{4})")


def _decode_wind(token: str) -> str | None:
    m = _WIND_RE.match(token)
    if not m:
        return None
    direction = m.group("dir")
    speed = int(m.group("spd"))
    gust = m.group("gst")
    gust_part = f", порывы {int(gust)} узл" if gust else ""
    if direction == "VRB":
        return f"переменный ветер {speed} узл{gust_part}"
    return f"ветер {direction}° {speed} узл{gust_part}"


def _decode_weather(tokens: list[str]) -> list[str]:
    out = []
    for t in tokens:
        if t in _WEATHER_CODES:
            out.append(_WEATHER_CODES[t])
    return out


def _decode_cloud(tokens: list[str]) -> list[str]:
    out = []
    for t in tokens:
        for code, desc in _CLOUD_CODES.items():
            if t.startswith(code):
                height = t[len(code):]
                if height.isdigit():
                    meters = int(height) * 30.48  # 100 ft increments
                    out.append(f"{desc} {int(meters)} м")
                else:
                    out.append(desc)
    return out


def _range_to_local(start_token: str, end_token: str, issue_dt: datetime, tz_str: str) -> tuple[str, str]:
    """Convert DDHH/DDHH tokens to local HH:MM."""
    start_day = int(start_token[:2])
    start_hour = int(start_token[2:4])
    end_day = int(end_token[:2])
    end_hour = int(end_token[2:4])

    year = issue_dt.year
    month = issue_dt.month

    def _to_dt(day: int, hour: int):
        dt = datetime(year, month, day, hour, tzinfo=timezone.utc)
        if dt < issue_dt:
            # crossed month forward
            dt += timedelta(days=31)
        return dt

    local_tz = tz.gettz(tz_str)
    start_dt_local = _to_dt(start_day, start_hour).astimezone(local_tz)
    end_dt_local = _to_dt(end_day, end_hour).astimezone(local_tz)

    return start_dt_local.strftime("%H:%M"), end_dt_local.strftime("%H:%M")


def summarize_taf(taf_raw: str, issue_dt: datetime, tz_str: str) -> str:
    """Return human-readable summary of key TAF changes."""

    lines = [l.strip() for l in taf_raw.splitlines() if l.strip()]
    summaries: list[str] = []

    # First line may start with DDHH/DDHH or wind etc.
    for line in lines:
        tokens = line.split()
        if not tokens:
            continue
        first = tokens[0]
        if first in {"FM", "BECMG", "TEMPO"} or first.startswith("PROB"):
            # complex forms like FMHHMM not handled yet. We'll handle BECMG/TEMPO/PROBxx + range.
            if first == "BECMG":
                # BECMG DDHH/DDHH ...
                if len(tokens) >= 2 and _TIME_RANGE_RE.match(tokens[1]):
                    start_token, end_token = _TIME_RANGE_RE.match(tokens[1]).groups()
                    start_local, end_local = _range_to_local(start_token, end_token, issue_dt, tz_str)
                    conditions_tokens = tokens[2:]
                    wind_desc = None
                    for t in conditions_tokens:
                        w = _decode_wind(t)
                        if w:
                            wind_desc = w
                            break
                    pieces = []
                    if wind_desc:
                        pieces.append(wind_desc)
                    pieces.extend(_decode_weather(conditions_tokens))
                    pieces.extend(_decode_cloud(conditions_tokens))
                    cond_text = ", ".join(pieces) if pieces else "изменение погоды"
                    summaries.append(f"С {start_local} до {end_local} ожидается {cond_text}.")
            elif first == "TEMPO":
                if len(tokens) >= 2 and _TIME_RANGE_RE.match(tokens[1]):
                    start_token, end_token = _TIME_RANGE_RE.match(tokens[1]).groups()
                    start_local, end_local = _range_to_local(start_token, end_token, issue_dt, tz_str)
                    conditions_tokens = tokens[2:]
                    pieces = []
                    pieces.extend(_decode_weather(conditions_tokens))
                    wind_desc = None
                    for t in conditions_tokens:
                        w = _decode_wind(t)
                        if w:
                            wind_desc = w
                            break
                    if wind_desc:
                        pieces.append(wind_desc)
                    pieces.extend(_decode_cloud(conditions_tokens))
                    cond_text = ", ".join(pieces) if pieces else "временное изменение погоды"
                    summaries.append(f"Временами ({start_local}-{end_local}) {cond_text}.")
            elif first.startswith("PROB"):
                prob = first[4:]  # 30 or 40
                idx = 1
                range_token = None
                if len(tokens) > 1 and _TIME_RANGE_RE.match(tokens[1]):
                    range_token = tokens[1]
                    idx = 2
                if range_token:
                    start_token, end_token = _TIME_RANGE_RE.match(range_token).groups()
                    start_local, end_local = _range_to_local(start_token, end_token, issue_dt, tz_str)
                    conditions_tokens = tokens[idx:]
                else:
                    start_local = end_local = ""
                    conditions_tokens = tokens[idx:]
                pieces = _decode_weather(conditions_tokens)
                pieces.extend(_decode_cloud(conditions_tokens))
                cond_text = ", ".join(pieces) if pieces else "изменение погоды"
                time_part = f" ({start_local}-{end_local})" if start_local else ""
                summaries.append(f"Вероятность {prob}%{time_part} {cond_text}.")
        else:
            # Base forecast line (after issuance), often wind + CAVOK
            pieces = []
            wind_desc = _decode_wind(first)
            if wind_desc:
                pieces.append(wind_desc)
                remainder = tokens[1:]
            else:
                remainder = tokens
            pieces.extend(_decode_weather(remainder))
            pieces.extend(_decode_cloud(remainder))
            if "CAVOK" in remainder:
                pieces.append("CAVOK (видимость >10 км, нет значимой облачности)")
            if pieces:
                summaries.append("Основной прогноз: " + ", ".join(pieces) + ".")

    return "\n".join(summaries) if summaries else taf_raw
