"""
통합 테스트: API 엔드포인트 전체 흐름 검증
"""
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# 테스트용 환경 설정
pytestmark = pytest.mark.asyncio


class TestAPIIntegration:
    """API 통합 테스트"""

    @pytest.fixture
    def client(self):
        """테스트 클라이언트 픽스처"""
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def mock_plc_service(self):
        """Mock PLC 서비스"""
        with patch('app.services.plc.plc_service.PLCService') as mock:
            mock_instance = Mock()
            mock_instance.connect.return_value = True
            mock_instance.read_device.return_value = {"value": 100, "status": "ok"}
            mock_instance.write_device.return_value = True
            mock_instance.is_connected.return_value = True
            mock.return_value = mock_instance
            yield mock_instance

    def test_health_check(self, client):
        """헬스 체크 API 테스트"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_api_v1_docs_accessible(self, client):
        """API 문서 접근 가능성 테스트"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_plc_connection_flow(self, client, mock_plc_service):
        """PLC 연결 전체 흐름 테스트"""
        # 1. 연결 상태 확인
        response = client.get("/api/v1/plc/status")
        assert response.status_code == 200

        # 2. 연결 시도
        response = client.post("/api/v1/plc/connect")
        assert response.status_code == 200

        # 3. 데이터 읽기
        response = client.get("/api/v1/plc/read/D100")
        assert response.status_code == 200
        assert "value" in response.json()

        # 4. 데이터 쓰기
        response = client.post("/api/v1/plc/write/D100", json={"value": 200})
        assert response.status_code == 200

    def test_ai_integration_flow(self, client):
        """AI 통합 전체 흐름 테스트"""
        # AI 분석 요청
        test_data = {
            "data": [100, 110, 105, 95, 102],
            "analysis_type": "trend"
        }

        with patch('app.services.ai.ai_service.analyze_data') as mock_ai:
            mock_ai.return_value = {"trend": "stable", "confidence": 0.85}

            response = client.post("/api/v1/ai/analyze", json=test_data)
            assert response.status_code == 200
            assert "trend" in response.json()

    def test_error_handling(self, client):
        """에러 핸들링 테스트"""
        # 잘못된 엔드포인트
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

        # 잘못된 데이터 형식
        response = client.post("/api/v1/plc/write/D100", json={"invalid": "data"})
        assert response.status_code in [400, 422]

    @pytest.mark.skipif(
        condition=True,  # 실제 PLC 하드웨어가 필요한 테스트
        reason="Requires actual PLC hardware connection"
    )
    def test_real_plc_integration(self, client):
        """실제 PLC 하드웨어 통합 테스트 (선택적)"""
        # 실제 PLC 연결이 필요한 테스트
        # CI/CD에서는 스킵, 로컬 개발환경에서만 실행
        pass


class TestWebSocketIntegration:
    """WebSocket 통합 테스트"""

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """WebSocket 연결 테스트"""
        from app.main import app

        async with AsyncClient(app=app, base_url="http://test") as client:
            with client.websocket_connect("/ws") as websocket:
                # 연결 성공 확인
                data = websocket.receive_json()
                assert "status" in data

    @pytest.mark.asyncio
    async def test_real_time_data_streaming(self):
        """실시간 데이터 스트리밍 테스트"""
        from app.main import app

        with patch('app.services.plc.plc_service.PLCService') as mock_plc:
            mock_instance = Mock()
            mock_instance.get_real_time_data.return_value = {
                "timestamp": "2025-09-20T14:00:00",
                "devices": {"D100": 150, "D101": 75}
            }
            mock_plc.return_value = mock_instance

            async with AsyncClient(app=app, base_url="http://test") as client:
                with client.websocket_connect("/ws/realtime") as websocket:
                    # 실시간 데이터 수신 확인
                    data = websocket.receive_json()
                    assert "timestamp" in data
                    assert "devices" in data


class TestEnvironmentIntegration:
    """환경 설정 통합 테스트"""

    def test_environment_variables_loaded(self):
        """환경변수 로딩 테스트"""
        from app.core.config import settings

        # 필수 환경변수들이 로드되었는지 확인
        assert settings.PLC_HOST is not None
        assert settings.PLC_PORT is not None
        assert settings.API_V1_STR is not None

    def test_cross_platform_compatibility(self):
        """크로스 플랫폼 호환성 테스트"""
        import platform

        # 현재 플랫폼에서 정상 동작하는지 확인
        current_platform = platform.system().lower()
        assert current_platform in ['windows', 'darwin', 'linux']

        # 플랫폼별 초기화 로직 테스트
        from app.core.platform import get_platform_config
        config = get_platform_config()
        assert config is not None

    def test_gemini_cli_integration(self):
        """Gemini CLI 통합 테스트"""
        import subprocess
        import os

        # Gemini CLI 설치 확인
        try:
            result = subprocess.run(['gemini', '--version'],
                                  capture_output=True, text=True)
            assert result.returncode == 0
        except FileNotFoundError:
            pytest.skip("Gemini CLI not installed")

        # API 키 설정 확인 (실제 호출은 안함)
        assert os.getenv('GEMINI_API_KEY') is not None


if __name__ == "__main__":
    # 직접 실행 시 테스트 수행
    pytest.main([__file__, "-v"])