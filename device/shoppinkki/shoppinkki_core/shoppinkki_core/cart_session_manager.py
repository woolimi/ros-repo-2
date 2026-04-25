"""카트 + 배터리 + REST 호출 + 세션 lifecycle 매니저.

main_node에서 분리된 카트/배터리/세션 컴포넌트.

- 로컬 카트 캐시 (`_cart_items`)와 배터리 잔량(`_battery`) 보관.
- control_service REST(/zones, /session, /cart) 헬퍼 제공.
- 세션 시작/종료 시 카트 상태 초기화 및 `/robot_<id>/cart` 토픽 publish.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Optional
from urllib.error import HTTPError, URLError
from urllib import request as urlrequest

from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from std_msgs.msg import String

if TYPE_CHECKING:
    import rclpy.node

logger = logging.getLogger(__name__)


class CartSessionManager:
    """카트 아이템, 배터리, REST 호출, 세션 시작/종료 매니저."""

    def __init__(
        self,
        node: 'rclpy.node.Node',
        robot_id: str,
        control_service_base: str,
    ) -> None:
        self._node = node
        self._robot_id = str(robot_id)
        self._base = control_service_base.rstrip('/')

        # 카트 + 배터리 + zone 캐시 ───────────────
        self._cart_items: list = []
        self._battery: float = 100.0
        self._zones: dict[int, dict] = {}

        # /robot_<id>/cart publisher (main_node 원본과 동일하게 depth=10) ──
        cart_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )
        self._cart_pub = node.create_publisher(
            String, f'/robot_{self._robot_id}/cart', cart_qos
        )

    # ──────────────────────────────────────────
    # Public read-only properties
    # ──────────────────────────────────────────

    @property
    def items(self) -> list:
        return self._cart_items

    @property
    def battery(self) -> float:
        return self._battery

    @property
    def zones(self) -> dict[int, dict]:
        return self._zones

    @property
    def base_url(self) -> str:
        return self._base

    # ──────────────────────────────────────────
    # Mutators
    # ──────────────────────────────────────────

    def update_battery(self, pct: float) -> None:
        self._battery = float(pct)

    def fetch_zones(self, host: str, port: int) -> None:
        """control_service REST `/zones` 캐시 1회 fetch."""
        from shoppinkki_nav.nav2_client import fetch_all_zones
        try:
            self._zones = fetch_all_zones(host, port)
        except Exception as e:
            self._node.get_logger().warning(
                f'CartSessionManager: fetch_zones failed: {e}'
            )
            self._zones = {}

    def remove_item(self, item_id: int) -> None:
        """카트에서 item 제거 (main_node._on_delete_item 원본 동작)."""
        self._node.get_logger().info('delete_item: id=%d' % item_id)
        self._cart_items = [
            i for i in self._cart_items if i.get('id') != item_id
        ]

    def clear_session(self) -> None:
        """세션 시작/종료 시 카트 초기화."""
        self._cart_items = []

    def has_unpaid_items(self) -> bool:
        """True if cart has unpaid lines (local cache, else control_service REST).

        On REST/network errors, returns False so WAITING exit uses RETURNING
        (via ``waiting_exit_by_unpaid``), not LOCKED — avoids false LOCKED when
        the server cannot be reached. Matches BTRunner: callback exception → unpaid False.
        """
        # 1) Prefer local cart cache if available
        if any(not item.get('is_paid', True) for item in self._cart_items):
            return True

        # 2) Fallback to control_service REST for authoritative cart state
        try:
            session = self._rest_get_json(f'/session/robot/{self._robot_id}')
            cart_id = int((session or {}).get('cart_id', 0) or 0)
            if cart_id <= 0:
                return False
            result = self._rest_get_json(f'/cart/{cart_id}/has_unpaid')
            return bool((result or {}).get('has_unpaid', False))
        except (HTTPError, URLError, TimeoutError) as e:
            # 조회 실패 시 LOCKED 오탐을 피하기 위해 RETURNING 경로를 우선한다.
            self._node.get_logger().warning(
                f'has_unpaid_items fallback failed: {e}'
            )
            return False
        except Exception as e:
            self._node.get_logger().warning(
                f'has_unpaid_items unexpected error: {e}'
            )
            return False

    # ──────────────────────────────────────────
    # REST helper
    # ──────────────────────────────────────────

    def rest_get_json(self, path: str) -> dict:
        """control_service REST GET → JSON dict (404는 빈 dict)."""
        return self._rest_get_json(path)

    def _rest_get_json(self, path: str) -> dict:
        url = f'{self._base}{path}'
        req = urlrequest.Request(url, method='GET')
        try:
            with urlrequest.urlopen(req, timeout=1.5) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except HTTPError as e:
            # 404는 "활성 세션/카트 없음"으로 간주한다.
            if e.code == 404:
                return {}
            raise
