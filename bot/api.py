from __future__ import annotations

import logging
import re
from typing import Tuple

import requests

API_URL = "https://aviationweather.gov/api/data/metar"

# Fallback NOAA endpoints for raw text
NOAA_METAR_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao}.TXT"
NOAA_TAF_URL = "https://tgftp.nws.noaa.gov/data/forecasts/taf/stations/{icao}.TXT"

logger = logging.getLogger(__name__)

_TAF_HEADER_RE = re.compile(r"^\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}$")


def _strip_taf_prefix(line: str, icao_upper: str) -> str:
    tokens = line.split()
    if not tokens:
        return ""
    if tokens[0].upper() == "TAF":
        tokens = tokens[1:]
    if tokens and tokens[0].upper() in {"AMD", "COR", "RTD"}:
        tokens = tokens[1:]
    if tokens and tokens[0].upper() == icao_upper:
        tokens = tokens[1:]
    return " ".join(tokens)


def _normalize_taf_lines(lines: list[str], icao_upper: str) -> str:
    cleaned: list[str] = []
    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            continue
        if idx == 0:
            line = _strip_taf_prefix(line, icao_upper)
            if not line:
                continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def fetch_metar_taf(icao: str) -> Tuple[str, str]:
    """Fetch raw METAR and TAF strings for given ICAO code.

    Strategy:
      1. Try AviationWeather experimental API (may change format).
      2. If parsing fails or endpoint unavailable, fall back to classic NOAA
         text files (tgftp.nws.noaa.gov) which reliably host latest METAR & TAF.
    """
    icao_upper = icao.upper()
    params = {
        "ids": icao_upper,
        "format": "raw",
        "taf": "true",
    }
    logger.debug("Requesting METAR/TAF for %s", icao)
    try:
        resp = requests.get(API_URL, params=params, timeout=10)
        resp.raise_for_status()

        content_lines = [l.strip() for l in resp.text.strip().splitlines() if l.strip()]
        if content_lines:
            # Example format:
            #  EPLB 032100Z 33011KT ...
            #  TAF EPLB 031730Z 0318/0418 ...
            first_line_tokens = content_lines[0].split()
            if first_line_tokens[0].upper() == icao_upper:
                metar_raw = content_lines[0]
                taf_raw = _normalize_taf_lines(content_lines[1:], icao_upper)

                if metar_raw and taf_raw:
                    return metar_raw, taf_raw

        logger.debug("AviationWeather response not parsed, will fall back to NOAA.")
    except Exception as e:  # noqa: BLE001
        logger.debug("Failed to fetch from AviationWeather API: %s", e)

    # --- Fallback to NOAA text files ---
    metar_url = NOAA_METAR_URL.format(icao=icao_upper)
    taf_url = NOAA_TAF_URL.format(icao=icao_upper)

    logger.debug("Fetching METAR from %s", metar_url)
    metar_resp = requests.get(metar_url, timeout=10)
    metar_resp.raise_for_status()
    # NOAA text file has first line date/time, second line METAR
    metar_lines = metar_resp.text.strip().splitlines()
    metar_raw = metar_lines[-1].strip()

    logger.debug("Fetching TAF from %s", taf_url)
    taf_resp = requests.get(taf_url, timeout=10)
    taf_resp.raise_for_status()
    taf_lines = [l.rstrip() for l in taf_resp.text.strip().splitlines() if l.strip()]
    if taf_lines and _TAF_HEADER_RE.match(taf_lines[0]):
        taf_lines = taf_lines[1:]
    taf_raw = _normalize_taf_lines(taf_lines, icao_upper)

    if not metar_raw or len(metar_raw.split()) < 2:
        raise ValueError("Fallback NOAA source did not return valid METAR")
    if not taf_raw or len(taf_raw.split()) < 2:
        raise ValueError("Fallback NOAA source did not return valid TAF")

    return metar_raw, taf_raw
