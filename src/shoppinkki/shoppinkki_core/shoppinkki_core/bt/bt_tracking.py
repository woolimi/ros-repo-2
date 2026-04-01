"""Tracking BT stub — P-Control follower."""

import logging
from shoppinkki_interfaces.protocols import NavBTInterface

logger = logging.getLogger(__name__)


class BTTracking(NavBTInterface):
    """P-Control follower BT. Publishes cmd_vel based on Detection."""

    def start(self, **kwargs) -> None:
        logger.info('[BTTracking] start()')

    def stop(self) -> None:
        logger.info('[BTTracking] stop()')

    def tick(self) -> str:
        return 'RUNNING'
