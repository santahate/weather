# Weather Bot – Implementation Plan

> Created by Full-Stack Dev (James)

## Goal
Build an automated script that fetches METAR/TAF, stores data in SQLite and pushes a human-readable report and pressure chart to Telegram, as described in `Weather Bot Description.md`.

## Milestones

1. Project scaffold (pyproject.toml, README, directory structure). ✅
2. Implement API fetch layer (bot/api.py). ✅
3. Implement decoding (bot/parser.py) using python-metar + metar-taf-parser. ✅
4. SQLite persistence and deduplication (bot/db.py). ✅
5. Text template + report builder (bot/report.py, bot/templates/report_template.txt). ✅
6. Pressure chart generation (bot/chart.py). ✅
7. Telegram integration (bot/telegram.py). ✅
8. CLI & orchestrator (bot/cli.py, main.py). ✅
9. Test run locally, add unit tests (future). ⬜
10. Documentation (README) and example cron. ✅

## Open points / Further Enhancements

* Improve TAF summarisation logic.
* Add unit tests & CI workflow.
* Set up linting / formatting (ruff, black) via uv.
* Parametrise SQLite path via env/CLI.

---

Date: {{TODAY}}
