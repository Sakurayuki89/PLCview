#!/usr/bin/env python3
"""
PLC AI Assistant - 메인 애플리케이션
Claude Code가 직접 작성한 핵심 애플리케이션 파일
"""
import uvicorn
import asyncio
import platform
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import settings
from app.services.plc.connection import plc_connection
from app.services.plc.simulator import plc_simulator
from app.api.v1.router import api_router


class PLCApplication:
    """PLC AI Assistant 애플리케이션 클래스"""

    def __init__(self):
        self.app = None
        self.is_running = False

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """애플리케이션 생명주기 관리"""
        # 시작 시 초기화
        await self.startup()
        yield
        # 종료 시 정리
        await self.shutdown()

    def create_app(self) -> FastAPI:
        """FastAPI 애플리케이션 생성 및 설정"""
        app = FastAPI(
            title="PLC AI Assistant",
            description="Cross-platform PLC Programming AI Support System",
            version="0.1.0",
            docs_url="/docs",
            redoc_url="/redoc",
            lifespan=self.lifespan
        )

        # CORS 설정
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # API 라우터 등록
        app.include_router(api_router, prefix=settings.api_v1_str)

        # 정적 파일 서빙 (플랫폼별 경로 처리)
        frontend_path = Path(__file__).parent.parent / "frontend"
        if frontend_path.exists():
            app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

        # WebSocket 관리자 설정
        self.setup_websocket(app)

        # 기본 엔드포인트
        self.setup_basic_endpoints(app)

        self.app = app
        return app

    def setup_websocket(self, app: FastAPI):
        """WebSocket 연결 관리 설정"""
        from app.services.websocket_manager import connection_manager

        @app.websocket("/ws/plc-data")
        async def websocket_plc_data(websocket: WebSocket):
            """PLC 데이터 실시간 스트리밍"""
            await connection_manager.connect(websocket)
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                connection_manager.disconnect(websocket)

    def setup_basic_endpoints(self, app: FastAPI):
        """기본 엔드포인트 설정"""
        @app.get("/")
        async def root():
            return {
                "message": "PLC AI Assistant API",
                "status": "running",
                "platform": platform.system(),
                "version": "0.1.0"
            }

        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "platform": platform.system(),
                "plc_connected": plc_connection.is_connected,
                "simulator_running": plc_simulator.running,
                "environment": "development" if settings.debug else "production"
            }

    async def startup(self):
        """애플리케이션 시작 시 초기화"""
        print(f"🚀 PLC AI Assistant 시작 - {platform.system()}")
        print(f"🌐 서버 주소: http://{settings.host}:{settings.port}")

        # 플랫폼별 초기화
        await self.platform_specific_setup()

        # PLC 시뮬레이터 시작
        if settings.dev_mode:
            asyncio.create_task(plc_simulator.start_simulation())
            print("🔧 개발 모드: PLC 시뮬레이터 시작")

        # 실시간 데이터 브로드캐스팅 시작
        asyncio.create_task(self.data_broadcasting_loop())

        self.is_running = True

    async def shutdown(self):
        """애플리케이션 종료 시 정리"""
        print("🛑 PLC AI Assistant 종료")
        self.is_running = False

        # PLC 연결 해제
        await plc_connection.disconnect()

        # 시뮬레이터 정지
        plc_simulator.stop_simulation()

    async def platform_specific_setup(self):
        """플랫폼별 초기화 작업"""
        if settings.is_windows:
            print("🪟 Windows 환경에서 실행")
            # Windows 특화 설정
        elif settings.is_macos:
            print("🍎 macOS 환경에서 실행")
            # macOS 특화 설정
        else:
            print("🐧 Linux 환경에서 실행")
            # Linux 특화 설정

    async def data_broadcasting_loop(self):
        """실시간 데이터 브로드캐스팅 루프"""
        from app.services.websocket_manager import connection_manager
        from datetime import datetime
        import json

        while self.is_running:
            try:
                # PLC 데이터 수집
                data = await self.collect_plc_data()

                # WebSocket으로 브로드캐스트
                if connection_manager.active_connections:
                    await connection_manager.broadcast(data)

            except Exception as e:
                print(f"❌ 데이터 브로드캐스팅 오류: {e}")

            await asyncio.sleep(0.1)  # 100ms 주기

    async def collect_plc_data(self) -> dict:
        """PLC 데이터 수집"""
        from datetime import datetime

        try:
            if plc_connection.is_connected:
                # 실제 PLC에서 데이터 읽기
                temperature = await plc_connection.read_data("D100", 1)
                pressure = await plc_connection.read_data("D101", 1)
                speed = await plc_connection.read_data("D102", 1)

                return {
                    "timestamp": datetime.now().isoformat(),
                    "plc_data": {
                        "temperature": temperature[0] if temperature else 0,
                        "pressure": pressure[0] if pressure else 0,
                        "speed": speed[0] if speed else 0,
                    },
                    "status": "connected",
                    "source": "plc"
                }
            else:
                # 시뮬레이터 데이터 사용
                return {
                    "timestamp": datetime.now().isoformat(),
                    "plc_data": {
                        "temperature": plc_simulator.read_device("D100"),
                        "pressure": plc_simulator.read_device("D101"),
                        "speed": plc_simulator.read_device("D102"),
                    },
                    "status": "simulator",
                    "source": "simulator"
                }

        except Exception as e:
            print(f"❌ 데이터 수집 오류: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "plc_data": {"temperature": 0, "pressure": 0, "speed": 0},
                "status": "error",
                "source": "none"
            }


# 전역 애플리케이션 인스턴스
plc_app = PLCApplication()

# FastAPI 앱 인스턴스 (외부에서 import 가능)
app = plc_app.create_app()


def main():
    """메인 함수 - 개발용 서버 실행"""
    app = plc_app.create_app()

    # 플랫폼별 서버 설정
    if settings.is_windows:
        # Windows에서는 기본 이벤트 루프 사용
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
    else:
        # macOS/Linux에서는 uvloop 사용 가능
        try:
            import uvloop
            uvloop.install()
        except ImportError:
            pass

        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )


if __name__ == "__main__":
    main()