# Weather Bot

Python 3.14-compatible script that fetches METAR/TAF for a selected airport, stores unique reports in SQLite and publishes updates (text + pressure chart) to Telegram.

## Quick start

```bash
# 1. Install uv (if not installed)
curl -Ls https://astral.sh/uv/install.sh | sh

# 2. Install project dependencies (creates .venv)
uv venv .venv -p python3.14
uv pip install -r pyproject.toml  # uv understands PEP-621 deps

# 3. Run manual fetch
source /path/to/project/.venv/bin/activate
python -m bot.cli --airport UUEE --timezone Europe/Warsaw --token $TG_TOKEN --chat $CHAT_ID
```

## Cron example (every 10 minutes)

```cron
*/5 * * * * cd /path/to/project/ &&  /path/to/project/.venv/bin/python -m bot.cli --airport XXXX --timezone Europe/Warsaw --token "XXXX" --chat -XXXX'
```

## Project layout

```
bot/
  __init__.py
  api.py          # HTTP requests to aviationweather.gov
  parser.py       # Decode METAR/TAF
  db.py           # SQLite persistence
  report.py       # Build human-readable report
  chart.py        # Pressure chart via matplotlib
  telegram.py     # Message/photo posting
  templates/
    report.txt    # Text template for the report
main.py           # Entry-point wrapper (import bot.cli)
```

## Development

* Dependencies are declared in `pyproject.toml`; manage them via **uv**.
* Run tests with:

```bash
uv -q python -m pytest
```

* Linting:

```bash
uv -q python -m ruff check .
```

## License

MIT
