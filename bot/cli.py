from __future__ import annotations

import argparse
import logging
import sys
import traceback
from pathlib import Path

from . import api, chart, db, parser as parser_module, report as report_module, telegram
from . import taf_summary

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("bot.cli")


def parse_args(argv: list[str] | None = None):
    p = argparse.ArgumentParser(description="Fetch METAR/TAF and send Telegram report")
    p.add_argument("--airport", required=True, help="ICAO code of airport")
    p.add_argument("--timezone", required=True, help="Timezone string, e.g., Europe/Moscow or UTC+2")
    p.add_argument("--token", required=True, help="Telegram bot token")
    p.add_argument("--chat", required=True, help="Telegram chat ID")
    return p.parse_args(argv)


def main(argv: list[str] | None = None):
    args = parse_args(argv)

    try:
        db.init_db()

        metar_raw, taf_raw = api.fetch_metar_taf(args.airport)
        data = parser_module.decode_metar_taf(args.airport, metar_raw, taf_raw)

        if db.already_exists(data):
            logger.info("No new data – latest METAR/TAF already stored. Exiting.")
            return 0

        db.insert_weather(data)
        db.cleanup()

        # Prepare TAF summary (very naive – could be improved)
        taf_text = taf_summary.summarize_taf(taf_raw, data.taf_issue_time, args.timezone)

        text_report = report_module.generate_report(data, args.timezone, taf_text)

        tg = telegram.TelegramClient(args.token, args.chat)

        # Pressure chart
        rows = db.fetch_pressure_last_hours(12, icao=args.airport)
        chart_sent = False
        if rows and any(row[1] is not None for row in rows):
            try:
                img_path = chart.generate_pressure_chart(rows)
                tg.send_photo(img_path, caption=text_report if len(text_report) <= 1024 else None)
                chart_sent = True
            except ValueError as e:
                logger.warning("Chart skipped: %s", e)

        # If chart not sent (e.g., no data), send text separately
        if not chart_sent:
            tg.send_message(text_report)
    except Exception as e:  # noqa: BLE001
        err_text = traceback.format_exc()
        logger.error("Error occurred: %s", err_text)
        try:
            tg = telegram.TelegramClient(args.token, args.chat)  # may raise if token invalid
            tg.send_message(f"❗ Ошибка скрипта:\n{err_text}")
        except Exception:  # noqa: BLE001
            logger.exception("Could not send error message to Telegram")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
