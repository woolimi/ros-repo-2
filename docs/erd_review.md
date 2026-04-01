# ERD 검토 결과

> 검토일: 2026-04-01
> 검토 대상: `docs/erd.md`

---

## 버그 수준 — 구현 전 반드시 수정

### 1. ROBOT 테이블에 `active_user_id` 컬럼 누락

- **위치:** `erd.md` ROBOT 엔티티 상세 테이블
- **문제:** `active_user_id` 컬럼이 엔티티 상세 테이블과 Mermaid ERD 양쪽 모두 정의되어 있지 않음
- **근거:** CLAUDE.md 및 Mermaid 주석(`"현재 활성 세션 user_id. NULL이면 빈 카트 (SR-19 중복 체크용)"`)에 존재한다고 명시되어 있음
- **수정:** ROBOT 엔티티 상세에 아래 컬럼 추가
  ```
  | active_user_id | STRING | 현재 세션 user_id. NULL이면 빈 카트 (SR-19 중복 체크) |
  ```

### 2. `EVENT_LOG`가 저장 위치 구분 표에서 누락

- **위치:** `erd.md` 상단 "저장 위치 구분" 테이블
- **문제:** `EVENT_LOG`가 표에 없음 → 중앙 서버 DB인지 Pi 5 로컬 DB인지 명시 안 됨
- **수정:** 아래 행 추가
  ```
  | EVENT_LOG | 중앙 서버 DB | scenario_17 — 운용 이벤트 타임라인 |
  ```

### 3. ROBOT 설명에 통신 채널 오기재

- **위치:** `erd.md` ROBOT 엔티티 상세 설명
- **문제:** "Pi 5가 **WebSocket**으로 1~2Hz 주기 갱신"이라고 되어 있음
- **실제:** ROS DDS (채널 C, `/robot_<id>/status` 토픽)로 통신. WebSocket은 customer_web ↔ 브라우저 구간(채널 A)
- **수정:** "Pi 5가 **ROS DDS (채널 C, `/robot_<id>/status`)** 로 1~2Hz 주기 갱신"으로 변경

---

## 설계 모호 — 정책 명시 또는 구조 개선 검토

### 4. `SESSION.is_active` vs `expires_at` 이중 관리

- **문제:** 두 컬럼이 모두 세션 유효성 판단에 쓰이는데, 불일치 케이스 처리가 정의되어 있지 않음
  - `expires_at` 초과인데 `is_active = true`인 경우 어떻게 처리?
  - 어느 컬럼을 우선하는가?
- **권장 방향:** `expires_at`은 자동 만료 판단, `is_active`는 명시적 종료(세션 강제 종료, 로그아웃) 전용 플래그로 역할을 분리하고 주석에 명시
  - 유효 조건: `is_active = true AND expires_at > now()`

### 5. `CART_ITEM.price` 출처 취약

- **문제:** `PRODUCT` 테이블에 `price`가 없고, QR 코드에서 디코딩한 값을 그대로 저장함
  - QR 코드 생성 주체가 가격을 임의로 조작할 수 있음
- **데모 수준이면:** 현재 구조 유지하되 주석에 "데모용, 실서비스 시 PRODUCT.price 참조 필요" 명시
- **개선 방향:** PRODUCT 테이블에 `price INT` 추가 → QR 스캔 시 `product_name`만 읽고 서버에서 JOIN으로 가격 조회

### 6. `ALARM_LOG.user_id`가 Mermaid에 FK 미표시

- **문제:** 엔티티 상세에는 `FK → USER`로 명시되어 있으나, Mermaid 다이어그램에 관계선과 컬럼 FK 표시가 없음
- **수정:** Mermaid ALARM_LOG 엔티티에 `string user_id FK` 추가 및 관계선 `USER ||--o{ ALARM_LOG` 추가 (이미 있긴 하나 컬럼 정의와 불일치)

---

## 잘 된 부분

- Cross-DB 논리적 참조를 물리적 FK와 명확히 구분한 것
- `ALARM_LOG`(원본)와 `EVENT_LOG`(타임라인 요약)의 역할 분리 명시
- `POSE_DATA` 세션 종료 시 삭제 정책 명시
- `PRODUCT.zone_id`가 특수 구역(ID 100~)을 참조하면 안 된다는 운영 규칙 명시

---

## 수정 체크리스트

- [ ] ROBOT 엔티티 상세에 `active_user_id` 컬럼 추가
- [ ] ROBOT 엔티티 상세에 `active_user_id` Mermaid ERD에도 추가
- [ ] 저장 위치 구분 표에 `EVENT_LOG` 행 추가
- [ ] ROBOT 설명 "WebSocket" → "ROS DDS (채널 C)" 수정
- [ ] SESSION `is_active`와 `expires_at` 우선순위 정책 주석 추가
- [ ] `CART_ITEM.price` 출처 정책 명시 (데모 수준 명시 또는 PRODUCT.price 추가)
- [ ] Mermaid ERD ALARM_LOG에 `user_id FK` 컬럼 추가
