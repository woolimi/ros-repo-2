"""OwnerDetector — YOLO + ReID person follower."""

import logging
from typing import Optional

from shoppinkki_interfaces.protocols import Detection, OwnerDetectorInterface

logger = logging.getLogger(__name__)


class OwnerDetector(OwnerDetectorInterface):
    """Detects owner using YOLOv8 + HSV ReID."""

    def run(self, frame, camera_mode: str) -> None:
        pass

    def get_latest(self) -> Optional[Detection]:
        return None

    def register_target(self) -> None:
        logger.info('[OwnerDetector] register_target()')
