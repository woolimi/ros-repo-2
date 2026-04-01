from shoppinkki_perception.aruco_tracker import ArUcoTracker


def test_get_latest_returns_none():
    tracker = ArUcoTracker()
    assert tracker.get_latest() is None
