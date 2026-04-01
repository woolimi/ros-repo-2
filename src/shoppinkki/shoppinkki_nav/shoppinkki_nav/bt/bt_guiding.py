"""BTGuiding stub — Nav2-based zone navigation."""

import logging
from shoppinkki_interfaces.protocols import NavBTInterface

logger = logging.getLogger(__name__)


class BTGuiding(NavBTInterface):
    """Navigates to a target zone using Nav2."""

    def __init__(self):
        self._zone_id: int = 0

    def start(self, zone_id: int = 0, **kwargs) -> None:
        self._zone_id = zone_id
        logger.info(f'[BTGuiding] start(zone_id={zone_id})')

    def stop(self) -> None:
        logger.info('[BTGuiding] stop()')

    def tick(self) -> str:
        return 'RUNNING'
