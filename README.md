# 🌱 통합 스마트팜 자동화 시스템

> IoT 프로젝트 4조 저장소 – 스마트팜

## 프로젝트 개요

육묘(모종 재배) 환경을 자동으로 제어하고, 무인 이송 로봇으로 작물을 운반하며, 관리자 대시보드를 통해 전체 시스템을 실시간으로 관제하는 **통합 스마트팜 자동화 시스템**입니다.

## 프로젝트 구조

```
iot-repo-4/
├── .env                     # Wi-Fi, 서버 IP (git 제외, .env.example 복사 후 수정)
├── .env.example             # 설정 템플릿
├── config/
│   ├── wifi_config.h        # (git 제외) .env에서 생성
│   └── wifi_config.h.example # 템플릿
├── scripts/
│   └── update_wifi_config.py # .env → wifi_config.h 변환
│
├── server/                  # Flask 웹서버 + 로봇 TCP 브로커 (운반차 제어)
│   ├── app.py               # Flask 진입점 (웹 UI 5000, TCP 8080)
│   ├── run.sh               # 서버 실행 스크립트 (venv 자동 설정)
│   ├── db.py                # SQLite DB 관리
│   ├── templates/
│   └── requirements.txt
│
├── control-server/          # Python 기반 중앙 제어 서버 (DB 연동, 통신)
│   ├── database/
│   │   ├── __init__.py
│   │   └── db_manager.py    # DatabaseManager 클래스 (pymysql)
│   ├── __init__.py
│   ├── main_server.py       # 서버 진입점 (Entry Point)
│   └── requirements.txt
│
├── main-gui/                # Python + PyQt 관리자 관제 대시보드
│   └── README.md
│
├── robot-firmware/          # 무인 이송 시스템 ESP32 펌웨어 (C++)
│   ├── robot-firmware.ino
│   └── src/
│
├── esp32-cam/               # ESP32-CAM WiFi 웹캠 펌웨어 (UDP 스트리밍)
│   └── esp32-cam.ino
│
├── farm-firmware/           # 육묘 시스템 환경 제어 ESP32 펌웨어 (C++)
│   └── README.md
│
└── README.md
```

## 기술 스택

| 모듈 | 언어 / 프레임워크 | 역할 |
|------|-------------------|------|
| control-server | Python, pymysql | 중앙 제어 서버, AWS EC2 MySQL DB 연동 |
| main-gui | Python, PyQt | 관리자 관제 대시보드 |
| robot-firmware | C++ (ESP32, ESP32 CAM) | 무인 이송 시스템 펌웨어 |
| farm-firmware | C++ (ESP32) | 육묘 환경 제어 펌웨어 |

## 서버 실행 방법

### 1. 스마트팜 운반차 제어 서버 (`server/`)

Flask 웹서버 + 로봇 TCP 브로커. 웹 UI에서 목적지를 입력하면 ESP32 로봇에 GOTO 명령을 전송합니다.

**방법 A: run.sh 사용 (권장)**

```bash
cd server
./run.sh
```

`run.sh`가 가상환경(venv)이 없으면 생성하고, 의존성을 설치한 뒤 서버를 실행합니다.

**방법 B: 수동 실행**

```bash
cd server
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

- **웹 UI** (또는 노트북 IP:5000)
- **로봇 TCP**: 0.0.0.0:8080

### Wi-Fi / 서버 IP 설정 (.env)

`.env`에서 Wi-Fi SSID, 비밀번호, 서버 IP를 관리합니다. **wifi_config.h는 .gitignore**되어 비밀정보가 저장소에 올라가지 않습니다.

```bash
# 최초: .env.example을 .env로 복사 후 편집
cp .env.example .env
# .env 수정 (WIFI_SSID, WIFI_PASSWORD, SERVER_IP)
# 스크립트 실행 → config, esp32-cam, robot-firmware 에 wifi_config.h 생성
python3 scripts/update_wifi_config.py
```

`.env` 예시:
```
WIFI_SSID=YOUR_WIFI_SSID
WIFI_PASSWORD=YOUR_WIFI_PASSWORD
SERVER_IP=192.168.0.xxx
```

