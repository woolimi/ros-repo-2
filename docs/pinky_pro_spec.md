# Pinky Pro 하드웨어 스펙

> **제조사:** Pinklab ([pinklab.art/pinky-pro](https://pinklab.art/pinky-pro/))
> **용도:** ROS 2 기반 교육용 소형 이동 로봇

---

## 물리적 사양

| 항목 | 값 |
|---|---|
| 크기 (W × D × H) | 110 × 120 × 142 mm |

---

## 컴퓨팅

| 항목 | 사양 |
|---|---|
| SBC (메인 컴퓨터) | Raspberry Pi 5 (8 GB RAM) |

---

## 센서

| 센서 | 모델 | 설명 |
|---|---|---|
| 카메라 | — | 5 MP |
| LiDAR | SLAMTEC RPLiDAR C1 | 2D 라이다 (SLAM / 장애물 회피) |
| IMU | BNO055 | 9축 (가속도계 + 자이로 + 지자기) |
| 초음파 | US-016 | 근거리 장애물 감지 (보유 로봇에 미장착) |
| IR | TCRT5000 | 바닥 감지 / 라인 트래킹 |

---

## 액추에이터

| 항목 | 모델 | 설명 |
|---|---|---|
| 구동 모터 | Dynamixel XL330-M288-T | TTL 통신, 스마트 서보 (위치 / 속도 / 전류 제어) |

---

## 디스플레이 및 LED

| 항목 | 모델 | 설명 |
|---|---|---|
| LCD | ST7789, 2.4인치 | 감정 표현(GIF), QR 코드, UI 표시 |
| LED | WS2812B | 풀컬러 RGB LED 스트립 |
| 부저 | — | 알림음 출력 |

---

## 전원

| 항목 | 사양 |
|---|---|
| 배터리 종류 | 리튬이온 (Li-ion) |

---

## 소프트웨어 스택

| 항목 | 내용 |
|---|---|
| OS | Ubuntu (ARM64) |
| ROS 버전 | ROS 2 Jazzy |
| 주요 패키지 | `pinky_bringup`, `pinky_description`, `pinky_navigation`, `pinky_gz_sim` 등 |
| 시뮬레이터 | Gazebo (Ignition) |
| SLAM | slam_toolbox |
| 자율주행 | Nav2 |
| 하드웨어 라이브러리 | `pinkylib` (Python — 카메라, 모터, 센서 추상화) |

---

## 쑈삥끼 프로젝트 적용 시 주요 제약

| 제약 | 내용 |
|---|---|
| 로봇 크기 | 110 × 120 × 142 mm → 미니어처 맵(1.4 × 1.8 m)에서 데모 필요 |
| 연산 능력 | Pi 5 단독으로 YOLO 실시간 추론 부담 → PC 오프로딩 구조 채택 |
| 카메라 해상도 | 5 MP / 15 FPS 스트리밍 (네트워크 대역폭 고려 JPEG 압축 적용) |
| 통신 | PC ↔ Pi 동일 LAN + `ROS_DOMAIN_ID=14` 설정 필요 |
