"""Buzzer stub (GPIO via RPi.GPIO or similar)."""

import logging

logger = logging.getLogger(__name__)


class Buzzer:
    """Controls onboard buzzer."""

    def beep(self, duration: float = 0.2, count: int = 1) -> None:
        logger.info(f'[Buzzer] beep(duration={duration}, count={count})')
