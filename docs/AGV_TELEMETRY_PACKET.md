# 📡 AGV 주행 텔레메트리 패킷 정의서

> ESP32 → 중앙 서버 (TCP), 주기: 1초, Big Endian  
> `logged_at`은 패킷 미포함 → 서버 수신 시점에 기록

---

## AGV 주행 텔레메트리 패킷

| 필드명 | 예시 값 | 크기(B) | 타입 |
|--------|---------|---------|------|
| STX | 0x02 | 1 | UINT8 |
| agv_id | 1 | 2 | UINT16 |
| task_id | 5 | 2 | UINT16 |
| current_status | 0x01 | 1 | UINT8 |
| task_status | 0x01 | 1 | UINT8 |
| CRC-16 | | 2 | UINT16 |
| ETX | 0x03 | 1 | UINT8 |
| **합계** | | **11** | |

---

## current_status 매핑 (agv_robots.current_status)

| 값 | DB ENUM | 설명 |
|----|---------|------|
| 0x00 | IDLE | 대기 |
| 0x01 | MOVING | 이동 중 |
| 0x02 | WORKING | 작업 중 |
| 0x03 | CHARGING | 충전 중 |
| 0x04 | ERROR | 오류 |

---

## task_status 매핑 (transport_tasks.task_status)

| 값 | DB ENUM | 설명 |
|----|---------|------|
| 0x00 | PENDING | 대기 |
| 0x01 | IN_PROGRESS | 진행 중 |
| 0x02 | COMPLETED | 완료 |
| 0x03 | FAILED | 실패 |

---

## agv_id 매핑

| 값 | DB agv_id |
|----|-----------|
| 1 | R01 |
| 2 | R02 |
| 3 | R03 |
