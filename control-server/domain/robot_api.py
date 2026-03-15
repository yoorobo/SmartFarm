"""
로봇 제어 API 모듈
- 개별 로봇 제어, 비상 정지, GOTO/MOVE 명령 전송
- [추가] 액추에이터(PUMP, FAN, LED, MODE) 바이너리 제어 인터페이스 통합
"""
import json
from flask import Blueprint, request, jsonify
from datetime import datetime
from network.tcp_robot_server import active_tcp_connections, latest_robot_state
# 프로토콜 정의 파일에서 필요한 상수 및 함수 임포트
from network.sfam_protocol import (
    build_actuator_packet, ACT_ID_MODE, ACT_ID_PUMP, 
    ACT_ID_FAN, ACT_ID_HEATER, ACT_ID_LED, ID_SERVER
)

robot_bp = Blueprint('robot', __name__)

# 로봇이 인식 가능한 목적지 노드 목록 (PathFinder 기준)
VALID_NODES = [
    "a01", "a02", "a03", "a04",
    "s05", "s06", "s07",
    "r08", "r09", "r10",
    "s11", "s12", "s13",
    "r14", "r15", "r16",
]

# --- [도움 함수] 전송 로직 분리 ---

def send_to_robot(robot_id, cmd):
    """로봇에게 JSON 명령 전송 (기존 JSON 방식)"""
    payload = json.dumps(cmd) + "\n"
    if robot_id and robot_id in active_tcp_connections:
        sock = active_tcp_connections[robot_id]
    elif active_tcp_connections:
        robot_id = next(iter(active_tcp_connections.keys()))
        sock = active_tcp_connections[robot_id]
    else:
        return False

    try:
        sock.sendall(payload.encode("utf-8"))
        print(f"📤 [TCP JSON 전송] {robot_id} → {cmd}")
        return True
    except Exception as e:
        print(f"❌ [TCP 전송 실패] {robot_id}: {e}")
        if robot_id in active_tcp_connections:
            del active_tcp_connections[robot_id]
        return False

def send_binary_to_robot(robot_id, packet):
    """로봇에게 바이너리 패킷 전송 (신규 하드웨어 제어용)"""
    if robot_id and robot_id in active_tcp_connections:
        sock = active_tcp_connections[robot_id]
    elif active_tcp_connections:
        robot_id = next(iter(active_tcp_connections.keys()))
        sock = active_tcp_connections[robot_id]
    else:
        return False

    try:
        sock.sendall(packet)
        print(f"📤 [TCP 바이너리 전송] {robot_id} → {packet.hex().upper()}")
        return True
    except Exception as e:
        print(f"❌ [TCP 바이너리 전송 실패] {robot_id}: {e}")
        return False


# --- [신규 API] 액추에이터 제어 ---

@robot_bp.route('/api/robot/actuator', methods=['POST'])
def control_actuator():
    """
    Auto/Manual 모드 변경 및 개별 장치 제어 (MSG_TYPE: 0x21)
    - actuator_id: 0(MODE), 1(PUMP), 2(FAN), 3(HEATER), 4(LED)
    - value: 0(OFF/MANUAL), 1(ON/AUTO) (LED는 0~100)
    """
    data = request.get_json()
    robot_id = data.get('robot_id', 'R01')
    actuator_id = data.get('actuator_id')
    state_value = data.get('value')

    if actuator_id is None or state_value is None:
        return jsonify({"ok": False, "error": "actuator_id와 value가 필요합니다."}), 400

    # 바이너리 패킷 생성
    packet = build_actuator_packet(dst_id=0x01, actuator_id=actuator_id, state_value=state_value)
    
    if send_binary_to_robot(robot_id, packet):
        devices = ["MODE", "PUMP", "FAN", "HEATER", "LED"]
        device_name = devices[actuator_id] if actuator_id < len(devices) else "UNKNOWN"
        return jsonify({"ok": True, "message": f"{device_name} 제어 명령 전송 완료"})
    
    return jsonify({"ok": False, "error": "로봇 연결 안됨"}), 503


# --- [기존 API] 로봇 제어 및 상태 ---

@robot_bp.route('/api/robot/control', methods=['POST'])
def control_robot():
    """개별 로봇 제어 (이동/정지)"""
    data = request.get_json()
    robot_id = data.get('robot_id')
    command = data.get('command')
    print(f"💻 [API 수신] 로봇: {robot_id} | 명령: {command}")
    return jsonify({"success": True, "message": f"{robot_id} 로봇 {command} 명령 처리 성공"})


@robot_bp.route('/api/robot/emergency_stop', methods=['POST'])
def emergency_stop():
    """전체 로봇 비상 정지"""
    print("🚨 [API 수신] 모든 로봇 비상 정지 명령 수신!")
    for rid in list(active_tcp_connections.keys()):
        send_to_robot(rid, {"cmd": "STOP"})
    return jsonify({"success": True, "message": "비상 정지 명령 처리 성공"})


@robot_bp.route('/api/robot/cmd', methods=['POST'])
def manual_control_cmd():
    """수동 이동 명령 전송 (W,A,S,D 조이스틱)"""
    data = request.get_json()
    robot_id = data.get('robot_id', 'R01')
    command = data.get('command', 'MOVE')
    direction = data.get('direction', 'STOP')
    
    cmd_dict = {"cmd": command, "direction": direction}
    if send_to_robot(robot_id, cmd_dict):
        return jsonify({"ok": True, "message": f"{direction} 이동 명령 전송"})
    return jsonify({"ok": False, "error": "로봇 연결 안됨"}), 503


