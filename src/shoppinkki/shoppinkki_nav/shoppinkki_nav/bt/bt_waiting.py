"""BTWaiting stub — pedestrian avoidance during WAITING state."""

import logging
from shoppinkki_interfaces.protocols import NavBTInterface

logger = logging.getLogger(__name__)


class BTWaiting(NavBTInterface):
    """Waits in place, avoiding pedestrians if needed."""

    def start(self, **kwargs) -> None:
        logger.info('[BTWaiting] start()')

    def stop(self) -> None:
        logger.info('[BTWaiting] stop()')

    def tick(self) -> str:
        return 'RUNNING'
