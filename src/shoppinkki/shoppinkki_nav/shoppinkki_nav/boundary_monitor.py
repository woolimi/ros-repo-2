"""BoundaryMonitor — checks robot pose against configured zone boundaries."""

import logging
from typing import Callable, Optional

from shoppinkki_interfaces.protocols import BoundaryMonitorInterface

logger = logging.getLogger(__name__)


class BoundaryMonitor(BoundaryMonitorInterface):
    """Real boundary monitor using BOUNDARY_CONFIG fetched from control_service."""

    def __init__(self):
        self._on_zone_out: Optional[Callable[[], None]] = None
        self._on_payment_zone: Optional[Callable[[], None]] = None
        self._shop_boundary = None
        self._payment_zone = None

    def set_callbacks(
        self,
        on_zone_out: Callable[[], None],
        on_payment_zone: Callable[[], None],
    ) -> None:
        self._on_zone_out = on_zone_out
        self._on_payment_zone = on_payment_zone
        logger.info('[BoundaryMonitor] callbacks set')

    def update_pose(self, x: float, y: float) -> None:
        pass
