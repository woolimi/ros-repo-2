# Interface Specification

> **프로젝트:** 쑈삥끼 (ShopPinkki)
> 모듈 간 통신 규칙 명세. 채널 A~H 기준: `docs/system_architecture.md`

---

## 1. Python 모듈 간 인터페이스

구현체 위치: `src/shoppinkki/shoppinkki_interfaces/`

### 의존 관계

```
shoppinkki_core (main_node)
    ├── DollDetectorInterface    ← shoppinkki_perception 구현
    ├── QRScannerInterface       ← shoppinkki_perception 구현
    ├── NavBTInterface           ← shoppinkki_nav 구현
    ├── BoundaryMonitorInterface ← shoppinkki_nav 구현
    └── RobotPublisherInterface  ← shoppinkki_core 내부 구현
```

### `protocols.py`

```python
from typing import Protocol, Optional
from dataclasses import dataclass

# ── 공유 데이터 타입 ──────────────────────────────────────────

@dataclass
class Detection:
    cx: float           # bbox 중심 x (픽셀)
    area: float         # bbox 넓이 (px²) — P-Control 선속도용
    confidence: float   # YOLO 감지 신뢰도 (0~1)
    reid_score: float   # ReID + 색상 유사도 (0~1)

@dataclass
class CartItem:
    item_id: int
    product_name: str
    price: int
    is_paid: bool


# ── shoppinkki_perception ────────────────────────────────────

class DollDetectorInterface(Protocol):
    def register(self, frame) -> bool: ...
    # IDLE 단계: 프레임에서 인형 YOLO 감지 후 ReID + 색상 템플릿 등록.
    # 감지 성공 시 True, 미감지 시 False.

    def run(self, frame) -> None: ...
    # TRACKING 단계: YOLO 감지 → ReID + 색상 매칭 → 결과를 내부 버퍼에 저장.

    def get_latest(self) -> Optional[Detection]: ...
    # 가장 최근 프레임의 주인 인형 감지 결과.
    # 미감지 또는 ReID 임계값 미달 시 None.

    def is_ready(self) -> bool: ...
    # register() 성공 후 True. SM이 IDLE → TRACKING 전환 판단에 사용.


class QRScannerInterface(Protocol):
    def start(self, on_scanned: callable, on_timeout: callable) -> None: ...
    # on_scanned(name: str, price: int) — 스캔 성공마다 호출, 타이머 리셋
    # on_timeout() — 마지막 스캔으로부터 30초 무활동 시 호출

    def stop(self) -> None: ...


# ── shoppinkki_nav ───────────────────────────────────────────

class NavBTInterface(Protocol):
    def start(self, **kwargs) -> None: ...
    # BTGuiding: start(zone_id=6)
    # BTReturning: start(slot_zone_id=140)

    def stop(self) -> None: ...

    def tick(self) -> str: ...
    # 반환: "RUNNING" | "SUCCESS" | "FAILURE"


class BoundaryMonitorInterface(Protocol):
    def set_callbacks(
        self,
        on_checkout_enter: callable,
        on_checkout_exit_blocked: callable,
        on_checkout_reenter: callable,
    ) -> None: ...
    # on_checkout_enter()         — TRACKING 중 결제 구역 진입 감지 (1회)
    # on_checkout_exit_blocked()  — TRACKING 중 출구 방향 이동 차단
    # on_checkout_reenter()       — TRACKING_CHECKOUT 중 결제 구역 재진입

    def update_pose(self, x: float, y: float) -> None: ...
    # /amcl_pose 수신마다 호출


# ── shoppinkki_core 내부 ─────────────────────────────────────

class RobotPublisherInterface(Protocol):
    def publish_status(
        self,
        mode: str,
        pos_x: float,
        pos_y: float,
        battery: int,
        is_locked_return: bool = False,
    ) -> None: ...
    # /robot_<id>/status 발행 (1~2Hz heartbeat)

    def publish_staff_call(self, event_type: str) -> None: ...
    # /robot_<id>/alarm 발행. event_type: 'LOCKED' | 'HALTED'

    def get_cart_items(self) -> list[CartItem]: ...
    def has_unpaid_items(self) -> bool: ...
    # is_paid=False인 CART_ITEM 존재 여부. 보내주기 분기 판단용

    def add_cart_item(self, product_name: str, price: int) -> None: ...
    def delete_cart_item(self, item_id: int) -> None: ...
    def mark_items_paid(self) -> None: ...
    # 현재 is_paid=0인 CART_ITEM 전체 → is_paid=1

    def terminate_session(self) -> None: ...
    # SESSION.is_active=False + CART_ITEM 전체 삭제
```

