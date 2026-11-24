import logging

from flask import g, has_request_context


class RequestIdFilter(logging.Filter):
    """Adds the current request id to every log record."""

    def filter(self, record):
        record.request_id = g.get("request_id", "-") if has_request_context() else "-"
        return True


def configure_logging(level):
    logger = logging.getLogger("library")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.addFilter(RequestIdFilter())
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s"
            )
        )
        logger.addHandler(handler)
