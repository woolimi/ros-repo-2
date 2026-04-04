# 시스템 요구사항 (System Requirements)

> **프로젝트:** 쑈삥끼 (ShopPinkki)
> **팀:** 삥끼랩 | 에드인에듀 자율주행 프로젝트 2팀

시스템 요구사항은 사용자 요구사항(UR)을 시스템이 어떻게 구현하는지를 정의합니다.

---

## SR 테이블

### 하드웨어 / 플랫폼

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-01 | 전체 | 로봇은 Raspberry Pi 5 (8GB) 기반 Pinky Pro를 사용한다. |
| SR-02 | UR-21 | 쑈삥끼 LCD(ST7789, 2.4인치)는 터치 입력을 지원하지 않는다. 모든 사용자 조작은 웹앱을 통해 이루어진다. |

### 네트워크

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-03 | 전체 | 모든 Pinky와 중앙 관제 노트북은 동일한 WiFi 네트워크(LAN)에 연결되어야 한다. |
| SR-04 | 전체 | 각 Pinky는 고유한 고정 IP를 가져야 한다. 공유기의 MAC 주소 기반 IP 예약(DHCP 고정 할당)으로 설정한다. (Pinky #54 → `192.168.x.54`, Pinky #18 → `192.168.x.18`) |
| SR-05 | 전체 | Pinky는 AP 모드가 아닌 클라이언트(Station) 모드로 동작하며, 기존 WiFi 네트워크에 접속한다. |

### 계정 및 세션

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-10 | UR-02 | 사용자 계정(ID, 비밀번호, 이름, 전화번호, 카드 정보)은 Control Center DB에 영구 보관된다. Pi 5는 계정 DB를 보유하지 않으며, 로그인 요청을 Control Device로 전달한다. |
| SR-11 | UR-04 | 세션 쿠키가 유효한 경우 QR 재접속 시 로그인 및 인형 등록을 건너뛰고 메인화면으로 이동한다. |
| SR-12 | UR-05 | Control Device는 로그인 요청 처리 시 해당 user_id가 다른 로봇에 이미 활성 세션으로 등록되어 있는지 확인한다. 중복 활성 세션이 존재하면 로그인을 거부한다. |
| SR-13 | UR-43 | 충전소 도착 시(`enter_charging` 전환) Pi 5의 세션을 종료한다. 인형 등록 데이터를 삭제하고 로봇을 CHARGING 상태로 초기화한다. |

### 주인 인형 인식

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-20 | UR-03 | 주인 인형 인식은 Pi 5에서 로컬로 처리한다. 외부 서버 오프로딩 없음. |
| SR-21 | UR-03 | 인형 탐지는 custom-trained YOLOv8n 모델(단일 클래스: 인형)을 사용한다. |
| SR-22 | UR-03 | 주인 재식별(ReID)은 ReID 특징 벡터 + HSV 색상 히스토그램(상/하의 분리) 기반 특징 비교로 수행한다. |
| SR-23 | UR-03 | IDLE 상태 진입 후 카메라로 인형이 최초 감지되면 ReID/색상 템플릿을 등록하고 `enter_tracking` 전환을 수행한다. |

### 상태 머신 (SM)

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-30 | 전체 | 로봇 동작 모드는 9개 상태(CHARGING / IDLE / TRACKING / GUIDING / SEARCHING / WAITING / TRACKING_CHECK_OUT / RETURNING / LOCKED)로 정의된 State Machine으로 관리한다. (`docs/state_machine.md` 참조) |
| SR-31 | UR-14 | TRACKING 상태에서 배터리 잔량이 임계값 이하로 떨어지면 `enter_locked` 전환을 수행하여 LOCKED 상태로 전환한다. 앱과 LCD에 배터리 부족 알림을 표시한다. |
| SR-32 | UR-40 | BoundaryMonitor가 AMCL pose 기준으로 결제 구역(ID 150) 진입을 감지하면 SM 상태는 TRACKING을 유지한 채 앱에 결제 알람 팝업을 전송하고 LCD를 결제 QR 코드 화면으로 전환한다. |
| SR-32a | UR-40a | 결제 미완료 상태에서 BoundaryMonitor가 출구 방향 경계 초과를 감지하면 로봇을 정지시키고 앱에 결제 필요 알림을 표시한다. 결제 완료 후 `enter_tracking_checkout` 전환을 수행하여 출구 통과를 허용한다. |
| SR-32b | UR-40b | TRACKING_CHECK_OUT 상태에서 로봇이 결제 구역 안쪽으로 복귀하면 `enter_tracking` 전환을 수행한다. Cart 테이블에서 이미 결제된 항목(`is_paid=1`)과 미결제 항목(`is_paid=0`)을 구분하여 관리하며, 다음 결제 시 미결제 항목만 결제 대상으로 처리한다. |
| SR-33 | UR-42 | WAITING 상태에서 "보내주기" 명령 수신 시 미결제 항목 없음 → `enter_returning`, 미결제 항목 있음 → `enter_locked` 전환을 수행한다. |
| SR-35 | UR-43 | RETURNING 상태에서 Nav2 Goal 성공(충전소 도착)하면 `enter_charging` 전환을 수행하여 CHARGING 상태로 복귀한다. |
| SR-36 | UR-52 | 관제 강제 종료 명령(`force_terminate`) 수신 시 현재 상태에 관계없이 세션을 종료하고 CHARGING 상태로 초기화한다. |

### 주행 / 네비게이션

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-40 | UR-10 | 주인 추종 주행(TRACKING)은 인식된 인형의 bbox 중심·크기를 기반으로 P-Control을 사용한다. |
| SR-41 | UR-10 | 추종 중 장애물 회피는 RPLiDAR C1 스캔 데이터를 모니터링하여 전방 일정 거리 이내에 장애물 감지 시 속도를 감소하거나 정지하는 반응형 회피 레이어로 처리한다. |
| SR-42 | UR-11 | SEARCHING 상태에서는 제자리에서 일정 각도씩 회전하며 YOLOv8n으로 인형을 탐색한다. 360° 탐색 후에도 찾지 못하면 `enter_waiting` 전환을 수행한다. |
| SR-43 | UR-13 | WAITING 상태에서 RPLiDAR C1으로 근접 통행자를 감지하면 Nav2를 통해 소폭 이동하여 통행로를 확보한다. |
| SR-44 | UR-33, UR-42 | GUIDING / RETURNING 주행은 Nav2 Waypoint Navigation을 사용한다. |

### LED 동작

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-50 | UR-01 | CHARGING 상태에서는 LED를 빨간색(충전 중)으로 표시한다. |
| SR-51 | UR-03 | IDLE 상태(인형 등록 대기)에서는 LED를 파란색 점멸로 표시한다. |
| SR-52 | UR-10 | TRACKING 상태에서는 LED를 초록색으로 표시한다. |
| SR-53 | UR-11 | SEARCHING 상태에서는 LED를 주황색으로 표시한다. |
| SR-54 | UR-12, UR-14 | WAITING 상태에서는 LED를 파란색으로 표시한다. |
| SR-55 | UR-33 | GUIDING 상태에서는 LED를 노란색으로 표시한다. |
| SR-56 | UR-40 | TRACKING_CHECK_OUT 및 LOCKED 상태에서는 LED를 빨간색으로 표시한다. |
| SR-57 | UR-42 | RETURNING 상태에서는 LED를 보라색으로 표시한다. |

### 쇼핑 리스트 / QR 스캔

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-60 | UR-30 | 상품 QR 코드 스캔은 OpenCV `QRCodeDetector`를 사용한다. |
| SR-61 | UR-30 | 상품 QR 코드에는 상품명과 가격 정보가 인코딩된다. |
| SR-62 | UR-30 | 웹앱에서 "물건 추가" 모드를 선택하면 주인 추종을 일시 정지하고 QR 스캔 모드로 전환한다. 스캔 완료 또는 취소 시 추종을 재개한다. |

### 상품 및 구역 데이터

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-70 | UR-32, UR-33 | 상품 구역(ID 1~8) 및 특수 구역(ID 100~)의 Nav2 Waypoint 좌표는 Control Center DB에서 관리한다. |
| SR-71 | UR-32 | 물건 찾기 요청 시 Customer Web이 LLM 서버(AI Server, REST :8000)에 자연어 질의하여 zone_id를 응답받아 앱에 전달한다. |
| SR-72 | UR-33 | 안내 요청(`navigate_to`) 수신 시 Pi 5 BT가 Control Device API에 zone_id를 질의하여 Nav2 Waypoint 좌표를 응답받고 GUIDING 이동을 시작한다. |
| SR-73 | UR-40 | 결제 구역(ID 150) 진입 좌표 임계값은 Control Center DB에서 관리한다. |
| SR-74 | UR-42 | 귀환 목적지는 충전소 Waypoint(CHARGING 위치)를 사용한다. |

### 웹앱 (Customer Web)

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-80 | UR-01 | LCD에 표시되는 QR 코드는 Mini Server(Customer Web) 주소를 인코딩한다. |
| SR-81 | UR-20 | Customer Web은 Control Device와 TCP(채널 C)로 연결하여 로봇 상태(위치, 모드, 배터리 잔량)를 실시간으로 수신하고, 앱에서의 모드 전환 명령도 동일 채널로 전송한다. |
| SR-82 | UR-32 | 웹앱의 물건 찾기 STT 기능은 브라우저 Web Speech API를 사용한다. |
| SR-83 | UR-41 | 결제는 등록된 카드 정보를 기반으로 가상 결제로 처리한다. 실제 결제 API 연동은 없다. |

### 중앙 관제 (Control Center)

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-90 | UR-50 | 관제 대시보드(Admin UI)는 Control Device와 TCP(채널 B)로 연결한다. |
| SR-91 | UR-50 | 각 Pi 5는 Control Device에 위치, 동작 모드, 배터리 잔량을 1~2Hz 주기로 실시간 전송한다. (`/robot_<id>/status` ROS 토픽) |
| SR-92 | UR-50 | 관제 대시보드는 마트 맵 이미지 위에 각 로봇의 실시간 위치를 오버레이하여 표시한다. |
| SR-93 | UR-51 | 배터리 부족 등 이벤트 발생 시 `/robot_<id>/alarm` ROS 토픽으로 Control Device에 즉시 전송하고 로그에 기록한다. |
| SR-94 | UR-52 | 관제 강제 종료는 Admin UI → Control Device(채널 B) → `/robot_<id>/cmd`: `{"cmd": "force_terminate"}` 경로로 전달된다. |

### 배터리

| SR ID | 연관 UR | Description |
|---|---|---|
| SR-95 | UR-14 | 배터리 잔량은 pinkylib API를 통해 주기적으로 읽는다. 잔량이 임계값(기본 20%) 이하로 떨어지면 `enter_locked` 전환을 수행하고 앱·LCD에 배터리 부족 알림을 표시한다. |
