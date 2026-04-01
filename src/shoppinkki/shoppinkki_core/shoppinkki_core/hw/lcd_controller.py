"""LCD controller stub (ST7789 emotion display via pinky_interfaces SetEmotion service)."""

import logging

logger = logging.getLogger(__name__)

EMOTIONS = ('hello', 'basic', 'angry', 'bored', 'fun', 'happy', 'interest', 'sad')


class LCDController:
    """Controls LCD ST7789 emotion GIF via /set_emotion service."""

    def __init__(self, node):
        self._node = node

    def set_emotion(self, emotion: str) -> None:
        if emotion not in EMOTIONS:
            logger.warning(f'[LCD] unknown emotion: {emotion}')
            return
        logger.info(f'[LCD] set_emotion({emotion})')
