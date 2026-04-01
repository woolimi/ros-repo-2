"""BTGuiding stub tests."""

from shoppinkki_nav.bt.bt_guiding import BTGuiding


def test_tick_returns_running():
    bt = BTGuiding()
    bt.start(zone_id=6)
    assert bt.tick() == 'RUNNING'
    bt.stop()
