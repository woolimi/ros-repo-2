"""FPS benchmark script for perception pipeline."""

import time


def measure_fps(detector, frames: list, mode: str = 'PERSON') -> float:
    """Measure detection FPS on provided frames."""
    start = time.monotonic()
    for frame in frames:
        detector.run(frame, mode)
    elapsed = time.monotonic() - start
    fps = len(frames) / elapsed if elapsed > 0 else 0.0
    print(f'FPS: {fps:.1f} over {len(frames)} frames')
    return fps


if __name__ == '__main__':
    print('No frames provided — import and call measure_fps() directly.')
