"""Mock implementations of ShopPinkki interfaces for development/testing."""

from .protocols import (
    BoundaryMonitorInterface,
    CartItem,
    Detection,
    NavBTInterface,
    OwnerDetectorInterface,
    PoseScannerInterface,
    QRScannerInterface,
    RobotPublisherInterface,
)


class MockOwnerDetector(OwnerDetectorInterface):
    """Always returns a fixed detection (or None based on always_detect)."""

    def __init__(self, always_detect: bool = True):
        self._always_detect = always_detect

    def run(self, frame, camera_mode: str) -> None:
        pass

    def get_latest(self):
        if self._always_detect:
            return Detection(cx=320.0, area=40000.0, distance=0.8, confidence=0.95)
        return None

    def register_target(self) -> None:
        print('[MockOwnerDetector] register_target()')


class MockQRScanner(QRScannerInterface):
    """Never calls on_scanned — simulates no QR found."""

    def start(self, on_scanned, on_timeout) -> None:
        print('[MockQRScanner] start() — will not call on_scanned')

    def stop(self) -> None:
        print('[MockQRScanner] stop()')


class MockPoseScanner(PoseScannerInterface):
    """Immediately returns empty pose list."""

    def scan(self, session_id, on_direction_done) -> list:
        print(f'[MockPoseScanner] scan(session_id={session_id}) → []')
        return []


class MockNavBT(NavBTInterface):
    """Returns a fixed tick result."""

    def __init__(self, result: str = 'SUCCESS'):
        self._result = result

    def start(self, **kwargs) -> None:
        print(f'[MockNavBT] start({kwargs})')

    def stop(self) -> None:
        print('[MockNavBT] stop()')

    def tick(self) -> str:
        return self._result


class MockBoundaryMonitor(BoundaryMonitorInterface):
    """Stores callbacks but never calls them."""

    def set_callbacks(self, on_zone_out, on_payment_zone) -> None:
        print('[MockBoundaryMonitor] set_callbacks()')

    def update_pose(self, x: float, y: float) -> None:
        pass


class MockRobotPublisher(RobotPublisherInterface):
    """Prints all calls; maintains an in-memory cart."""

    def __init__(self):
        self._cart: list[CartItem] = []
        self._next_id = 1

    def publish_status(self, mode, pos_x, pos_y, battery) -> None:
        print(f'[MockRobotPublisher] status: mode={mode} pos=({pos_x:.2f},{pos_y:.2f}) bat={battery}%')

    def publish_alarm(self, event_type, user_id='') -> None:
        print(f'[MockRobotPublisher] alarm: {event_type} user={user_id}')

    def publish_cart(self) -> None:
        items = [{'item_id': i.item_id, 'product_name': i.product_name, 'price': i.price}
                 for i in self._cart]
        print(f'[MockRobotPublisher] cart: {items}')

    def add_cart_item(self, product_name, price) -> None:
        item = CartItem(item_id=self._next_id, product_name=product_name, price=price)
        self._cart.append(item)
        self._next_id += 1
        print(f'[MockRobotPublisher] add_cart_item: {product_name} {price}원')

    def get_cart_items(self) -> list:
        return list(self._cart)

    def clear_cart(self) -> None:
        self._cart.clear()
        print('[MockRobotPublisher] clear_cart()')

    def terminate_session(self) -> None:
        print('[MockRobotPublisher] terminate_session()')