---

## 2. 채널별 메시지 명세

### 채널 A — Customer UI ↔ customer_web (WebSocket)

| 방향 | 메시지 | 설명 |
|---|---|---|
| 앱 → web | `{"cmd": "mode", "value": "WAITING"}` | [대기하기] 클릭 |
| 앱 → web | `{"cmd": "resume_tracking"}` | [따라가기] / 도착 팝업 [확인] 클릭 |
| 앱 → web | `{"cmd": "return"}` | [쇼핑 종료] 클릭 (보내주기) |
| 앱 → web | `{"cmd": "navigate_to", "zone_id": 6}` | 상품 안내 요청 |
| 앱 → web | `{"cmd": "delete_item", "item_id": 3}` | 장바구니 항목 삭제 |
| web → 앱 | `{"type": "status", "my_robot": {"robot_id": 54, "mode": "TRACKING", "pos_x": 1.2, "pos_y": 0.8, "battery": 72, "is_locked_return": false}, "other_robots": [{"robot_id": 18, "pos_x": 0.5, "pos_y": 0.3}]}` | 1~2Hz push. `other_robots`는 위치만 포함 |
| web → 앱 | `{"type": "cart", "items": [{"id": 1, "name": "콜라", "price": 1500, "is_paid": false}]}` | 장바구니 갱신 |
| web → 앱 | `{"type": "registration_done"}` | 인형 등록 완료 → 메인 화면 전환 |
| web → 앱 | `{"type": "checkout_zone_enter"}` | 결제 구역 진입 → 결제 팝업(3-F) 표시 |
| web → 앱 | `{"type": "checkout_blocked"}` | 미결제 출구 시도 차단 → 토스트 표시 |
| web → 앱 | `{"type": "payment_done"}` | 결제 완료 → 팝업 닫힘, 뱃지 TRACKING_CHECKOUT 전환 |
| web → 앱 | `{"type": "find_product_result", "zone_id": 6, "zone_name": "음료"}` | 상품 검색 결과 |
| web → 앱 | `{"type": "arrived", "zone_name": "음료"}` | 도착 팝업(3-H) 표시 |
| web → 앱 | `{"type": "nav_failed"}` | 안내 실패 토스트 |
| web → 앱 | `{"type": "enter_locked"}` | LOCKED 알림 패널(3-G) 전환 |
| web → 앱 | `{"type": "enter_halted"}` | HALTED 알림 패널(3-I) 전환 |
| web → 앱 | `{"type": "staff_resolved"}` | 세션 종료 → login.html 리다이렉트 |

---

### 채널 B — Admin UI ↔ control_service (TCP :8080)

| 방향 | 메시지 | 설명 |
|---|---|---|
| admin → control | `{"cmd": "mode", "robot_id": 54, "value": "WAITING"\|"RETURNING"}` | 모드 전환 |
| admin → control | `{"cmd": "resume_tracking", "robot_id": 54}` | [추종] 버튼 — Pi SM `resume_tracking()` 호출 |
| admin → control | `{"cmd": "force_terminate", "robot_id": 54}` | 강제 종료 |
| admin → control | `{"cmd": "staff_resolved", "robot_id": 54}` | 잠금 해제 / 초기화 |
| admin → control | `{"cmd": "admin_goto", "robot_id": 54, "x": 1.2, "y": 0.8, "theta": 0.0}` | IDLE 상태에서 Nav2 직접 목표 |
| control → admin | `{"type": "status", "robot_id": 54, "mode": "TRACKING", "pos_x": 1.2, "pos_y": 0.8, "battery": 72, "is_locked_return": false}` | 1~2Hz push |
| control → admin | `{"type": "staff_call", "robot_id": 54, "event_type": "LOCKED"\|"HALTED", "occurred_at": "..."}` | 직원 호출 이벤트 |
| control → admin | `{"type": "staff_resolved", "robot_id": 54}` | 처리 완료 확인 |
| control → admin | `{"type": "offline", "robot_id": 54}` | 오프라인 감지 |
| control → admin | `{"type": "online", "robot_id": 54}` | 온라인 복귀 |
| control → admin | `{"type": "event", "robot_id": 54, "event_type": "...", "event_detail": "...", "occurred_at": "..."}` | 운용 이벤트 |
| control → admin | `{"type": "admin_goto_rejected", "robot_id": 54}` | admin_goto 거부 (IDLE 아님) |

