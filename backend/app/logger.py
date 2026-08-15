"""
logger.py — Structured JSON logging for FLYYY.AI backend.

Uses stdlib `logging` only — no extra dependencies.
All scan lifecycle events are emitted as structured JSON lines for easy
ingestion by log aggregators (Datadog, Loki, CloudWatch, etc.).

Usage:
    from app.logger import get_logger
    log = get_logger(__name__)
    log.info("scan_started", scan_id="...", repo_url="...")
"""

import json
import logging
import sys
import time
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Merge any extra kwargs attached by the caller
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k
            not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            }
        }
        payload.update(extras)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def _build_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JsonFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


class _StructuredLogger:
    """
    Thin wrapper that lets callers write:
        log.info("scan_started", scan_id="abc", repo_url="...")
    instead of the verbose stdlib API.
    """

    def __init__(self, name: str):
        self._log = _build_logger(name)

    def _emit(self, level: int, event: str, **kwargs: Any) -> None:
        self._log.log(level, event, extra=kwargs)

    def debug(self, event: str, **kwargs: Any) -> None:
        self._emit(logging.DEBUG, event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        self._emit(logging.INFO, event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        self._emit(logging.WARNING, event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        self._emit(logging.ERROR, event, **kwargs)

    def exception(self, event: str, **kwargs: Any) -> None:
        self._emit(logging.ERROR, event, exc_info=True, **kwargs)


def get_logger(name: str) -> _StructuredLogger:
    """Return a structured logger for the given module name."""
    return _StructuredLogger(name)


def configure_root_logging(level: str = "INFO") -> None:
    """
    Call once at app startup to set the root log level.
    FastAPI/uvicorn's own loggers are left untouched.
    """
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger("app").setLevel(numeric)
