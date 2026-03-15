import pymysql  # pymysql로 통일
from .db_config import db_config_settings  # 정확한 변수명 가져오기


class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            # pymysql.connect(**설정값)
            self.conn = pymysql.connect(**db_config_settings)
            self.cursor = self.conn.cursor()
            print("✅ [DB 연결 성공] 3.35.24.94 서버에 접속되었습니다.")
        except Exception as e:
            print(f"❌ [DB 연결 실패]: {e}")

    def execute_query(self, query, params=None):
        if not self.cursor:
            return None
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ 쿼리 실행 실패: {e}")
            return None

    def execute_update(self, query, params=None):
        if not self.conn or not self.cursor:
            print("❌ DB가 연결되지 않았습니다.")
            return
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            print("💾 DB 저장 완료")
        except Exception as e:
            print(f"❌ 데이터 저장 실패: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print("🔌 DB 연결 해제")
