"""ShopPinkki main ROS2 node — wired with Mock implementations."""

import json
import logging
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from shoppinkki_interfaces.mocks import (
    MockBoundaryMonitor,
    MockNavBT,
    MockOwnerDetector,
    MockPoseScanner,
    MockQRScanner,
    MockRobotPublisher,
)
from shoppinkki_core.state_machine import ShopPinkkiSM
from shoppinkki_core.bt_runner import BTRunner
from shoppinkki_core.hw.led_controller import LEDController
from shoppinkki_core.hw.lcd_controller import LCDController
from shoppinkki_core.hw.buzzer import Buzzer
from shoppinkki_core import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROBOT_ID = '54'
HEARTBEAT_HZ = 0.5  # 2-second period


class MainNode(Node):
    """ShopPinkki main node."""

    def __init__(self):
        super().__init__('shoppinkki_main')

        # --- DB init ---
        db.init_db()

        # --- SM ---
        self._sm = ShopPinkkiSM()
        self._sm.on_enter_IDLE = self._on_enter_IDLE
        self._sm.on_enter_REGISTERING = self._on_enter_REGISTERING
        self._sm.on_enter_TRACKING = self._on_enter_TRACKING
        self._sm.on_enter_SEARCHING = self._on_enter_SEARCHING
        self._sm.on_enter_WAITING = self._on_enter_WAITING
        self._sm.on_enter_ITEM_ADDING = self._on_enter_ITEM_ADDING
        self._sm.on_enter_GUIDING = self._on_enter_GUIDING
        self._sm.on_enter_RETURNING = self._on_enter_RETURNING
        self._sm.on_enter_ALARM = self._on_enter_ALARM

        # --- BT Runner ---
        self._bt_runner = BTRunner()

        # --- HW stubs ---
        self._led = LEDController(self)
        self._lcd = LCDController(self)
        self._buzzer = Buzzer()

        # --- Mock components ---
        self._owner_detector = MockOwnerDetector(always_detect=True)
        self._qr_scanner = MockQRScanner()
        self._pose_scanner = MockPoseScanner()
        self._bt_tracking = MockNavBT(result='RUNNING')
        self._bt_searching = MockNavBT(result='RUNNING')
        self._bt_waiting = MockNavBT(result='RUNNING')
        self._boundary_monitor = MockBoundaryMonitor()
        self._robot_publisher = MockRobotPublisher()

        self._boundary_monitor.set_callbacks(
            on_zone_out=self._on_zone_out,
            on_payment_zone=self._on_payment_zone,
        )

        # --- ROS subscriptions ---
        self._cmd_sub = self.create_subscription(
            String,
            f'/robot_{ROBOT_ID}/cmd',
            self._on_cmd,
            10,
        )

        # --- Heartbeat timer ---
        self._heartbeat_timer = self.create_timer(
            1.0 / HEARTBEAT_HZ,
            self._heartbeat,
        )

        self.get_logger().info(f'[MainNode] started — SM state: {self._sm.state}')

    # --- Heartbeat ---

    def _heartbeat(self):
        self._robot_publisher.publish_status(
            mode=self._sm.state,
            pos_x=0.0,
            pos_y=0.0,
            battery=100,
        )

    # --- CMD handler ---

    def _on_cmd(self, msg: String):
        try:
            payload = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().error(f'[MainNode] invalid cmd JSON: {msg.data}')
            return

        cmd = payload.get('cmd')
        self.get_logger().info(f'[MainNode] cmd received: {cmd}')

        if cmd == 'start_session':
            self._sm.start_session()
        elif cmd == 'mode':
            value = payload.get('value', '')
            if value == 'WAITING':
                self._sm.to_waiting()
            elif value == 'TRACKING':
                self._sm.to_tracking()
            elif value == 'RETURNING':
                self._sm.start_returning()
            elif value == 'ITEM_ADDING':
                self._sm.to_item_adding()
        elif cmd == 'dismiss_alarm':
            if self._sm.current_alarm == 'THEFT':
                self._sm.dismiss_to_idle()
            else:
                self._sm.dismiss_to_waiting()
        elif cmd == 'payment_error':
            self._sm.payment_error()
        elif cmd == 'force_terminate':
            self._sm.admin_force_idle()
        else:
            self.get_logger().warning(f'[MainNode] unknown cmd: {cmd}')

    # --- Boundary callbacks ---

    def _on_zone_out(self):
        self._sm.current_alarm = 'THEFT'
        self._sm.zone_out()

    def _on_payment_zone(self):
        self._sm.to_waiting()

    # --- SM enter callbacks ---

    def _on_enter_IDLE(self):
        self.get_logger().info('[SM] → IDLE')
        self._led.off()
        self._lcd.set_emotion('basic')

    def _on_enter_REGISTERING(self):
        self.get_logger().info('[SM] → REGISTERING')
        self._lcd.set_emotion('hello')

    def _on_enter_TRACKING(self):
        self.get_logger().info('[SM] → TRACKING')
        self._lcd.set_emotion('happy')

    def _on_enter_SEARCHING(self):
        self.get_logger().info('[SM] → SEARCHING')
        self._lcd.set_emotion('interest')

    def _on_enter_WAITING(self):
        self.get_logger().info('[SM] → WAITING')
        self._lcd.set_emotion('basic')

    def _on_enter_ITEM_ADDING(self):
        self.get_logger().info('[SM] → ITEM_ADDING')

    def _on_enter_GUIDING(self):
        self.get_logger().info('[SM] → GUIDING')

    def _on_enter_RETURNING(self):
        self.get_logger().info('[SM] → RETURNING')

    def _on_enter_ALARM(self):
        alarm = self._sm.current_alarm
        self.get_logger().info(f'[SM] → ALARM ({alarm})')
        self._robot_publisher.publish_alarm(alarm or 'UNKNOWN')
        self._buzzer.beep(count=3)
        self._lcd.set_emotion('angry')


def main(args=None):
    rclpy.init(args=args)
    node = MainNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
