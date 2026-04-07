-- ShopPinkki Seed Data
USE shoppinkki;

-- ──────────────────────────────────────────────
-- ZONE (상품 구역 1~8, 특수 구역)
-- ──────────────────────────────────────────────

INSERT INTO ZONE (zone_id, zone_name, zone_type, waypoint_x, waypoint_y, waypoint_theta) VALUES
-- 상품 구역
(1,   '가전제품',  'product', 0.0, 0.0, 0.0),
(2,   '과자',     'product', 0.0, 0.0, 0.0),
(3,   '해산물',   'product', 0.0, 0.0, 0.0),
(4,   '육류',     'product', 0.0, 0.0, 0.0),
(5,   '채소',     'product', 0.0, 0.0, 0.0),
(6,   '음료',     'product', 0.0, 0.0, 0.0),
(7,   '베이커리', 'product', 0.0, 0.0, 0.0),
(8,   '음식',     'product', 0.0, 0.0, 0.0),
-- 특수 구역
(100, '화장실',   'special', 0.0, 0.0, 0.0),
(110, '입구',     'special', 0.0, 0.0, 0.0),
(120, '출구',     'special', 0.0, 0.0, 0.0),
(140, '충전소 P1','special', 0.699, 0.100, 1.5708),
(141, '충전소 P2','special', 0.939, 0.100, 1.5708),
(150, '결제 구역','special', 0.0, 0.0, 0.0)
ON DUPLICATE KEY UPDATE zone_name=VALUES(zone_name);

-- ──────────────────────────────────────────────
-- PRODUCT
-- ──────────────────────────────────────────────

INSERT INTO PRODUCT (product_name, zone_id, price) VALUES
('TV',       1, 990000), ('냉장고',   1, 1290000), ('에어컨',   1, 1590000),
('쌀과자',   2,   2000), ('포카칩',   2,    1800), ('오레오',   2,    2500),
('연어',     3,  12000), ('새우',     3,    9000), ('오징어',   3,    8000),
('소고기',   4,  15000), ('돼지고기', 4,    9000), ('닭고기',   4,    7000),
('당근',     5,   1500), ('브로콜리', 5,    2500), ('상추',     5,    2000),
('콜라',     6,   1500), ('커피',     6,    3000), ('오렌지주스', 6,   3500),
('식빵',     7,   2800), ('크루아상', 7,    3200), ('머핀',     7,    3000),
('볶음밥',   8,   5500), ('라면',     8,    4500), ('떡볶이',   8,    5000)
ON DUPLICATE KEY UPDATE zone_id=VALUES(zone_id), price=VALUES(price);

-- ──────────────────────────────────────────────
-- BOUNDARY_CONFIG
-- ──────────────────────────────────────────────

INSERT INTO BOUNDARY_CONFIG (description, x_min, x_max, y_min, y_max) VALUES
('결제 구역',     1.0,  1.8,  -0.3, 0.5),
('맵 외곽 경계',  -0.3, 1.6,  -1.7, 0.3)
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- ──────────────────────────────────────────────
-- ROBOT
-- ──────────────────────────────────────────────

INSERT INTO ROBOT (robot_id, ip_address, current_mode) VALUES
('54', '192.168.102.54', 'CHARGING'),
('18', '192.168.102.18', 'CHARGING')
ON DUPLICATE KEY UPDATE ip_address=VALUES(ip_address), current_mode='CHARGING';

-- ──────────────────────────────────────────────
-- USER / CARD (테스트 계정, password = 'test1234' bcrypt)
-- ──────────────────────────────────────────────

INSERT INTO USER (user_id, password_hash) VALUES
('test01', '$2b$12$KIXbVqfTz0iYa.W9P1qG3OQvK6T8m2zN5cLnRjpFdS4AyXeUvHwMi'),
('test02', '$2b$12$KIXbVqfTz0iYa.W9P1qG3OQvK6T8m2zN5cLnRjpFdS4AyXeUvHwMi')
ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash);

INSERT INTO CARD (user_id, card_alias) VALUES
('test01', '신한카드 1234'),
('test02', '국민카드 5678')
ON DUPLICATE KEY UPDATE card_alias=VALUES(card_alias);
