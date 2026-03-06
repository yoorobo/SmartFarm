"""
db.py - SQLite 데이터베이스 초기화 및 작업 관리
===============================================
목적지(task)를 저장하고 조회하는 모듈.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "robot_tasks.db")

# 로봇이 인식 가능한 목적지 노드 목록 (PathFinder 기준)
VALID_NODES = [
    "a01", "a02", "a03", "a04",
    "s05", "s06", "s07",
    "r08", "r09", "r10",
    "s11", "s12", "s13",
    "r14", "r15", "r16",
]


def init_db():
    """데이터베이스 및 테이블 생성"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            robot_id TEXT DEFAULT 'R01',
            status TEXT DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            sent_at TEXT,
            completed_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS task_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            event TEXT,
            message TEXT,
            created_at TEXT,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)
    conn.commit()
    conn.close()


def add_task(destination: str, robot_id: str = "R01") -> int:
    """새 목적지 작업 추가. 반환: task_id"""
    if destination not in VALID_NODES:
        raise ValueError(f"유효하지 않은 목적지: {destination}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO tasks (destination, robot_id, status, created_at) VALUES (?, ?, 'PENDING', ?)",
        (destination, robot_id, now),
    )
    task_id = cur.lastrowid
    conn.commit()
    conn.close()
    return task_id


def get_task(task_id: int) -> Optional[dict]:
    """task_id로 작업 조회"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_pending_tasks(robot_id: Optional[str] = None) -> list:
    """대기 중인 작업 목록"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if robot_id:
        cur.execute(
            "SELECT * FROM tasks WHERE status = 'PENDING' AND robot_id = ? ORDER BY id",
            (robot_id,),
        )
    else:
        cur.execute("SELECT * FROM tasks WHERE status = 'PENDING' ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_task_sent(task_id: int):
    """작업이 로봇에 전송됨"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "UPDATE tasks SET status = 'SENT', sent_at = ? WHERE id = ?",
        (now, task_id),
    )
    conn.commit()
    conn.close()


def mark_task_completed(task_id: int):
    """작업 완료 처리"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "UPDATE tasks SET status = 'COMPLETED', completed_at = ? WHERE id = ?",
        (now, task_id),
    )
    conn.commit()
    conn.close()


def get_recent_tasks(limit: int = 20) -> list:
    """최근 작업 목록 (웹 UI용)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM tasks ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
