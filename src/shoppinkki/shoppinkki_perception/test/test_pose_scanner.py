from shoppinkki_perception.pose_scanner import PoseScanner


def test_scan_returns_list():
    scanner = PoseScanner()
    result = scanner.scan(session_id=1, on_direction_done=lambda d: None)
    assert isinstance(result, list)
