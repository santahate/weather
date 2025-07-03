from importlib.metadata import version as _version

__all__ = ["__version__"]

try:
    __version__ = _version("weather_bot")
except Exception:  # pragma: no cover
    __version__ = "0.0.0"
