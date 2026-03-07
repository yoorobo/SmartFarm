#!/usr/bin/env python3
"""
.env 파일을 읽어 config, esp32-cam, robot-firmware 의 wifi_config.h 를 생성합니다.
사용법: python scripts/update_wifi_config.py
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"
CONFIG_PATHS = [
    REPO_ROOT / "config" / "wifi_config.h",
    REPO_ROOT / "esp32-cam" / "wifi_config.h",
    REPO_ROOT / "robot-firmware" / "wifi_config.h",
]


def load_env():
    """Parse .env file (simple KEY=value format)."""
    env = {}
    if not ENV_PATH.exists():
        print(f"[오류] .env 파일이 없습니다. .env.example을 .env로 복사한 뒤 수정하세요.")
        return None
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"\'')
    return env


def generate_header(env):
    ssid = env.get("WIFI_SSID", "YOUR_WIFI_SSID")
    password = env.get("WIFI_PASSWORD", "YOUR_WIFI_PASSWORD")
    server_ip = env.get("SERVER_IP", "192.168.0.xxx")
    return f'''/**
 * wifi_config.h (auto-generated from .env)
 * =============
 * python scripts/update_wifi_config.py 로 생성됨
 */

#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

#define WIFI_SSID     "{ssid}"
#define WIFI_PASSWORD "{password}"
#define SERVER_IP     "{server_ip}"

#define SERVER_TCP_PORT 8080
#define SERVER_UDP_PORT 7070

#endif
'''


def main():
    env = load_env()
    if env is None:
        return 1
    content = generate_header(env)
    for p in CONFIG_PATHS:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    print(f"[완료] 3개 파일 갱신됨 (config, esp32-cam, robot-firmware)")
    return 0


if __name__ == "__main__":
    exit(main())
