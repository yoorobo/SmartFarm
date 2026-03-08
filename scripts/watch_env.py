#!/usr/bin/env python3
"""
.env 파일의 변경 사항을 실시간으로 감지하여 자동으로 wifi_config.h를 갱신합니다.
사용법: python scripts/watch_env.py
"""
import os
import time
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"
UPDATE_SCRIPT = REPO_ROOT / "scripts" / "update_wifi_config.py"

def main():
    print("👀 ['.env' 자동 갱신 모니터링 시작]")
    print("종료하시려면 Ctrl+C를 누르세요.\n")
    print("이제 .env 파일을 수정하고 저장할 때마다 아두이노용 헤더 파일이 알아서 갱신됩니다.")
    
    last_mtime = 0
    # 스크립트 시작 시 최신 수정 시간으로 초기화 (최초 1회 실행 생략 위함)
    if ENV_PATH.exists():
        last_mtime = os.path.getmtime(ENV_PATH)
        # 시작할 때도 한 번 동기화시켜줍니다.
        subprocess.run(["python3", str(UPDATE_SCRIPT)])
        
    while True:
        try:
            if ENV_PATH.exists():
                current_mtime = os.path.getmtime(ENV_PATH)
                if current_mtime != last_mtime:
                    print(f"\n[{time.strftime('%H:%M:%S')}] .env 변경 감지됨! wifi_config.h 자동 갱신 중...")
                    # 파일이 수정되었으면 업데이트 스크립트 실행
                    subprocess.run(["python3", str(UPDATE_SCRIPT)])
                    last_mtime = current_mtime
            
            time.sleep(1)  # 1초마다 파일 상태 확인
        except KeyboardInterrupt:
            print("\n감지를 종료합니다.")
            break
        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
