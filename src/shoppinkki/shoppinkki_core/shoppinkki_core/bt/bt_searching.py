"""Searching BT stub — rotation search."""

import logging
from shoppinkki_interfaces.protocols import NavBTInterface

logger = logging.getLogger(__name__)


class BTSearching(NavBTInterface):
    """Rotation search BT. Spins in place looking for the owner."""

    def start(self, **kwargs) -> None:
        logger.info('[BTSearching] start()')

    def stop(self) -> None:
        logger.info('[BTSearching] stop()')

    def tick(self) -> str:
        return 'RUNNING'
