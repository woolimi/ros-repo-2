from shoppinkki_perception.owner_detector import OwnerDetector


def test_get_latest_returns_none():
    detector = OwnerDetector()
    assert detector.get_latest() is None
