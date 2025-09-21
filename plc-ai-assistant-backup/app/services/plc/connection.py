"""
PLC 연결 서비스
Claude Code가 직접 작성한 핵심 PLC 통신 로직
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class PLCConnection:
    """PLC 연결 및 통신 관리 클래스"""

    def __init__(self):
        self.plc = None
        self.is_connected: bool = False
        self._connection_lock = asyncio.Lock()
        self._retry_count = 0
        self._max_retries = 3

    async def connect(self) -> bool:
        """PLC 연결 (스레드 안전)"""
        async with self._connection_lock:
            if self.is_connected:
                logger.info("이미 PLC에 연결되어 있습니다.")
                return True

            return await self._attempt_connection()

    async def _attempt_connection(self) -> bool:
        """실제 PLC 연결 시도"""
        try:
            # pymcprotocol 동적 임포트 (선택적 의존성)
            try:
                import pymcprotocol
            except ImportError:
                logger.warning("pymcprotocol이 설치되지 않았습니다. 시뮬레이터 모드로 실행됩니다.")
                return False

            self.plc = pymcprotocol.Type3E()

            # 비동기 연결을 위해 executor 사용
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.plc.connect,
                settings.plc_host,
                settings.plc_port
            )

            self.is_connected = True
            self._retry_count = 0
            logger.info(f"✅ PLC 연결 성공: {settings.plc_host}:{settings.plc_port}")

            # 연결 상태 확인을 위한 간단한 읽기 테스트
            await self._test_connection()

            return True

        except Exception as e:
            self.is_connected = False
            self._retry_count += 1
            logger.error(f"❌ PLC 연결 실패 (시도 {self._retry_count}/{self._max_retries}): {e}")

            if self._retry_count < self._max_retries:
                await asyncio.sleep(2)  # 2초 대기 후 재시도
                return await self._attempt_connection()

            return False

    async def _test_connection(self):
        """연결 상태 테스트"""
        try:
            # 간단한 디바이스 읽기로 연결 확인
            await self.read_data("D0", 1)
            logger.info("📡 PLC 연결 상태 확인 완료")
        except Exception as e:
            logger.warning(f"⚠️ PLC 연결 테스트 실패: {e}")

    async def disconnect(self):
        """PLC 연결 해제"""
        async with self._connection_lock:
            if self.plc and self.is_connected:
                try:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self.plc.close)
                    self.is_connected = False
                    logger.info("✅ PLC 연결 해제 완료")
                except Exception as e:
                    logger.error(f"❌ PLC 연결 해제 실패: {e}")

    async def read_data(self, device: str, count: int = 1) -> Optional[List[int]]:
        """
        PLC 데이터 읽기

        Args:
            device: 디바이스 주소 (예: "D100", "M101")
            count: 읽을 데이터 개수

        Returns:
            읽은 데이터 리스트 또는 None
        """
        if not await self._ensure_connection():
            return None

        try:
            loop = asyncio.get_event_loop()

            # 디바이스 타입에 따른 읽기 함수 선택
            if device.startswith('M') or device.startswith('X') or device.startswith('Y'):
                # 비트 디바이스
                data = await loop.run_in_executor(
                    None,
                    self.plc.batchread_bitunits,
                    device,
                    count
                )
            else:
                # 워드 디바이스
                data = await loop.run_in_executor(
                    None,
                    self.plc.batchread_wordunits,
                    device,
                    count
                )

            logger.debug(f"📖 PLC 읽기 성공: {device} = {data}")
            return data

        except Exception as e:
            logger.error(f"❌ PLC 데이터 읽기 실패 {device}: {e}")
            await self._handle_communication_error()
            return None

    async def write_data(self, device: str, values: List[int]) -> bool:
        """
        PLC 데이터 쓰기

        Args:
            device: 디바이스 주소
            values: 쓸 데이터 리스트

        Returns:
            성공 여부
        """
        if not await self._ensure_connection():
            return False

        try:
            loop = asyncio.get_event_loop()

            # 디바이스 타입에 따른 쓰기 함수 선택
            if device.startswith('M') or device.startswith('X') or device.startswith('Y'):
                # 비트 디바이스
                await loop.run_in_executor(
                    None,
                    self.plc.batchwrite_bitunits,
                    device,
                    values
                )
            else:
                # 워드 디바이스
                await loop.run_in_executor(
                    None,
                    self.plc.batchwrite_wordunits,
                    device,
                    values
                )

            logger.debug(f"📝 PLC 쓰기 성공: {device} = {values}")
            return True

        except Exception as e:
            logger.error(f"❌ PLC 데이터 쓰기 실패 {device}: {e}")
            await self._handle_communication_error()
            return False

    async def _ensure_connection(self) -> bool:
        """연결 상태 확인 및 자동 재연결"""
        if not self.is_connected:
            logger.info("🔄 PLC 자동 재연결 시도...")
            return await self.connect()
        return True

    async def _handle_communication_error(self):
        """통신 오류 처리"""
        self.is_connected = False
        logger.warning("📡 PLC 통신 오류 감지, 연결 상태 초기화")

    async def get_connection_status(self) -> Dict[str, Any]:
        """연결 상태 정보 반환"""
        return {
            "connected": self.is_connected,
            "host": settings.plc_host,
            "port": settings.plc_port,
            "retry_count": self._retry_count,
            "max_retries": self._max_retries
        }

    async def batch_read_multiple(self, devices: Dict[str, int]) -> Dict[str, Optional[List[int]]]:
        """
        여러 디바이스 일괄 읽기

        Args:
            devices: {"device_name": count} 형태의 딕셔너리

        Returns:
            {"device_name": [values]} 형태의 결과
        """
        results = {}
        for device, count in devices.items():
            results[device] = await self.read_data(device, count)
        return results


# 전역 PLC 연결 인스턴스
plc_connection = PLCConnection()