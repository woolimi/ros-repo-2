"""TCP client stub — connects to control_service:8080."""

import json
import logging
import socket
from typing import Optional

from config import CONTROL_SERVICE_HOST, CONTROL_SERVICE_PORT

logger = logging.getLogger(__name__)


class TCPClient:
    """Synchronous TCP client for customer_web ↔ control_service."""

    def __init__(self):
        self._sock: Optional[socket.socket] = None

    def connect(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((CONTROL_SERVICE_HOST, CONTROL_SERVICE_PORT))
        logger.info(f'[TCPClient] connected to {CONTROL_SERVICE_HOST}:{CONTROL_SERVICE_PORT}')

    def send(self, data: dict) -> None:
        if not self._sock:
            logger.error('[TCPClient] not connected')
            return
        try:
            self._sock.sendall((json.dumps(data) + '\n').encode('utf-8'))
        except OSError as e:
            logger.error(f'[TCPClient] send error: {e}')

    def disconnect(self) -> None:
        if self._sock:
            self._sock.close()
            self._sock = None
        logger.info('[TCPClient] disconnected')
