"""BTReturning stub — Nav2 return to cart exit + queue assignment."""

import logging
from shoppinkki_interfaces.protocols import NavBTInterface

logger = logging.getLogger(__name__)


class BTReturning(NavBTInterface):
    """Returns robot to cart exit zone (140/141) via Nav2 and queue assignment."""

    def start(self, **kwargs) -> None:
        logger.info('[BTReturning] start()')

    def stop(self) -> None:
        logger.info('[BTReturning] stop()')

    def tick(self) -> str:
        return 'RUNNING'