---

### 채널 C — customer_web ↔ control_service (TCP :8080, JSON 개행 구분)

| 방향 | 메시지 |
|---|---|
| web → control | `{"cmd": "session_check", "robot_id": 54}` |
| web → control | `{"cmd": "login", "robot_id": 54, "user_id": "hong123", "password": "..."}` |
| web → control | `{"cmd": "mode", "robot_id": 54, "value": "WAITING"}` |
| web → control | `{"cmd": "resume_tracking", "robot_id": 54}` |
| web → control | `{"cmd": "return", "robot_id": 54}` |
| web → control | `{"cmd": "navigate_to", "robot_id": 54, "zone_id": 6}` |
| web → control | `{"cmd": "delete_item", "robot_id": 54, "item_id": 3}` |
| web → control | `{"cmd": "process_payment", "robot_id": 54}` |
| control → web | `{"type": "status", "my_robot": {...}, "other_robots": [...]}` | 1~2Hz push |
| control → web | `{"type": "cart", "robot_id": 54, "items": [...]}` |
| control → web | `{"type": "checkout_zone_enter", "robot_id": 54}` |
| control → web | `{"type": "checkout_blocked", "robot_id": 54}` |
| control → web | `{"type": "payment_done", "robot_id": 54}` |
| control → web | `{"type": "arrived", "robot_id": 54, "zone_name": "음료"}` |
| control → web | `{"type": "find_product_result", "robot_id": 54, "zone_id": 6, "zone_name": "음료"}` |
| control → web | `{"type": "nav_failed", "robot_id": 54}` |
| control → web | `{"type": "enter_locked", "robot_id": 54}` |
| control → web | `{"type": "enter_halted", "robot_id": 54}` |
| control → web | `{"type": "staff_resolved", "robot_id": 54}` |

---

### 채널 D — customer_web ↔ LLM (REST HTTP :8000)

customer_web이 LLM Docker 서비스를 직접 호출. 자연어 상품 검색 전용.

| 메서드 | 경로 | 요청 | 응답 |
|---|---|---|---|
| GET | `/query` | `?name=콜라` | `{"zone_id": 3, "zone_name": "음료 코너"}` |

---

### 채널 E — control_service ↔ MySQL DB (TCP :3306)

MySQL 서버 독립 프로세스. `mysql-connector-python`으로 접속.
연결 설정: 환경 변수 `MYSQL_HOST` / `MYSQL_PORT` / `MYSQL_USER` / `MYSQL_PASSWORD` / `MYSQL_DATABASE`

---

### 채널 F — control_service ↔ AI Server YOLO (TCP + UDP 하이브리드)

Pi에서 수신한 카메라 스트림을 YOLO 추론 서버로 전달.

| 방향 | 프로토콜 | 데이터 |
|---|---|---|
| control → YOLO | **UDP** | 원시 영상 프레임 (고용량, 지연 최소화) |
| YOLO → control | **TCP** | `{"cx": 320, "area": 12000, "confidence": 0.92}` (유실 불허) |

---

### 채널 G — control_service ↔ shoppinkki packages (ROS 2 DDS, `ROS_DOMAIN_ID=14`)

**Pi → control_service:**

| 토픽 | 타입 | 페이로드 |
|---|---|---|
| `/robot_<id>/status` | `std_msgs/String` | `{"mode": "TRACKING", "pos_x": 1.2, "pos_y": 0.8, "battery": 72, "is_locked_return": false}` |
| `/robot_<id>/alarm` | `std_msgs/String` | `{"event": "LOCKED"\|"HALTED"}` |
| `/robot_<id>/cart` | `std_msgs/String` | `{"items": [{"id": 1, "name": "콜라", "price": 1500, "is_paid": false}]}` |

