"""
farm_env_manager.py
===================
육묘장 환경(온도, 습도)을 모니터링하고,
목표 범위를 벗어났을 때 제어 조치를 판단하는 비즈니스 로직 모듈.
"""

from database.farm_repository import FarmRepository


class FarmEnvManager:
    """
    육묘 환경 제어 매니저.

    역할:
        - 각 노드의 온/습도 데이터를 수신하여 모니터링
        - 목표 온습도 범위를 벗어나면 쿨링 팬 / 히터 / 가습기 등 제어 명령 생성
        - 환경 데이터를 DB에 기록 (FarmRepository 활용)

    의존성:
        - FarmRepository : DB에 환경 데이터 기록 및 노드 상태 업데이트
    """

    # ──────────────────────────────────────────────
    #  목표 환경 설정값 (기본값)
    # ──────────────────────────────────────────────
    DEFAULT_TARGET_TEMP_MIN = 20.0   # 최소 목표 온도 (°C)
    DEFAULT_TARGET_TEMP_MAX = 28.0   # 최대 목표 온도 (°C)
    DEFAULT_TARGET_HUM_MIN = 50.0    # 최소 목표 습도 (%)
    DEFAULT_TARGET_HUM_MAX = 70.0    # 최대 목표 습도 (%)

    def __init__(self, farm_repository: FarmRepository):
        """
        Args:
            farm_repository : FarmRepository 인스턴스 (DI – 의존성 주입)
        """
        self.repo = farm_repository

        # ── 목표 환경 범위 설정 ──
        self.target_temp_min = self.DEFAULT_TARGET_TEMP_MIN
        self.target_temp_max = self.DEFAULT_TARGET_TEMP_MAX
        self.target_hum_min = self.DEFAULT_TARGET_HUM_MIN
        self.target_hum_max = self.DEFAULT_TARGET_HUM_MAX

        # ── 최근 수신된 각 노드의 환경 데이터 캐시 (Key 타입을 str로 통일) ──
        self._env_cache: dict[str, dict] = {}

    # ──────────── 환경 데이터 업데이트 (메인 진입점) ────────────
    def update_environment(self, node_id: str, temperature: float, humidity: float):
        """
        센서에서 수신된 환경 데이터를 처리한다.
        """
        # node_id가 혹시 숫자로 들어와도 안전하게 문자열로 변환
        node_id_str = str(node_id)

        print(f"\n🌡️ [FarmEnvManager] 노드 {node_id_str} 환경 수신: "
              f"온도={temperature}°C, 습도={humidity}%")

        # 1) 캐시 업데이트
        self._env_cache[node_id_str] = {
            "temperature": temperature,
            "humidity": humidity,
        }

        # 2) DB에 현재 환경 데이터 반영 (Repository에 해당 함수가 있어야 함)
        self.repo.update_node_environment(node_id_str, temperature, humidity)

        # 3) 센서 로그 기록
        self.repo.insert_sensor_log(node_id_str, temperature, humidity)

        # 4) [수정완료] _check_and_control 호출 시 self 인자 중복 제거
        self._check_and_control(node_id_str, temperature, humidity)

    # ──────────── 환경 이상 판단 및 제어 ────────────
    # [수정완료] node_id 타입을 str로 통일
    def _check_and_control(self, node_id: str, temperature: float, humidity: float):
        """
        현재 온습도가 목표 범위 내에 있는지 확인하고 조치 실행.
        """
        # ─── 온도 판단 ───
        if temperature > self.target_temp_max:
            print(f"🔴 [FarmEnvManager] 노드 {node_id}: 온도 초과 "
                  f"({temperature}°C > {self.target_temp_max}°C)")
            self._activate_cooling_fan(node_id)

        elif temperature < self.target_temp_min:
            print(f"🔵 [FarmEnvManager] 노드 {node_id}: 온도 부족 "
                  f"({temperature}°C < {self.target_temp_min}°C)")
            self._activate_heater(node_id)

        else:
            print(f"🟢 [FarmEnvManager] 노드 {node_id}: 온도 정상 범위 ✅")

        # ─── 습도 판단 ───
        if humidity > self.target_hum_max:
            print(f"🔴 [FarmEnvManager] 노드 {node_id}: 습도 초과 "
                  f"({humidity}% > {self.target_hum_max}%)")
            self._activate_ventilation(node_id)

        elif humidity < self.target_hum_min:
            print(f"🔵 [FarmEnvManager] 노드 {node_id}: 습도 부족 "
                  f"({humidity}% < {self.target_hum_min}%)")
            self._activate_humidifier(node_id)

        else:
            print(f"🟢 [FarmEnvManager] 노드 {node_id}: 습도 정상 범위 ✅")

    # ──────────────────────────────────────────────
    #  제어 장치 액추에이터 명령 (뼈대)
    # ──────────────────────────────────────────────

    def _activate_cooling_fan(self, node_id: str):
        print(f"❄️ [FarmEnvManager] 노드 {node_id}: 쿨링 팬 가동 명령 전송")

    def _activate_heater(self, node_id: str):
        print(f"🔥 [FarmEnvManager] 노드 {node_id}: 히터 가동 명령 전송")

    def _activate_ventilation(self, node_id: str):
        print(f"💨 [FarmEnvManager] 노드 {node_id}: 환기 팬 가동 명령 전송")

    def _activate_humidifier(self, node_id: str):
        print(f"💧 [FarmEnvManager] 노드 {node_id}: 가습기 가동 명령 전송")

    # ──────────── 전체 캐시 환경 조회 ────────────
    # [수정완료] 반환 타입 힌트를 dict[str, dict]로 변경
    def get_all_environments(self) -> dict[str, dict]:
        """캐시에 저장된 전체 노드의 최신 환경 데이터를 반환"""
        return self._env_cache.copy()