"""
WebSocket 연결 관리자
Claude Code가 직접 작성한 핵심 서비스
"""
import json
import asyncio
from typing import List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket 연결 관리 클래스"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """새로운 WebSocket 연결 추가"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info(f"✅ WebSocket 연결 추가. 총 연결 수: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """WebSocket 연결 제거"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"❌ WebSocket 연결 제거. 총 연결 수: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """특정 WebSocket에 메시지 전송"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"개별 메시지 전송 실패: {e}")
            self.disconnect(websocket)

    async def broadcast(self, data: dict):
        """모든 연결된 클라이언트에 데이터 브로드캐스트"""
        if not self.active_connections:
            return

        message = json.dumps(data, ensure_ascii=False)
        disconnected = []

        # 모든 연결에 동시 전송
        tasks = []
        for connection in self.active_connections.copy():
            tasks.append(self._safe_send(connection, message, disconnected))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        # 끊어진 연결들 제거
        for connection in disconnected:
            self.disconnect(connection)

    async def _safe_send(self, connection: WebSocket, message: str, disconnected: List[WebSocket]):
        """안전한 메시지 전송"""
        try:
            await connection.send_text(message)
        except Exception as e:
            logger.warning(f"WebSocket 전송 실패: {e}")
            disconnected.append(connection)

    async def broadcast_status(self, status: str, details: dict = None):
        """시스템 상태 브로드캐스트"""
        data = {
            "type": "status",
            "status": status,
            "details": details or {}
        }
        await self.broadcast(data)

    async def broadcast_alert(self, level: str, message: str):
        """알림 메시지 브로드캐스트"""
        data = {
            "type": "alert",
            "level": level,  # info, warning, error
            "message": message
        }
        await self.broadcast(data)

    def get_connection_count(self) -> int:
        """현재 연결 수 반환"""
        return len(self.active_connections)


# 전역 연결 관리자 인스턴스
connection_manager = ConnectionManager()