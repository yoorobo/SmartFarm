import socket
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from database.db_manager import DatabaseManager
    print("✅ [성공] DatabaseManager를 로드했습니다!")
except ImportError as e:
    print(f"❌ [오류] 모듈 로드 실패: {e}")
    sys.exit(1)

def get_valid_ids(db):
    """DB에서 실제로 존재하는 user_id와 action_type_id 하나씩을 가져옵니다."""
    try:
        # 실제 존재하는 유저 하나 가져오기
        user = db.execute_query("SELECT user_id FROM users LIMIT 1;")
        # 실제 존재하는 액션 타입 하나 가져오기
        action = db.execute_query("SELECT action_type_id FROM action_types LIMIT 1;")
        
        u_id = user[0]['user_id'] if user else 1
        a_id = action[0]['action_type_id'] if action else 1
        return u_id, a_id
    except:
        return 1, 1 # 실패 시 기본값

def start_server():
    db = DatabaseManager()
    db.connect()

    # 1. 헛바퀴 돌지 않게 실제 DB에 있는 '진짜 ID'를 찾아옵니다.
    valid_user_id, valid_action_id = get_valid_ids(db)
    print(f"🔍 [ID 체크] 사용 가능한 ID 선택: user_id={valid_user_id}, action_id={valid_action_id}")

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_sock.bind(('0.0.0.0', 8000))
        server_sock.listen(5)
        print(f"\n🚀 [TCP 서버] 바이너리 대기 중... (Port: 8000)")
    except Exception as e:
        print(f"❌ 서버 바인딩 실패: {e}")
        return

    try:
        while True:
            client_sock, addr = server_sock.accept()
            print(f"\n✅ 로봇 접속: {addr}")
            
            try:
                while True:
                    data = client_sock.recv(1024)
                    if not data: break
                    
                    hex_data = data.hex().upper()
                    print(f"📡 수신(Binary): {hex_data}")
                    
                    # JSON 포맷 준수
                    binary_log = json.dumps({
                        "raw_packet": hex_data,
                        "type": "robot_binary"
                    })
                    
                    # 2. 검증된 ID를 쿼리에 사용
                    query = """
                        INSERT INTO user_action_logs 
                        (user_id, action_type_id, action_detail, action_result) 
                        VALUES (%s, %s, %s, %s)
                    """
                    # action_result도 안전하게 정수 1(성공)로 전달
                    db.execute_update(query, (valid_user_id, valid_action_id, binary_log, 1))
                    
            except Exception as e:
                print(f"⚠️ 에러: {e}")
            finally:
                client_sock.close()
                print("🔌 연결 해제됨.")
                
    except KeyboardInterrupt:
        print("\n🛑 서버 종료")
    finally:
        db.disconnect()
        server_sock.close()

if __name__ == "__main__":
    start_server()