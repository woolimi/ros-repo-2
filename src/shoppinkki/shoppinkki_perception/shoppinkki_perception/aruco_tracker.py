"""ArUco tracker — OwnerDetectorInterface for ArUco marker mode."""

import logging
from typing import Optional

from shoppinkki_interfaces.protocols import Detection, OwnerDetectorInterface

logger = logging.getLogger(__name__)


class ArUcoTracker(OwnerDetectorInterface):
    """Tracks owner via ArUco marker attached to shopping cart handle."""

    def run(self, frame, camera_mode: str) -> None:
        pass

    def get_latest(self) -> Optional[Detection]:
        return None

    def register_target(self) -> None:
        logger.info('[ArUcoTracker] register_target()')
