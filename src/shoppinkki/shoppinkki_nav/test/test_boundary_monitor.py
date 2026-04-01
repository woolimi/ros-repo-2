"""BoundaryMonitor stub tests."""

from shoppinkki_nav.boundary_monitor import BoundaryMonitor


def test_set_callbacks():
    bm = BoundaryMonitor()
    bm.set_callbacks(on_zone_out=lambda: None, on_payment_zone=lambda: None)
    assert bm._on_zone_out is not None


def test_update_pose_no_crash():
    bm = BoundaryMonitor()
    bm.set_callbacks(on_zone_out=lambda: None, on_payment_zone=lambda: None)
    bm.update_pose(0.5, 0.5)
