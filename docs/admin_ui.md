# Admin UI 명세

> **기술 스택:** PyQt6 데스크톱 앱. 별도 프로세스 또는 별도 기기에서 실행.
> **통신:** 채널 B (TCP, admin_ui ↔ control_service:8080)
> **실행:** `ros2 run admin_ui admin_ui` 또는 `python3 src/control_center/admin_ui/admin_ui/main.py`

---

## 구현 기능 목록

| # | 기능 | 관련 시나리오 | 트리거 |
|---|---|---|---|
| 1 | 실시간 로봇 모니터링 (카드 + 맵) | S13 | control_service TCP push (1~2Hz) |
| 2 | 로봇 상태 변경 (모드 전환) | S13 | 관제자 상태 버튼 클릭 |
| 3 | 알람 수신 및 해제 | S14 | `/robot_<id>/alarm` 수신 → TCP push |
| 4 | 세션 강제 종료 | S15 | 관제자 [강제 종료] 클릭 |
| 5 | 위치 호출 (admin_goto) | S15 | 맵 클릭 → [이동 명령] |
| 6 | 오프라인 감지 / 재연결 표시 | S16 | cleanup 스레드 → TCP push |
| 7 | 이벤트 로그 패널 | S17 | 모든 운용 이벤트 TCP push |
| 8 | 대기열 상태 표시 | S18 | QueueManager 상태 변경 시 |

---

## 화면 구성

전체 레이아웃은 단일 메인 윈도우(`QMainWindow`)로 구성된다.

```
┌──────────────────────────────────────────────────────────────────┐
│  ShopPinkki 관제 대시보드                            [연결 상태]  │
├──────────────────┬───────────────────────────────────────────────┤
│                  │  로봇 카드 패널                               │
│   맵 오버레이    │  ┌──────────────┐  ┌──────────────┐          │
│   (MapWidget)    │  │  Robot #54   │  │  Robot #18   │          │
│                  │  │  [카드 내용] │  │  [카드 내용] │          │
│                  │  └──────────────┘  └──────────────┘          │
│                  │                                               │
│                  │  대기열 패널                                  │
│                  │  [1번: Robot#54]  [2번: Robot#18]  [3번: -]  │
├──────────────────┴───────────────────────────────────────────────┤
│  알람 패널                    │  이벤트 로그 패널                 │
│  [알람 목록]                  │  [전체] [알람] [세션] [대기열]    │
│                               │  [이벤트 로그 목록]               │
└───────────────────────────────┴──────────────────────────────────┘
```

---

### 1. 맵 오버레이 (`MapWidget`)

**역할:** `shop_map.png` 위에 로봇 위치 실시간 표시. 맵 클릭으로 위치 호출 좌표 선택.

**UI 요소:**
- 맵 이미지 (QLabel + QPixmap)
- 로봇 아이콘 (robot_id별 색상 구분, yaw 방향 표시)
  - 온라인: 색상 원형 아이콘
  - 오프라인: × 표시, 마지막 위치 유지
- 맵 클릭 시 목표 마커 (파란 십자+원) 표시 → 이동 명령 전송 후 제거

**좌표 변환:**
```python
# 월드 좌표 → 픽셀
px = int((x - origin_x) / resolution)
py = int(img_height - (y - origin_y) / resolution)  # y축 반전

# 픽셀 → 월드 좌표 (맵 클릭)
x = px * resolution + origin_x
y = (img_height - py) * resolution + origin_y
```

---

### 2. 로봇 카드 패널

