"""BT thread runner — ticks a NavBTInterface at a fixed rate."""

import threading
import time
import logging
from typing import Callable, Optional

from shoppinkki_interfaces.protocols import NavBTInterface

logger = logging.getLogger(__name__)


class BTRunner:
    """Runs a NavBTInterface in a background thread at a fixed tick rate."""

    def __init__(self):
        self._bt: Optional[NavBTInterface] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._hz = 10.0
        self.on_result: Optional[Callable[[str], None]] = None

    def start(self, bt: NavBTInterface, hz: float = 10.0, **kwargs) -> None:
        """Start ticking bt at hz. Calls self.on_result('SUCCESS'|'FAILURE') when done."""
        if self._running:
            self.stop()
        self._bt = bt
        self._hz = hz
        self._running = True
        bt.start(**kwargs)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info(f'[BTRunner] started at {hz}Hz')

    def stop(self) -> None:
        """Stop the BT runner."""
        self._running = False
        if self._bt:
            self._bt.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        self._bt = None
        logger.info('[BTRunner] stopped')

    def _loop(self) -> None:
        interval = 1.0 / self._hz
        while self._running and self._bt:
            result = self._bt.tick()
            if result in ('SUCCESS', 'FAILURE'):
                self._running = False
                logger.info(f'[BTRunner] BT finished: {result}')
                if self.on_result:
                    self.on_result(result)
                break
            time.sleep(interval)