**control_service → Pi (`/robot_<id>/cmd`):**

| cmd | 페이로드 | Pi 동작 |
|---|---|---|
| `start_session` | `{"cmd": "start_session", "user_id": "hong123"}` | CHARGING → IDLE |
| `mode` | `{"cmd": "mode", "value": "WAITING"\|"RETURNING"}` | SM 전환 |
| `resume_tracking` | `{"cmd": "resume_tracking"}` | `sm.resume_tracking()` 호출 → TRACKING 또는 TRACKING_CHECKOUT |
| `navigate_to` | `{"cmd": "navigate_to", "zone_id": 6, "x": 1.2, "y": 0.8, "theta": 0.0}` | SM → GUIDING + Nav2 Goal |
| `payment_success` | `{"cmd": "payment_success"}` | `sm.trigger('enter_tracking_checkout')` + `mark_items_paid()` |
| `delete_item` | `{"cmd": "delete_item", "item_id": 3}` | CART_ITEM 삭제 |
| `force_terminate` | `{"cmd": "force_terminate"}` | 세션 종료 → CHARGING |
| `staff_resolved` | `{"cmd": "staff_resolved"}` | `is_locked_return=False` + 세션 종료 → CHARGING |
| `admin_goto` | `{"cmd": "admin_goto", "x": 1.2, "y": 0.8, "theta": 0.0}` | IDLE 상태에서 Nav2 직접 목표 전송 |

---

### 채널 H — control_service ↔ pinky_pro packages (ROS 2 + UDP)

| 방향 | 프로토콜 | 데이터 |
|---|---|---|
| control → pinky | ROS 2 DDS | `/cmd_vel` (`geometry_msgs/Twist`) — 모터 속도 명령 |
| pinky → control | ROS 2 DDS | `/odom`, `/scan`, `/amcl_pose` — 오도메트리, LiDAR, AMCL |
| pinky → control | **UDP** | 원시 카메라 프레임 — 채널 F로 전달 |

---

## 3. REST API (control_service :8080)

customer_web과 Nav2 BT가 control_service에 질의하는 내부 API.

| 메서드 | 경로 | 응답 | 설명 |
|---|---|---|---|
| GET | `/zone/<zone_id>/waypoint` | `{"x": 1.2, "y": 0.8, "theta": 0.0}` | Nav2 목표 좌표 조회 |
| GET | `/zone/parking/available` | `{"zone_id": 140}` | 비어 있는 충전소 슬롯(140 / 141) 1개 반환 |
| GET | `/boundary` | `{"shop_boundary": {...}, "payment_zone": {...}}` | BOUNDARY_CONFIG 전체 |
| GET | `/events?robot_id=<id>&limit=<n>` | `[{"log_id":1, "event_type":"SESSION_START", ...}]` | EVENT_LOG 조회 |
| POST | `/session` | `{"session_id": "..."}` | 세션 생성 |
| GET | `/session/<session_id>` | `{"is_active": true, "expires_at": "..."}` | 세션 유효성 확인 |
| PATCH | `/session/<session_id>` | `{"ok": true}` | 세션 종료 (`is_active=false`) |
| POST | `/cart/<session_id>/item` | `{"item_id": 5}` | CART_ITEM 추가 |
| DELETE | `/cart/<session_id>/item/<item_id>` | `{"ok": true}` | CART_ITEM 삭제 |
| PATCH | `/cart/<session_id>/items/mark_paid` | `{"ok": true}` | `is_paid=0` 전체 → 1 (결제 완료) |
| GET | `/cart/<session_id>/has_unpaid` | `{"has_unpaid": true}` | 미결제 항목 존재 여부 |

> **`/zone/parking/available`:** ROBOT 테이블에서 `current_mode != 'OFFLINE'`이고 `pos_x`, `pos_y`가 슬롯 140/141 waypoint 반경 이내인 로봇 수를 확인하여 빈 슬롯 ID를 반환. 두 슬롯 모두 사용 중이면 140 반환(대기).
