from shoppinkki_perception.qr_scanner import QRScanner


def test_start_stop_no_crash():
    scanner = QRScanner()
    scanner.start(on_scanned=lambda d: None, on_timeout=lambda: None)
    scanner.stop()