**역할:** 각 로봇(#54, #18)의 현재 상태를 1~2Hz로 갱신하고, 관제자가 상태를 직접 변경할 수 있다.

**카드 구성 (로봇 1개당):**

```
┌──────────────────────────────────┐
│  Robot #54              [TRACKING]│  ← 모드 뱃지 (색상 구분)
│  👤 hong123                      │  ← 활성 사용자 ID (없으면 "-")
│  🔋 [████████░░] 72%             │  ← 배터리 바 (20% 이하 → 빨강)
│  📍 (1.20, 0.80)                 │  ← 좌표
│  ─────────────────────────────── │
│  상태 전환                        │
│  [대기]  [추종]  [복귀]           │  ← 현재 상태에 따라 활성/비활성
│  ─────────────────────────────── │
│  관제 명령                        │
│  [강제 종료]       [이동 명령]    │
└──────────────────────────────────┘
```

**모드 뱃지 색상:**

| 모드 | 색상 |
|---|---|
| IDLE | 회색 |
| REGISTERING | 파랑 |
| TRACKING | 초록 |
| SEARCHING | 노랑 |
| WAITING | 하늘 |
| GUIDING | 초록 |
| CHECK_OUT | 보라 |
| RETURNING | 주황 |
| TOWARD_STANDBY_1/2/3 | 주황 |
| STANDBY_1/2/3 | 하늘 |
| ALARM | 빨강 |
| OFFLINE | 회색 (카드 전체 회색 처리) |

**상태 전환 버튼 — 현재 모드별 활성화 규칙:**

| 버튼 | 전송 명령 | 활성 조건 |
|---|---|---|
| [대기] | `{"cmd": "mode", "value": "WAITING"}` | TRACKING, SEARCHING |
| [추종] | `{"cmd": "mode", "value": "TRACKING"}` | WAITING, SEARCHING |
| [복귀] | `{"cmd": "mode", "value": "RETURNING"}` | TRACKING, WAITING, SEARCHING, CHECK_OUT |

> control_service는 `mode` 명령을 `/robot_<id>/cmd`로 그대로 relay한다.

**관제 명령 버튼:**
- **[강제 종료]** — 확인 다이얼로그 후 `{"cmd": "force_terminate", "robot_id": N}` 전송. IDLE·OFFLINE 상태에서는 비활성화.
- **[이동 명령]** — 맵에서 위치 클릭 후 활성화 → `{"cmd": "admin_goto", "robot_id": N, "x": x, "y": y, "theta": 0.0}` 전송. IDLE 상태에서만 활성화.
  - 거부 응답(`admin_goto_rejected`) 수신 시 오류 토스트 표시.

---

### 3. 알람 패널

**역할:** 로봇 알람 이벤트 수신 시 표시. 관제자가 [해제] 버튼으로 처리.

**패널 구성:**

```
┌──────────────────────────────────────┐
│  🚨 알람                              │
│  ┌───────────────────────────────┐   │
│  │ Robot#54  THEFT  12:34:05 [해제]│  ← 빨강
│  ├───────────────────────────────┤   │
│  │ Robot#18  BATTERY_LOW  12:30  │   │  ← 노랑
│  │ ✓ 처리됨                      │   │
│  └───────────────────────────────┘   │
└──────────────────────────────────────┘
```

**알람 항목 색상:**

| event_type | 색상 | 해제 후 Pi 복귀 |
|---|---|---|
| THEFT | 빨강 | IDLE (세션 종료) |
| BATTERY_LOW | 노랑 | WAITING |
| TIMEOUT | 주황 | WAITING |
| PAYMENT_ERROR | 보라 | WAITING |

**동작:**
- TCP `{"type": "alarm", ...}` 수신 → 항목 추가 + 해당 로봇 카드 빨간 테두리
- [해제] 클릭 → `{"cmd": "dismiss_alarm", "robot_id": N}` 전송
- TCP `{"type": "alarm_dismissed", ...}` 수신 → 항목 "✓ 처리됨" 회색 처리 + 카드 테두리 복구
- 다중 알람: 독립 항목으로 각각 표시/해제 가능

---

### 4. 대기열 패널

**역할:** STANDBY 구역(zone 140/141/142)에 대기 중인 로봇 현황 표시.

**패널 구성:**

```
┌─────────────────────────────────────────────┐
│  대기열 현황                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────┐ │
│  │ 1번 위치   │  │ 2번 위치   │  │ 3번    │ │
│  │ Robot #54  │  │ Robot #18  │  │ 비어있음│ │
│  └────────────┘  └────────────┘  └────────┘ │
└─────────────────────────────────────────────┘
```

- 로봇이 있는 슬롯: `Robot #N` 표시, 파란 배경
- 비어있는 슬롯: "비어있음", 점선 박스
- TCP `{"type": "queue_update", "queue": [54, 18]}` 수신 시 갱신

---

### 5. 이벤트 로그 패널

**역할:** 운용 중 발생한 모든 이벤트 실시간 표시. 최신 이벤트가 상단.

**패널 구성:**

```
┌──────────────────────────────────────────────┐
│  이벤트 로그   [전체] [알람] [세션] [대기열]  │
├──────────────────────────────────────────────┤
│ [12:35:01] Robot#54  SESSION_START | hong123 │  ← 초록
│ [12:34:05] Robot#54  ALARM_RAISED  | THEFT   │  ← 빨강
│ [12:30:00] Robot#18  QUEUE_ADVANCE           │  ← 하늘
│ [12:20:00] Robot#54  OFFLINE                 │  ← 회색
│ ...                                          │
└──────────────────────────────────────────────┘
```

**이벤트 색상:**

| event_type | 배경색 |
|---|---|
| SESSION_START | `#d4edda` (초록) |
| SESSION_END | `#cce5ff` (파랑) |
| FORCE_TERMINATE | `#fff3cd` (노랑) |
| ALARM_RAISED | `#f8d7da` (빨강) |
| ALARM_DISMISSED | `#e2e3e5` (회색) |
| PAYMENT_SUCCESS | `#d4edda` (초록) |
| PAYMENT_FAIL | `#f8d7da` (빨강) |
| OFFLINE | `#888888` (회색) |
| ONLINE | `#d4edda` (초록) |
| QUEUE_ADVANCE | `#e8f4f8` (하늘) |

**동작:**
- TCP `{"type": "event", ...}` 수신 → 최상단에 행 추가
- 필터 버튼: [전체] / [알람] (ALARM_*) / [세션] (SESSION_*, FORCE_TERMINATE) / [대기열] (QUEUE_*)
- 최대 200건 유지. 행 클릭 시 해당 robot_id 카드 하이라이트.

---

## TCP 메시지 요약

### 수신 (control_service → admin_ui)

| type | 처리 |
|---|---|
| `status` | 로봇 카드 갱신 (모드·배터리·좌표), 맵 오버레이 위치 갱신, 상태 버튼 활성화 재계산 |
| `alarm` | 알람 패널 항목 추가, 로봇 카드 빨간 테두리 |
| `alarm_dismissed` | 알람 항목 "처리됨", 카드 테두리 복구 |
| `offline` | 카드 전체 회색, "오프라인" 뱃지, 맵 아이콘 × |
| `online` | 카드 정상 복구, 맵 아이콘 정상 |
| `event` | 이벤트 로그 패널 상단에 행 추가 |
| `queue_update` | 대기열 슬롯 갱신 |
| `admin_goto_rejected` | 오류 토스트 메시지 표시 |

### 송신 (admin_ui → control_service)

| 명령 | 페이로드 | 조건 |
|---|---|---|
| 모드 전환 | `{"cmd": "mode", "robot_id": N, "value": "WAITING"\|"TRACKING"\|"RETURNING"}` | 상태별 활성 조건 참고 |
| 강제 종료 | `{"cmd": "force_terminate", "robot_id": N}` | IDLE·OFFLINE 제외 |
| 위치 호출 | `{"cmd": "admin_goto", "robot_id": N, "x": x, "y": y, "theta": 0.0}` | IDLE만 |
| 알람 해제 | `{"cmd": "dismiss_alarm", "robot_id": N}` | ALARM 상태 |

> 모든 TCP 수신은 별도 스레드에서 처리 후 `pyqtSignal.emit()`으로 Qt 메인 스레드에 전달.

> 모든 TCP 수신은 별도 스레드에서 처리 후 `pyqtSignal.emit()`으로 Qt 메인 스레드에 전달.

---

## 유저 플로우

```
[admin_ui 기동]
    → TCP 연결: control_service:8080
    → 맵 이미지 로드, 로봇 카드 초기화, DB 이벤트 초기 50건 로드
        ↓
[실시간 모니터링]
    → 로봇 카드 / 맵 오버레이 1~2Hz 자동 갱신
    → 배터리 20% 이하 → 빨간 강조
    → 30s 무응답 → "오프라인" 뱃지 (cleanup 스레드)

[알람 수신 시]
    → 알람 패널 항목 추가 + 로봇 카드 빨간 테두리
    → [해제] 클릭 → control_service → Pi dismiss_alarm 전달
    → 알람 "처리됨" 표시 + 카드 복구

[상태 변경]
    → [대기] 클릭 (TRACKING/SEARCHING) → WAITING 전환
    → [추종] 클릭 (WAITING/SEARCHING) → TRACKING 전환
    → [복귀] 클릭 (TRACKING/WAITING/SEARCHING/CHECK_OUT) → RETURNING 전환
    → control_service가 /robot_<id>/cmd 로 relay → Pi SM 전환
    → status push 수신 → 카드 모드 뱃지 + 버튼 활성화 자동 갱신

[세션 강제 종료]
    → 로봇 카드 [강제 종료] 클릭 (IDLE 아닐 때 활성)
    → 확인 다이얼로그
    → control_service → Pi force_terminate 전달
    → 로봇 IDLE 복귀 (status push로 카드 갱신)

[위치 호출]
    → 로봇이 IDLE 상태일 때 맵 클릭 → 목표 마커 표시
    → [이동 명령] 클릭
    → control_service → Pi admin_goto 전달
    → 이동 완료(IDLE status 수신) → 목표 마커 제거

[이벤트 로그 조회]
    → 필터 버튼으로 이벤트 유형 필터링
    → 행 클릭 시 해당 로봇 카드 하이라이트
```
