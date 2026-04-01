"""ABC interfaces and dataclasses for ShopPinkki components."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Detection:
    """Detected target information."""

    cx: float           # center x in image (px)
    area: float         # bounding box area (px²)
    distance: float     # distance in meters (ArUco mode)
    confidence: float   # detection confidence (0~1)


@dataclass
class CartItem:
    """Cart item entry."""

    item_id: int
    product_name: str
    price: int


class OwnerDetectorInterface(ABC):
    """Interface for owner detection (YOLO+ReID or ArUco)."""

    @abstractmethod
    def run(self, frame, camera_mode: str) -> None:
        """Process a single frame. camera_mode: 'PERSON' or 'ARUCO'."""
        pass

    @abstractmethod
    def get_latest(self) -> Optional[Detection]:
        """Return the latest detection result, or None if not detected."""
        pass

    @abstractmethod
    def register_target(self) -> None:
        """Register the current detection as the tracking target."""
        pass


class QRScannerInterface(ABC):
    """Interface for QR code scanner."""

    @abstractmethod
    def start(self, on_scanned: Callable[[str], None], on_timeout: Callable[[], None]) -> None:
        """Start QR scanning. Calls on_scanned(data) or on_timeout() when done."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop QR scanning."""
        pass


class PoseScannerInterface(ABC):
    """Interface for 4-direction pose scan (HSV histogram registration)."""

    @abstractmethod
    def scan(self, session_id: int, on_direction_done: Callable[[str], None]) -> list:
        """Run pose scan. Returns list of pose dicts. Calls on_direction_done(direction) per step."""
        pass


class NavBTInterface(ABC):
    """Interface for navigation behavior tree."""

    @abstractmethod
    def start(self, **kwargs) -> None:
        """Start the behavior tree with given parameters."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the behavior tree."""
        pass

    @abstractmethod
    def tick(self) -> str:
        """Tick the BT once. Returns 'RUNNING', 'SUCCESS', or 'FAILURE'."""
        pass


class BoundaryMonitorInterface(ABC):
    """Interface for shop boundary monitoring."""

    @abstractmethod
    def set_callbacks(
        self,
        on_zone_out: Callable[[], None],
        on_payment_zone: Callable[[], None],
    ) -> None:
        """Register callbacks for boundary events."""
        pass

    @abstractmethod
    def update_pose(self, x: float, y: float) -> None:
        """Update the robot's current pose for boundary checking."""
        pass


class RobotPublisherInterface(ABC):
    """Interface for publishing robot state to control_service via ROS topics."""

    @abstractmethod
    def publish_status(self, mode: str, pos_x: float, pos_y: float, battery: int) -> None:
        """Publish /robot_<id>/status."""
        pass

    @abstractmethod
    def publish_alarm(self, event_type: str, user_id: str = '') -> None:
        """Publish /robot_<id>/alarm."""
        pass

    @abstractmethod
    def publish_cart(self) -> None:
        """Publish /robot_<id>/cart with current cart items."""
        pass

    @abstractmethod
    def add_cart_item(self, product_name: str, price: int) -> None:
        """Add an item to the cart."""
        pass

    @abstractmethod
    def get_cart_items(self) -> list:
        """Return list of CartItem."""
        pass

    @abstractmethod
    def clear_cart(self) -> None:
        """Clear all cart items."""
        pass

    @abstractmethod
    def terminate_session(self) -> None:
        """Publish session termination signal."""
        pass
