"""LED controller stub (WS2812B via pinky_interfaces SetLed service)."""

import logging

logger = logging.getLogger(__name__)


class LEDController:
    """Controls WS2812B LED strip via /set_led service."""

    def __init__(self, node):
        self._node = node

    def set_color(self, r: int, g: int, b: int) -> None:
        logger.info(f'[LED] set_color({r},{g},{b})')

    def off(self) -> None:
        logger.info('[LED] off()')
