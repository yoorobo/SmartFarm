# 스마트팜 운반차 제어 웹서버

SQLite 데이터베이스와 Flask 웹서버를 이용해 노트북에서 목적지를 입력하면 운반차(ESP32)가 수신해 이동하는 시스템입니다.

## 구조

```
[노트북]                         [ESP32 로봇]
  웹 브라우저 ──→ Flask(5000)       TCP 클라이언트
       │              │                    │
       │         SQLite DB                 │
       │         (목적지 저장)              │
       │              │                    │
       └──────────────┴── TCP(8080) ───────┘
                      GOTO 명령 전송
```

## 실행 방법

### 1. 가상환경 생성 및 의존성 설치

```bash
cd server
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 웹서버 실행

```bash
python app.py
```

- 웹 UI: http://127.0.0.1:5000 (또는 노트북 IP:5000)
- 로봇 TCP: 0.0.0.0:8080

### 3. 로봇 펌웨어 설정

로봇이 **노트북 IP**로 연결해야 합니다. `robot-firmware/robot-firmware.ino`에서 `SERVER_IP`를 노트북 IP로 수정하세요.

```cpp
const char* SERVER_IP   = "192.168.0.xxx";  // 노트북 IP
const uint16_t SERVER_PORT = 8080;
```

노트북 IP 확인:
- Linux: `ip addr` 또는 `hostname -I`
- Windows: `ipconfig`

### 4. 사용 순서

1. 노트북에서 `python app.py` 실행
2. 로봇 전원 켜기 (같은 Wi-Fi에 연결)
3. 브라우저에서 http://노트북IP:5000 접속
4. 목적지(a01, s06 등) 선택 후 "목적지 전송" 클릭
5. 로봇이 해당 노드로 이동

## 데이터베이스 (SQLite)

- 파일: `server/robot_tasks.db`
- 테이블: `tasks` (목적지, 상태, 시간), `task_log` (이벤트 로그)

DB 직접 확인:

```bash
sqlite3 server/robot_tasks.db "SELECT * FROM tasks;"
```

## 목적지 노드

- a01~a04: 메인 라인
- s05~s07, s11~s13: 상부 노드
- r08~r10, r14~r16: 하부 노드
