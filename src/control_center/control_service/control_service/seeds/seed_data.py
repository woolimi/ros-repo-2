"""Seed initial data — ZONEs, PRODUCTs, BOUNDARY_CONFIGs, ROBOTs."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from control_service.db import init_db, _get_conn, _lock

ZONES = [
    # (zone_id, zone_name, zone_type, waypoint_x, waypoint_y, waypoint_theta)
    (1,   '구역 1 (과자류)',      'product', None, None, None),
    (2,   '구역 2 (음료)',        'product', None, None, None),
    (3,   '구역 3 (유제품)',      'product', None, None, None),
    (4,   '구역 4 (냉동식품)',    'product', None, None, None),
    (5,   '구역 5 (즉석식품)',    'product', None, None, None),
    (6,   '구역 6 (생활용품)',    'product', None, None, None),
    (7,   '구역 7 (문구)',        'product', None, None, None),
    (8,   '구역 8 (장난감)',      'product', None, None, None),
    (130, '카트 입구',            'special', None, None, None),
    (140, '카트 출구 (대기열 1)', 'special', None, None, None),
    (141, '카트 출구 (대기열 2)', 'special', None, None, None),
    (150, '결제 구역',            'special', None, None, None),
    (160, '안내 데스크',          'special', None, None, None),
    (170, '비상구',               'special', None, None, None),
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


def reset_db():
    """Drop all tables and reinitialize schema. 개발 환경 전용."""
    from control_service.db import _DB_PATH
    import sqlite3
    os.makedirs(os.path.dirname(os.path.abspath(_DB_PATH)), exist_ok=True)
    with _lock:
        conn = sqlite3.connect(_DB_PATH)
        conn.executescript("""
            DROP TABLE IF EXISTS EVENT_LOG;
            DROP TABLE IF EXISTS ALARM_LOG;
            DROP TABLE IF EXISTS ROBOT;
            DROP TABLE IF EXISTS BOUNDARY_CONFIG;
            DROP TABLE IF EXISTS PRODUCT;
            DROP TABLE IF EXISTS ZONE;
            DROP TABLE IF EXISTS CARD;
            DROP TABLE IF EXISTS USER;
        """)
        conn.commit()
        conn.close()
    print('[seed_data] DB reset 완료')


def seed(replace: bool = False):
    """시드 데이터를 삽입한다.

    Args:
        replace: True이면 기존 행을 새 값으로 덮어씀 (INSERT OR REPLACE).
                 False이면 기존 행은 건드리지 않음 (INSERT OR IGNORE).
    """
    init_db()
    mode = 'REPLACE' if replace else 'IGNORE'
    with _lock:
        conn = _get_conn()
        conn.executemany(
            f"INSERT OR {mode} INTO ZONE "
            "(zone_id, zone_name, zone_type, waypoint_x, waypoint_y, waypoint_theta) "
            "VALUES (?,?,?,?,?,?)",
            ZONES,
        )
        conn.executemany(
            f"INSERT OR {mode} INTO PRODUCT (product_name, price, zone_id) VALUES (?,?,?)",
            PRODUCTS,
        )
        conn.executemany(
            f"INSERT OR {mode} INTO BOUNDARY_CONFIG "
            "(description, x_min, x_max, y_min, y_max) VALUES (?,?,?,?,?)",
            BOUNDARY_CONFIGS,
        )
        for (robot_id,) in ROBOTS:
            conn.execute(
                f"INSERT OR {mode} INTO ROBOT (robot_id) VALUES (?)", (robot_id,)
            )
        conn.commit()
        conn.close()
    print(f'[seed_data] done (mode={mode})')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='ShopPinkki control_service 시드 스크립트')
    parser.add_argument('--reset', action='store_true',
                        help='DB를 완전히 초기화한 뒤 시딩 (스키마 변경 시 사용)')
    parser.add_argument('--replace', action='store_true',
                        help='기존 행을 새 값으로 덮어씀 (INSERT OR REPLACE)')
    args = parser.parse_args()

    if args.reset:
        reset_db()
    seed(replace=args.reset or args.replace)
