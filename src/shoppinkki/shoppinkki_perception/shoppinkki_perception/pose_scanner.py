"""PoseScanner — 4-direction pose scan for PERSON mode registration."""

import logging
from typing import Callable

from shoppinkki_interfaces.protocols import PoseScannerInterface

logger = logging.getLogger(__name__)


class PoseScanner(PoseScannerInterface):
    """Guides user through 4 directions and captures HSV histograms."""

    def scan(self, session_id: int, on_direction_done: Callable[[str], None]) -> list:
        logger.info(f'[PoseScanner] scan(session_id={session_id})')
        return []
