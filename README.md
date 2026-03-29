# 쑈삥끼 (ShopPinkki)

> **에드인에듀 자율주행 프로젝트 2팀 | 팀명: 삥끼랩**

Pinky Pro 로봇을 활용한 미니어처 마트 스마트 카트 데모 프로젝트.
고객이 QR 코드로 로봇을 등록하면, 쑈삥끼가 마트 안에서 고객을 인식하고 졸졸 따라다니며 쇼핑을 보조합니다.

---

## 프로젝트 컨텍스트

| 항목 | 내용 |
|---|---|
| 팀명 | 삥끼랩 |
| 프로젝트명 | 쑈삥끼 (ShopPinkki) |
| 소속 | 에드인에듀 자율주행 프로젝트 2팀 |
| 로봇 플랫폼 | [Pinky Pro](https://pinklab.art/pinky-pro/) (by Pinklab) |
| 보유 로봇 | 2대 — Pinky #54 (`192.168.x.54`), Pinky #18 (`192.168.x.18`) |
| 데모 맵 크기 | 1.4 × 1.8 m (미니어처 마트) |
| 로봇 크기 | W 110 × D 120 × H 142 mm |
| ROS 버전 | ROS 2 Jazzy |
| OS | Ubuntu 24.04 |

로봇 크기 제약(110 × 120 × 142 mm)으로 인해 실제 마트를 축소한 미니어처 맵 환경에서 데모합니다.

---

## 핵심 기능 (User Requirements 요약)

전체 요구사항은 [`docs/user_requirements.md`](docs/user_requirements.md)를 참조하세요.

- **주인 등록**: LCD QR 코드 → 웹앱 연결 → 최초 사용 시 주인 등록
- **주인 추적**: 등록 후 주인를 인식해 마트 안에서 졸졸 따라다님
- **대기 모드**: 주인를 놓치거나 앱에서 직접 대기 모드 전환 가능. 장시간 미귀환 시 직원 호출
- **앱 연동**: 웹앱으로 마트 맵 + 로봇 위치 확인, 모드 전환
- **도난 감지**: 마트 구역 이탈 시 직원 호출
- **쇼핑 리스트**: 장바구니 물건 목록 관리. 결제 구역 진입 시 자동 결제 (데모용 가상 결제, 실 API 연동 없음)
- **물건 찾기**: 웹앱에서 텍스트 입력 또는 STT(음성→텍스트)로 물건 위치 질의 → 로봇이 해당 진열대로 안내
- **자동 귀환**: 사용 종료 시 카트 대기 구역으로 복귀. 배터리 부족 시 직원 호출

---

## 시스템 아키텍처

각 로봇(Pi 5)이 주인 인식부터 모터 제어, 주인용 웹앱까지 자체적으로 처리하는 **자립형 구조**입니다.
중앙 서버(노트북)는 AI 연산에 관여하지 않고, 전체 로봇의 상태/위치를 집계해 관제하는 역할만 담당합니다.

```
┌──────────────────────────────────────────────────────┐
│                  Raspberry Pi 5 (로봇)                 │
│                                                      │
│  카메라 (5MP)                                         │
│      ↓                                               │
│  주인 인식 (YOLOv8n + ReID)  ──▶  모터 제어 (/cmd_vel) │
│                                                      │
│  주인용 웹앱 (Flask)          ──▶  LCD 상태 표시        │
│  - 주인 등록 / 모드 전환                                │
│  - 장바구니 관리 / 결제                                 │
│  - 지도 + 로봇 위치 확인                                │
│                                                      │
│  상태/위치 WebSocket  ──────────────────────────────────────▶  중앙 서버
└──────────────────────────────────────────────────────┘             │
                                                                      ▼
                                               ┌──────────────────────────────┐
                                               │    노트북 (중앙 관제 서버)     │
                                               │                              │
                                               │  관제 대시보드 웹앱            │
                                               │  - 전체 로봇 맵 + 위치 표시   │
                                               │  - 동작 모드 현황              │
                                               │  - 알람 / 이벤트 로그          │
                                               └──────────────────────────────┘
                                                              ▲
                                                    직원 브라우저 접속
```

> **참고:** `src/shoppinkki/`의 현재 코드는 YOLOv8 + ReID 동작 검증용 테스트 코드입니다. 실제 구현과 무관합니다.

---

## 패키지 구성

### `src/shoppinkki/` — 쑈삥끼 서비스 패키지

> 패키지 구조는 구현 단계에서 확정 예정. 아래는 계획 기준.

| 패키지 (예정) | 실행 위치 | 역할 |
|---|---|---|
| 주인 인식 모듈 | Raspberry Pi 5 | YOLOv8n + ReID 기반 주인 탐지 및 추적 |
| 모터 제어 | Raspberry Pi 5 | 주인 위치 기반 P-제어, 모드별 주행 |
| 주인용 웹앱 | Raspberry Pi 5 | 주인 등록 / 모드 전환 / 장바구니 / 지도 |
| 관제 대시보드 | 노트북 (중앙 서버) | 전체 로봇 상태/위치 맵 표시 + 알람/로그 |

### `src/pinky_pro/` — Pinky Pro 플랫폼 패키지

| 패키지 | 역할 |
|---|---|
| `pinky_bringup` | 하드웨어 초기화 (Dynamixel XL330, 배터리, 센서) |
| `pinky_description` | URDF/XACRO 로봇 모델 |
| `pinky_navigation` | SLAM(slam_toolbox) + 자율주행(Nav2) |
| `pinky_gz_sim` | Gazebo 시뮬레이션 (쇼핑몰 월드 포함) |
| `pinky_emotion` | LCD 감정 표현 (GIF 재생) |
| `pinky_interfaces` | 커스텀 서비스 정의 (Emotion, SetLamp, SetLed 등) |
| `pinky_lamp_control` | 상단 램프 제어 |
| `pinky_led` | WS2812B LED 제어 |
| `pinky_imu_bno055` | BNO055 9축 IMU 드라이버 |

---

## ROS2 토픽 그래프

> 실제 토픽 설계는 구현 단계에서 확정 예정. 아래는 계획 기준.

| 토픽 | 타입 | 설명 |
|---|---|---|
| `/pinky/camera/compressed` | `sensor_msgs/CompressedImage` | 카메라 프레임 (Pi 내부) |
| `/pinky/target_position` | `geometry_msgs/Point` | 주인 위치 좌표 (인식 모듈 → 모터 제어) |
| `/pinky/mode` | `std_msgs/String` | 현재 동작 모드 |
| `/pinky/pose` | `geometry_msgs/PoseWithCovarianceStamped` | 로봇 위치 (Nav2 AMCL) |
| `/cmd_vel` | `geometry_msgs/Twist` | 모터 주행 명령 |

---

## 관련 문서

| 문서 | 내용 |
|---|---|
| [`docs/user_requirements.md`](docs/user_requirements.md) | 사용자 요구사항 (UR 테이블) |
| [`docs/system_requirements.md`](docs/system_requirements.md) | 시스템 요구사항 (SR 테이블) |
| [`docs/pinky_pro_spec.md`](docs/pinky_pro_spec.md) | Pinky Pro 하드웨어/소프트웨어 스펙 |
| [`docs/map.md`](docs/map.md) | 미니어처 마트 맵 레이아웃 및 구역 정의 |
| [`docs/erd.md`](docs/erd.md) | ERD — 중앙 서버 / Pi 5 로컬 DB 엔티티 정의 |
| [`docs/state_machine.md`](docs/state_machine.md) | 로봇 동작 모드 State Machine — 상태/전환 정의 |
| [`cheatsheet.md`](cheatsheet.md) | SLAM 맵 생성 및 네비게이션 명령 모음 |
