import socket
import time

def start_robot():
    # 서버 주소 (우리 서버는 로컬 8000번 포트에서 대기 중)
    server_ip = '127.0.0.1'
    server_port = 8000

    try:
        robot_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        robot_sock.connect((server_ip, server_port))
        print("🤖 로봇: 서버에 연결되었습니다!")

        # 테스트용 로봇 데이터 전송 (5번 반복)
        for i in range(5):
            test_data = bytes([0x02, 0x01, 0x00, 0x10, i, 0x03]) # 가짜 센서 데이터
            robot_sock.send(test_data)
            print(f"📡 로봇 -> 서버 데이터 전송: {test_data.hex().upper()}")
            time.sleep(2) # 2초 간격

    except Exception as e:
        print(f"❌ 로봇 에러: {e}")
    finally:
        robot_sock.close()
        print("🔌 로봇 연결 종료")

if __name__ == "__main__":
    start_robot()