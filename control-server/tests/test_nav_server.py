"""
test_nav_server.py
==================
AGV 네비게이션 테스트용 PC 서버.

ESP32가 TCP로 연결하면:
  - 키보드로 목적지 입력 → MOVE 명령 전송
  - ESP32에서 도착 보고 수신 → 터미널 출력

실행:
    python3 test_nav_server.py

노드 목록:
    입고장, a01, a02, a03, a04, 출고장
    s05, s06, s07, s11, s12, s13
    r08, r09, r10, r14, r15, r16
"""

import socket
import json
import threading
import sys

HOST = "0.0.0.0"
PORT = 8080

NODES = [
    "입고장", "a01", "a02", "a03", "a04", "출고장",
    "s05", "s06", "s07", "s11", "s12", "s13",
    "r08", "r09", "r10", "r14", "r15", "r16",
]

client_socket = None
client_addr = None


def receive_loop(sock):
    """ESP32에서 오는 메시지를 수신하고 출력한다."""
    buffer = ""
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("\n🔌 ESP32 연결 끊김")
                break
            buffer += data.decode("utf-8", errors="replace")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                msg = json.loads(line)
                status = msg.get("status", "")
                text = msg.get("msg", "")
                node = msg.get("node", "")

                if status == "SUCCESS" and "도착" in text:
                    print(f"\n🎯 [도착 보고] {text} (현재 노드: {node})")
                else:
                    print(f"\n📥 [ESP32] {json.dumps(msg, ensure_ascii=False)}")

                print(">>> ", end="", flush=True)

        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(f"\n❌ 수신 오류: {e}")
            break


def send_move(sock, target_node):
    """MOVE 명령 전송."""
    cmd = {"cmd": "MOVE", "target_node": target_node}
    json_str = json.dumps(cmd, ensure_ascii=False) + "\n"
    sock.sendall(json_str.encode("utf-8"))
    print(f"📤 [전송] MOVE → {target_node}")


def send_stop(sock):
    """STOP 명령 전송."""
    cmd = {"cmd": "STOP"}
    json_str = json.dumps(cmd, ensure_ascii=False) + "\n"
    sock.sendall(json_str.encode("utf-8"))
    print("📤 [전송] STOP")


def main():
    global client_socket, client_addr

    print("=" * 60)
    print("  🧪 AGV 네비게이션 테스트 서버")
    print(f"  대기 중: {HOST}:{PORT}")
    print("=" * 60)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    print("\n⏳ ESP32 연결 대기...\n")

    client_socket, client_addr = server.accept()
    print(f"✅ ESP32 연결됨: {client_addr[0]}:{client_addr[1]}\n")

    # 수신 스레드 시작
    recv_thread = threading.Thread(target=receive_loop, args=(client_socket,), daemon=True)
    recv_thread.start()

    # 사용 가능한 노드 출력
    print("📍 사용 가능한 목적지:")
    for i, name in enumerate(NODES):
        print(f"    {i:2d}. {name}")
    print()
    print("💡 사용법:")
    print("    노드 이름 입력 (예: s11)  → MOVE 명령")
    print("    stop                      → 정지")
    print("    sl                        → 제자리 좌회전 테스트 (1초)")
    print("    sr                        → 제자리 우회전 테스트 (1초)")
    print("    fw                        → 직진 테스트 (1초)")
    print("    q                         → 종료")
    print()

    try:
        while True:
            user_input = input(">>> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("q", "quit", "exit"):
                break

            if user_input.lower() == "stop":
                send_stop(client_socket)
                continue

            # 모터 테스트 명령
            if user_input.lower() == "sl":
                cmd = {"cmd": "SPIN_LEFT"}
                client_socket.sendall((json.dumps(cmd) + "\n").encode())
                print("📤 [전송] SPIN_LEFT (제자리 좌회전 1초)")
                continue

            if user_input.lower() == "sr":
                cmd = {"cmd": "SPIN_RIGHT"}
                client_socket.sendall((json.dumps(cmd) + "\n").encode())
                print("📤 [전송] SPIN_RIGHT (제자리 우회전 1초)")
                continue

            if user_input.lower() == "fw":
                cmd = {"cmd": "FORWARD"}
                client_socket.sendall((json.dumps(cmd) + "\n").encode())
                print("📤 [전송] FORWARD (직진 1초)")
                continue

            # 번호 입력 지원
            if user_input.isdigit():
                idx = int(user_input)
                if 0 <= idx < len(NODES):
                    user_input = NODES[idx]
                else:
                    print(f"❌ 잘못된 번호: {idx}")
                    continue

            # 노드 확인
            if user_input not in NODES:
                print(f"❌ 알 수 없는 노드: {user_input}")
                print(f"   사용 가능: {', '.join(NODES)}")
                continue

            send_move(client_socket, user_input)

    except KeyboardInterrupt:
        print("\n\n🛑 서버 종료")
    finally:
        client_socket.close()
        server.close()


if __name__ == "__main__":
    main()
