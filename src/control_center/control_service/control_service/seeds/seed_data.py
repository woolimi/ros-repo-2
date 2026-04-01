"""Seed initial data — ZONEs, PRODUCTs, BOUNDARY_CONFIGs, ROBOTs."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from control_service.db import init_db, _get_conn, _lock

ZONES = [
    (1,   '구역 1 (과자류)',      None, None, None),
    (2,   '구역 2 (음료)',        None, None, None),
    (3,   '구역 3 (유제품)',      None, None, None),
    (4,   '구역 4 (냉동식품)',    None, None, None),
    (5,   '구역 5 (즉석식품)',    None, None, None),
    (6,   '구역 6 (생활용품)',    None, None, None),
    (7,   '구역 7 (문구)',        None, None, None),
    (8,   '구역 8 (장난감)',      None, None, None),
    (130, '카트 입구',            None, None, None),
    (140, '카트 출구 (대기열 1)', None, None, None),
    (141, '카트 출구 (대기열 2)', None, None, None),
    (150, '결제 구역',            None, None, None),
    (160, '안내 데스크',          None, None, None),
    (170, '비상구',               None, None, None),
]

PRODUCTS = [
    ('새우깡',    500,  1),
    ('콜라',      1200, 2),
    ('우유',      2000, 3),
    ('냉동만두',  3500, 4),
    ('컵라면',    800,  5),
    ('세제',      4000, 6),
    ('볼펜',      1000, 7),
    ('블록',      5000, 8),
]

BOUNDARY_CONFIGS = [
    ('shop_boundary',  -999.0, 999.0, -999.0, 999.0),
    ('payment_zone',   -999.0, 999.0, -999.0, 999.0),
]

ROBOTS = [
    ('54',),
    ('18',),
]


def seed():
    init_db()
    with _lock:
        conn = _get_conn()
        conn.executemany(
            "INSERT OR IGNORE INTO ZONE (zone_id, zone_name, waypoint_x, waypoint_y, waypoint_theta) "
            "VALUES (?,?,?,?,?)",
            ZONES,
        )
        conn.executemany(
            "INSERT OR IGNORE INTO PRODUCT (product_name, price, zone_id) VALUES (?,?,?)",
            PRODUCTS,
        )
        conn.executemany(
            "INSERT OR IGNORE INTO BOUNDARY_CONFIG (description, x_min, x_max, y_min, y_max) "
            "VALUES (?,?,?,?,?)",
            BOUNDARY_CONFIGS,
        )
        for (robot_id,) in ROBOTS:
            conn.execute(
                "INSERT OR IGNORE INTO ROBOT (robot_id) VALUES (?)", (robot_id,)
            )
        conn.commit()
        conn.close()
    print('[seed_data] done')


if __name__ == '__main__':
    seed()
