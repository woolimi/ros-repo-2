"""State machine unit tests."""

import pytest
from transitions import MachineError

from shoppinkki_core.state_machine import ShopPinkkiSM


def _make_sm() -> ShopPinkkiSM:
    return ShopPinkkiSM()


def test_initial_state():
    sm = _make_sm()
    assert sm.state == 'IDLE'


def test_full_session_flow():
    sm = _make_sm()
    sm.start_session()
    assert sm.state == 'REGISTERING'
    sm.registration_done()
    assert sm.state == 'TRACKING'
    sm.owner_lost()
    assert sm.state == 'SEARCHING'
    sm.owner_found()
    assert sm.state == 'TRACKING'
    sm.to_waiting()
    assert sm.state == 'WAITING'
    sm.start_returning()
    assert sm.state == 'RETURNING'
    sm.session_ended()
    assert sm.state == 'IDLE'


def test_dismiss_to_idle_after_theft():
    sm = _make_sm()
    sm.start_session()
    sm.registration_done()
    sm.current_alarm = 'THEFT'
    sm.zone_out()
    assert sm.state == 'ALARM'
    sm.dismiss_to_idle()
    assert sm.state == 'IDLE'


def test_dismiss_to_waiting_after_battery_low():
    sm = _make_sm()
    sm.start_session()
    sm.registration_done()
    sm.current_alarm = 'BATTERY_LOW'
    sm.battery_low()
    assert sm.state == 'ALARM'
    sm.dismiss_to_waiting()
    assert sm.state == 'WAITING'


def test_invalid_transition_raises():
    sm = _make_sm()
    with pytest.raises(MachineError):
        sm.registration_done()  # IDLE → REGISTERING not done yet


def test_admin_force_idle_from_any_state():
    sm = _make_sm()
    sm.start_session()
    sm.registration_done()
    sm.to_waiting()
    sm.admin_force_idle()
    assert sm.state == 'IDLE'
