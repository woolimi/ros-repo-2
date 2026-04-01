"""ReID matcher — HSV histogram comparison."""

import logging

logger = logging.getLogger(__name__)


def extract_hsv_histogram(image, region) -> list:
    """Extract HSV histogram from image region. Returns histogram as list."""
    return []


def compare(h1: list, h2: list) -> float:
    """Compare two HSV histograms. Returns similarity score 0~1."""
    return 0.0
