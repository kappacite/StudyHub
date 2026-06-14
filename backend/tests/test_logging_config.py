import logging

from app.utils.logging_config import configure_logging, _HANDLER_NAME


class _FakeApp:
    def __init__(self, config):
        self.config = config


def _our_handlers():
    return [h for h in logging.getLogger().handlers if getattr(h, "name", None) == _HANDLER_NAME]


def test_configure_logging_adds_single_handler_and_is_idempotent():
    try:
        app = _FakeApp({"LOG_LEVEL": "INFO", "TESTING": False})
        configure_logging(app)
        configure_logging(app)  # un 2e appel (autre worker) ne doit pas dupliquer
        assert len(_our_handlers()) == 1
    finally:
        for h in _our_handlers():
            logging.getLogger().removeHandler(h)


def test_configure_logging_skips_in_testing():
    app = _FakeApp({"LOG_LEVEL": "INFO", "TESTING": True})
    configure_logging(app)
    assert _our_handlers() == []
