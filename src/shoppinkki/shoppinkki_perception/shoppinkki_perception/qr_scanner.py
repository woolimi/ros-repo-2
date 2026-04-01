"""QRScanner — QR code scanner for product/session QR."""

import logging
from typing import Callable

from shoppinkki_interfaces.protocols import QRScannerInterface

logger = logging.getLogger(__name__)


class QRScanner(QRScannerInterface):
    """Scans QR codes using OpenCV."""

    def start(self, on_scanned: Callable[[str], None], on_timeout: Callable[[], None]) -> None:
        logger.info('[QRScanner] start()')

    def stop(self) -> None:
        logger.info('[QRScanner] stop()')
