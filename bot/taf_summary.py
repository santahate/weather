from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone

from dateutil import tz
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

_WEATHER_CODES = {
    # Rain
    "-RA": "слабый дождь 🌧",
    "RA": "дождь 🌧🌧",
    "+RA": "сильный дождь 🌧🌧🌧",
    # Shower rain
    "-SHRA": "слабый ливневой дождь 🌦",
    "SHRA": "ливневой дождь 🌦🌦",
    "+SHRA": "сильный ливневой дождь 🌦🌦🌦",
    # Thunderstorm
    "TS": "гроза ⚡️",
    "-TSRA": "слабая гроза с дождём ⛈️",
    "TSRA": "гроза с дождём ⛈️",
    "+TSRA": "сильная гроза с дождём ⛈️",
    # Other phenomena
    "FG": "туман 😶‍🌫️",
    "SN": "снег ❄️",
    "SHSN": "ливневой снег ❄️❄️❄️",
}

_CLOUD_CODES = {
    "CLR": "безоблачно ○",
    "SKC": "безоблачно ○",
    "FEW": "небольшая облачность ◔",
    "SCT": "рассеянная облачность ◑",
    "BKN": "облачность 5-7 октантов ◕",
    "OVC": "сплошная облачность ●",
}

_WIND_RE = re.compile(r"(?P<dir>\d{3}|VRB)(?P<spd>\d{2})(G(?P<gst>\d{2}))?KT")
_TIME_RANGE_RE = re.compile(r"(\d{4})/(\d{4})")


def _kt_to_kmh(kn: str) -> int:
    return int(round(int(kn) * 1.852))


def _decode_wind(token: str) -> str | None:
    m = _WIND_RE.match(token)
    if not m:
        return None
    direction = m.group("dir")
    speed_kmh = _kt_to_kmh(m.group("spd"))
    gust = m.group("gst")
    gust_part = f", порывы {_kt_to_kmh(gust)} км/ч" if gust else ""
    if direction == "VRB":
        return f"переменный ветер {speed_kmh} км/ч{gust_part}"
    return f"ветер {direction}° {speed_kmh} км/ч{gust_part}"


def _decode_weather(tokens: list[str]) -> list[str]:
    out = []
    for t in tokens:
        if t in _WEATHER_CODES:
            out.append(_WEATHER_CODES[t])
    return out


def _decode_cloud(tokens: list[str]) -> list[str]:
    out = []
    for t in tokens:
        # detect cumulonimbus tag
        has_cb = t.endswith("CB")
        base = t[:-2] if has_cb else t
        for code, desc in _CLOUD_CODES.items():
            if base.startswith(code):
                height = base[len(code):]
                if height.isdigit():
                    meters = int(height) * 30.48
                    out.append(f"{desc} {int(meters)} м")
                else:
                    out.append(desc)
                if has_cb:
                    out.append("кучево-дождевые облака")
    return out


def _range_to_local(start_token: str, end_token: str, issue_dt: datetime, tz_str: str):
    """Convert DDHH/DDHH tokens to local datetime objects and string representation."""
    start_day = int(start_token[:2])
    start_hour = int(start_token[2:4])
    end_day = int(end_token[:2])
    end_hour = int(end_token[2:4])

    year = issue_dt.year
    month = issue_dt.month

    def _to_dt(day: int, hour: int):
        if hour == 24:
            # TAF uses 24 for midnight, meaning 0000 of the next day.
            # Create date for day at 00:00 and add 1 day to handle month/year roll.
            dt = datetime(year, month, day, 0, tzinfo=timezone.utc) + timedelta(days=1)
        else:
            dt = datetime(year, month, day, hour, tzinfo=timezone.utc)

        # If constructed date is before issue date, it must be for next month
        if dt < issue_dt:
            dt += relativedelta(months=1)
        return dt

    local_tz = tz.gettz(tz_str)
    start_dt_local = _to_dt(start_day, start_hour).astimezone(local_tz)
    end_dt_local = _to_dt(end_day, end_hour).astimezone(local_tz)

    return start_dt_local, end_dt_local


def summarize_taf(taf_raw: str, issue_dt: datetime, tz_str: str) -> str:
    """Return human-readable summary of key TAF changes."""

    lines = [l.strip() for l in taf_raw.splitlines() if l.strip()]
    summaries: list[str] = []
    prob_prefix: str | None = None
    now_local = datetime.now(tz.gettz(tz_str))

    # First line may start with DDHH/DDHH or wind etc.
    for line in lines:
        tokens = line.split()
        if not tokens:
            continue
        first = tokens[0]
        if first in {"FM", "BECMG", "TEMPO"} or first.startswith("PROB") or prob_prefix:
            # complex forms like FMHHMM not handled yet. We'll handle BECMG/TEMPO/PROBxx + range.
            if first.startswith("PROB") and not prob_prefix:
                prob = first[4:]
                idx = 1
                time_range_text = ""
                if len(tokens) > idx and _TIME_RANGE_RE.match(tokens[idx]):
                    start_token, end_token = _TIME_RANGE_RE.match(tokens[idx]).groups()
                    start_local_dt, end_local_dt = _range_to_local(start_token, end_token, issue_dt, tz_str)
                    if end_local_dt <= now_local:
                        continue  # interval already past
                    start_local = start_local_dt.strftime('%H:%M'); end_local = end_local_dt.strftime('%H:%M')
                    time_range_text = f"({start_local}-{end_local}) "
                    idx += 1

                # If there are tokens after the (optional) time-range, treat them as conditions of this PROB group.
                if len(tokens) > idx:
                    conditions_tokens = tokens[idx:]
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
                    cond_text = ", ".join(pieces) if pieces else "изменение погоды"
                    summaries.append(f"Вероятность {prob}% {time_range_text}{cond_text}.")
                    prob_prefix = None
                else:
                    # No condition tokens yet – keep prefix for the following line.
                    prob_prefix = f"Вероятность {prob}% {time_range_text}"
                continue

            if first == "BECMG":
                # BECMG DDHH/DDHH ...
                if len(tokens) >= 2 and _TIME_RANGE_RE.match(tokens[1]):
                    start_token, end_token = _TIME_RANGE_RE.match(tokens[1]).groups()
                    start_local_dt, end_local_dt = _range_to_local(start_token, end_token, issue_dt, tz_str)
                    if end_local_dt <= now_local:
                        continue
                    start_local = start_local_dt.strftime('%H:%M'); end_local = end_local_dt.strftime('%H:%M')
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
                    summaries.append(f"В интервале {start_local}-{end_local} ожидается изменение к: {cond_text}.")
            elif first == "TEMPO":
                if len(tokens) >= 2 and _TIME_RANGE_RE.match(tokens[1]):
                    start_token, end_token = _TIME_RANGE_RE.match(tokens[1]).groups()
                    start_local_dt, end_local_dt = _range_to_local(start_token, end_token, issue_dt, tz_str)
                    if end_local_dt <= now_local:
                        continue
                    start_local = start_local_dt.strftime('%H:%M'); end_local = end_local_dt.strftime('%H:%M')
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
                    prefix = prob_prefix or "Временами "
                    summaries.append(f"{prefix}({start_local}-{end_local}) {cond_text}.")
                    prob_prefix = None
            elif first.startswith("PROB"):
                # Standalone PROB lines handled earlier by setting prob_prefix
                pass
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
                base_text = ", ".join(pieces)
                if prob_prefix:
                    summaries.append(prob_prefix + base_text + ".")
                    prob_prefix = None
                else:
                    summaries.append("Основной прогноз: " + base_text + ".")

    return "\n".join(summaries) if summaries else taf_raw