@robot_bp.route('/api/robots')
def list_robots():
    """연결된 로봇 목록"""
    robots = list(active_tcp_connections.keys())
    return jsonify({"ok": True, "robots": robots})


@robot_bp.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    """작업 조회 및 생성"""
    from database.db_config import get_db_connection

    if request.method == 'GET':
        limit = request.args.get('limit', 20, type=int)
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT task_id, agv_id as robot_id, source_node, destination_node, task_status, ordered_at as created_at "
                    "FROM transport_tasks ORDER BY task_id DESC LIMIT %s", 
                    (limit,)
                )
                tasks = cursor.fetchall()
                for t in tasks:
                    if isinstance(t.get('created_at'), datetime):
                        t['created_at'] = t['created_at'].isoformat()
            return jsonify({"ok": True, "tasks": tasks})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500
        finally:
            if conn: conn.close()

    # POST (작업 생성) 처리
    data = request.get_json() or request.form
    destination = (data.get("destination") or "").strip().lower()
    robot_id = (data.get("robot_id") or "R01").strip()

    if not destination or destination not in VALID_NODES:
        return jsonify({"ok": False, "error": "유효하지 않은 목적지"}), 400

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT IGNORE INTO agv_robots (agv_id, status_id) VALUES (%s, 1)", (robot_id,))
            sql = """INSERT INTO transport_tasks 
                    (agv_id, variety_id, source_node, destination_node, ordered_by, quantity, task_status, ordered_at) 
                    VALUES (%s, 1, 'a01', %s, 1, 1, 0, %s)"""
            cursor.execute(sql, (robot_id, destination, datetime.now()))
            task_id = cursor.lastrowid
        conn.commit()
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    finally:
        if conn: conn.close()

    cmd = {"cmd": "GOTO", "target_node": destination}
    if send_to_robot(robot_id, cmd):
        return jsonify({"ok": True, "task_id": task_id, "message": f"목적지 {destination}로 전송 완료"})
    return jsonify({"ok": False, "error": "연결된 로봇이 없습니다.", "task_id": task_id}), 503


@robot_bp.route('/api/send_path', methods=['POST'])
def send_path():
    """경로 직접 전송 (MOVE + path)"""
    data = request.get_json() or request.form
    path = (data.get("path") or "").strip().upper()
    robot_id = (data.get("robot_id") or "R01").strip()

    if not path:
        return jsonify({"ok": False, "error": "경로를 입력하세요."}), 400

    cmd = {"cmd": "MOVE", "path": path}
    if send_to_robot(robot_id, cmd):
        return jsonify({"ok": True, "message": f"경로 '{path}' 전송 완료"})
    return jsonify({"ok": False, "error": "연결된 로봇이 없습니다."}), 503


@robot_bp.route('/api/robot/arm', methods=['POST'])
def arm_control():
    """암/그리퍼 제어 및 입고 작업 자동 생성"""
    data = request.get_json()
    action = (data.get("action") or "").strip()
    robot_id = (data.get("robot_id") or "R01").strip()

    VALID_ACTIONS = ("ARM_CW_180", "ARM_CCW_180", "GRIPPER_GRAB", "GRIPPER_RELEASE", "INBOUND_PICKUP", "U_TURN_TEST")
    if action not in VALID_ACTIONS:
        return jsonify({"ok": False, "error": "유효하지 않은 action"}), 400

    task_id = None
    if action == "INBOUND_PICKUP":
        from database.db_config import get_db_connection
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("INSERT IGNORE INTO agv_robots (agv_id, status_id) VALUES (%s, 1)", (robot_id,))
                cursor.execute("""
                    INSERT INTO transport_tasks 
                    (agv_id, variety_id, source_node, destination_node, ordered_by, quantity, task_status, ordered_at) 
                    VALUES (%s, 1, 'a01', 's11', 1, 1, 0, %s)
                """, (robot_id, datetime.now()))
                task_id = cursor.lastrowid
            conn.commit()
        except Exception as e:
            print(f"❌ DB 자동 작업 생성 오류: {e}")
        finally:
            if conn: conn.close()

    cmd = {"cmd": "TASK", "action": action}
    if send_to_robot(robot_id, cmd):
        msg = f"암 명령 '{action}' 전송 완료"
        if task_id: msg += f" (Task ID: {task_id} 생성)"
        return jsonify({"ok": True, "message": msg})
    return jsonify({"ok": False, "error": "연결된 로봇이 없습니다."}), 503


@robot_bp.route('/api/robot_state')
def get_robot_state():
    """웹 대시보드용 로봇 상태 반환"""
    robot_id = request.args.get('robot_id', 'R01')
    if robot_id in latest_robot_state:
        return jsonify({
            "ok": True, 
            "connected": robot_id in active_tcp_connections,
            "state": latest_robot_state[robot_id]
        })
    return jsonify({"ok": False, "error": "데이터 없음"}), 404


@robot_bp.route('/api/agv/activity_logs')
def get_agv_activity_logs():
    """AGV 활동 기록 조회"""
    from database.db_config import get_db_connection
    limit = request.args.get('limit', 20, type=int)
    agv_id = request.args.get('agv_id', 'R01')
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT log_id, action_type_id, target_id as agv_id, action_detail, action_time 
                FROM user_action_logs 
                WHERE action_type_id IN (10, 11) AND target_id = %s
                ORDER BY log_id DESC LIMIT %s
            """, (agv_id, limit))
            logs = cursor.fetchall()
            for l in logs:
                if l['action_time']: l['action_time'] = l['action_time'].isoformat()
            return jsonify({"ok": True, "logs": logs})
    finally:
        conn.close()