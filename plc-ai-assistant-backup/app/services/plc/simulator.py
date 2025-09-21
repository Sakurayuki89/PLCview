"""
PLC 시뮬레이터
Claude Code가 직접 작성한 개발용 PLC 시뮬레이터
"""
import asyncio
import random
import time
import math
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PLCSimulator:
    """개발용 PLC 시뮬레이터 클래스"""

    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.running = False
        self._simulation_task: Optional[asyncio.Task] = None
        self._cycle_time = 0.1  # 100ms 주기
        self._initialize_devices()

    def _initialize_devices(self):
        """시뮬레이터 디바이스 초기화"""
        # 워드 디바이스 (D 레지스터)
        self.data.update({
            "D100": 25,    # 온도 (25도)
            "D101": 5,     # 압력 (5 bar)
            "D102": 1000,  # 속도 (1000 rpm)
            "D103": 0,     # 생산량 카운터
            "D104": 0,     # 오류 코드
            "D105": 100,   # 진동 센서
            "D106": 50,    # 유량
            "D107": 80,    # 습도
            "D108": 0,     # 예비1
            "D109": 0,     # 예비2
        })

        # 비트 디바이스 (M 릴레이)
        self.data.update({
            "M100": True,   # 시스템 운전 상태
            "M101": False,  # 알람
            "M102": True,   # 자동 모드
            "M103": False,  # 비상정지
            "M104": True,   # 안전 도어
            "M105": False,  # 메인터넌스 모드
            "M106": True,   # 전원 상태
            "M107": False,  # 예비1
            "M108": False,  # 예비2
            "M109": False,  # 예비3
        })

        # 입력 디바이스 (X)
        self.data.update({
            "X001": True,   # 시동 버튼
            "X002": False,  # 정지 버튼
            "X003": True,   # 자동/수동 선택
            "X004": False,  # 리셋 버튼
            "X005": True,   # 안전 센서1
            "X006": True,   # 안전 센서2
        })

        # 출력 디바이스 (Y)
        self.data.update({
            "Y001": True,   # 메인 모터
            "Y002": False,  # 알람 램프
            "Y003": True,   # 운전 표시등
            "Y004": False,  # 경고등
            "Y005": False,  # 예비 출력1
            "Y006": False,  # 예비 출력2
        })

        logger.info(f"📊 시뮬레이터 초기화 완료: {len(self.data)}개 디바이스")

    async def start_simulation(self):
        """시뮬레이션 시작"""
        if self.running:
            logger.info("시뮬레이터가 이미 실행 중입니다.")
            return

        self.running = True
        self._simulation_task = asyncio.create_task(self._simulation_loop())
        logger.info("🚀 PLC 시뮬레이터 시작")

    def stop_simulation(self):
        """시뮬레이션 중지"""
        if not self.running:
            return

        self.running = False
        if self._simulation_task:
            self._simulation_task.cancel()

        logger.info("🛑 PLC 시뮬레이터 중지")

    async def _simulation_loop(self):
        """시뮬레이션 메인 루프"""
        start_time = time.time()

        try:
            while self.running:
                current_time = time.time()
                elapsed = current_time - start_time

                # 시간 기반 시뮬레이션 업데이트
                await self._update_simulated_data(elapsed)

                await asyncio.sleep(self._cycle_time)

        except asyncio.CancelledError:
            logger.info("시뮬레이션 루프 취소됨")
        except Exception as e:
            logger.error(f"시뮬레이션 오류: {e}")

    async def _update_simulated_data(self, elapsed_time: float):
        """시뮬레이션 데이터 업데이트"""
        # 온도 시뮬레이션 (사인파 + 노이즈)
        base_temp = 25
        temp_variation = 10 * math.sin(elapsed_time * 0.1) + random.uniform(-2, 2)
        self.data["D100"] = max(0, min(100, int(base_temp + temp_variation)))

        # 압력 시뮬레이션
        if self.data["M100"]:  # 운전 중일 때
            pressure_target = 5
            current_pressure = self.data["D101"]
            # 점진적 변화
            pressure_diff = pressure_target - current_pressure
            self.data["D101"] = max(0, min(15, current_pressure + pressure_diff * 0.1 + random.uniform(-0.5, 0.5)))
        else:
            # 정지 중일 때 압력 감소
            self.data["D101"] = max(0, self.data["D101"] - 0.1)

        # 속도 시뮬레이션
        if self.data["M100"] and not self.data["M103"]:  # 운전 중이고 비상정지가 아닐 때
            speed_variation = random.uniform(-50, 50)
            self.data["D102"] = max(0, min(1500, 1000 + speed_variation))
        else:
            # 정지 중일 때 속도 감소
            self.data["D102"] = max(0, self.data["D102"] - 50)

        # 생산량 카운터 (운전 중일 때 증가)
        if self.data["M100"] and self.data["D102"] > 500:
            if random.random() < 0.1:  # 10% 확률로 카운트 증가
                self.data["D103"] = min(9999, self.data["D103"] + 1)

        # 진동 센서 (속도에 따른 변화)
        speed_ratio = self.data["D102"] / 1500.0
        base_vibration = speed_ratio * 50
        self.data["D105"] = max(0, min(200, int(base_vibration + random.uniform(-10, 10))))

        # 유량 시뮬레이션
        if self.data["M100"]:
            self.data["D106"] = max(0, min(100, 50 + random.uniform(-10, 10)))
        else:
            self.data["D106"] = 0

        # 습도 (환경 변화)
        humidity_change = random.uniform(-1, 1)
        self.data["D107"] = max(20, min(95, self.data["D107"] + humidity_change))

        # 알람 조건 체크
        await self._check_alarm_conditions()

        # 랜덤 이벤트
        await self._random_events()

    async def _check_alarm_conditions(self):
        """알람 조건 확인"""
        alarm_conditions = [
            self.data["D100"] > 80,      # 온도 과열
            self.data["D101"] > 12,      # 압력 과다
            self.data["D105"] > 150,     # 진동 과다
            self.data["M103"],           # 비상정지
        ]

        # 알람 상태 업데이트
        alarm_active = any(alarm_conditions)
        self.data["M101"] = alarm_active
        self.data["Y002"] = alarm_active  # 알람 램프

        if alarm_active:
            self.data["D104"] = random.choice([1, 2, 3, 4])  # 오류 코드
        else:
            self.data["D104"] = 0

    async def _random_events(self):
        """랜덤 이벤트 발생"""
        # 1% 확률로 비상정지 발생/해제
        if random.random() < 0.01:
            self.data["M103"] = not self.data["M103"]
            if self.data["M103"]:
                logger.warning("⚠️ 시뮬레이터: 비상정지 발생")
            else:
                logger.info("✅ 시뮬레이터: 비상정지 해제")

        # 0.5% 확률로 운전 모드 변경
        if random.random() < 0.005:
            self.data["M102"] = not self.data["M102"]
            mode = "자동" if self.data["M102"] else "수동"
            logger.info(f"🔄 시뮬레이터: {mode} 모드로 변경")

    def read_device(self, device: str) -> Any:
        """디바이스 값 읽기"""
        value = self.data.get(device, 0)
        logger.debug(f"📖 시뮬레이터 읽기: {device} = {value}")
        return value

    def write_device(self, device: str, value: Any):
        """디바이스 값 쓰기"""
        if device in self.data:
            old_value = self.data[device]
            self.data[device] = value
            logger.debug(f"📝 시뮬레이터 쓰기: {device} = {old_value} → {value}")

            # 특정 디바이스 쓰기에 대한 반응
            if device == "M100" and value != old_value:
                # 시스템 운전 상태 변경
                status = "시작" if value else "정지"
                logger.info(f"🔄 시뮬레이터: 시스템 {status}")

    def get_all_data(self) -> Dict[str, Any]:
        """모든 디바이스 데이터 반환"""
        return self.data.copy()

    def get_device_list(self) -> list:
        """시뮬레이터 디바이스 목록 반환"""
        return list(self.data.keys())

    def reset_counters(self):
        """카운터 초기화"""
        self.data["D103"] = 0  # 생산량 카운터
        logger.info("🔄 시뮬레이터: 카운터 초기화")

    def get_statistics(self) -> Dict[str, Any]:
        """시뮬레이터 통계 정보"""
        return {
            "running": self.running,
            "device_count": len(self.data),
            "cycle_time": self._cycle_time,
            "alarm_active": self.data.get("M101", False),
            "system_running": self.data.get("M100", False),
            "production_count": self.data.get("D103", 0)
        }


# 전역 시뮬레이터 인스턴스
plc_simulator = PLCSimulator()