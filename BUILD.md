# BUILD.md - PLC AI 지원 시스템 효율적 빌드 가이드

> **토큰 절약형 개발**: 이 가이드는 Claude Code에서 최소한의 토큰으로 최대 효과를 내도록 설계되었습니다.

## 🎯 빌드 철학

1. **한 번에 하나씩**: 각 단계는 독립적으로 테스트 가능
2. **복붙 지향**: 코드는 바로 실행 가능한 완성된 형태
3. **오류 방지**: 검증된 패턴만 사용
4. **방향성 유지**: 명확한 다음 단계 제시

## 📋 빌드 체크리스트

```
□ Phase 1: 기반 설정 (30분)
□ Phase 2: PLC 연결 (45분)  
□ Phase 3: API 구축 (60분)
□ Phase 4: 실시간 스트리밍 (90분)
□ Phase 5: AI 통합 (120분)
```

---

## 🚀 Phase 1: 프로젝트 기반 설정 (30분)

### 1.1 디렉토리 구조 생성

```bash
# 한 번에 전체 구조 생성
mkdir -p plc-ai-assistant/{app/{api/v1/endpoints,core,services/{plc,ai,vision,data},workers,utils},tests/{unit,integration},scripts,docs,frontend/src,deployment}

cd plc-ai-assistant

# 필수 __init__.py 파일 생성
find app -type d -exec touch {}/__init__.py \;
touch tests/__init__.py
```

### 1.2 Poetry 설정 (pyproject.toml)

```toml
[tool.poetry]
name = "plc-ai-assistant"
version = "0.1.0"
description = "PLC AI Support System"
authors = ["Developer <dev@example.com>"]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "0.110.0"
uvicorn = {extras = ["standard"], version = "0.27.0"}
pymcprotocol = "0.3.0"
redis = "5.0.1"
pydantic-settings = "2.1.0"
python-multipart = "0.0.6"
sqlalchemy = "2.0.25"
websockets = "12.0"

[tool.poetry.group.dev.dependencies]
pytest = "7.4.4"
pytest-asyncio = "0.23.2"
black = "23.12.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 1.3 환경 설정 (.env)

```env
# PLC 설정
PLC_HOST=192.168.1.100
PLC_PORT=1025
PLC_TIMEOUT=5

# Redis 설정
REDIS_URL=redis://localhost:6379

# 애플리케이션 설정
DEBUG=true
LOG_LEVEL=INFO
API_V1_STR=/api/v1

# AI 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codegemma:7b
```

### 1.4 설정 관리 (app/config.py)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # PLC 설정
    plc_host: str = "192.168.1.100"
    plc_port: int = 1025
    plc_timeout: int = 5
    
    # Redis 설정
    redis_url: str = "redis://localhost:6379"
    
    # API 설정
    api_v1_str: str = "/api/v1"
    debug: bool = True
    log_level: str = "INFO"
    
    # AI 설정
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "codegemma:7b"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### ✅ Phase 1 검증

```bash
poetry install
poetry run python -c "from app.config import settings; print('✅ 설정 로드 성공:', settings.plc_host)"
```

---

## 🔌 Phase 2: PLC 연결 구현 (45분)

### 2.1 PLC 연결 서비스 (app/services/plc/connection.py)

```python
import pymcprotocol
import asyncio
from typing import Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class PLCConnection:
    def __init__(self):
        self.plc: Optional[pymcprotocol.Type3E] = None
        self.is_connected: bool = False
        
    async def connect(self) -> bool:
        """PLC 연결"""
        try:
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
            logger.info(f"✅ PLC 연결 성공: {settings.plc_host}:{settings.plc_port}")
            return True
        except Exception as e:
            logger.error(f"❌ PLC 연결 실패: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """PLC 연결 해제"""
        if self.plc and self.is_connected:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.plc.close)
                self.is_connected = False
                logger.info("✅ PLC 연결 해제 완료")
            except Exception as e:
                logger.error(f"❌ PLC 연결 해제 실패: {e}")
    
    async def read_data(self, device: str, count: int = 1) -> Optional[list]:
        """PLC 데이터 읽기"""
        if not self.is_connected or not self.plc:
            await self.connect()
            
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                self.plc.batchread_wordunits,
                device,
                count
            )
            return data
        except Exception as e:
            logger.error(f"❌ 데이터 읽기 실패 {device}: {e}")
            return None
    
    async def write_data(self, device: str, values: list) -> bool:
        """PLC 데이터 쓰기"""
        if not self.is_connected or not self.plc:
            await self.connect()
            
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.plc.batchwrite_wordunits,
                device,
                values
            )
            return True
        except Exception as e:
            logger.error(f"❌ 데이터 쓰기 실패 {device}: {e}")
            return False

# 전역 인스턴스
plc_connection = PLCConnection()
```

### 2.2 PLC 시뮬레이터 (개발용)

```python
# app/services/plc/simulator.py
import asyncio
import random
from typing import Dict, Any
from datetime import datetime

class PLCSimulator:
    """개발용 PLC 시뮬레이터"""
    
    def __init__(self):
        self.data = {
            "D100": 0,    # 온도
            "D101": 0,    # 압력
            "D102": 0,    # 속도
            "M100": False, # 모터 상태
            "M101": False, # 알람
        }
        self.running = False
    
    async def start_simulation(self):
        """시뮬레이션 시작"""
        self.running = True
        while self.running:
            # 랜덤 데이터 생성
            self.data["D100"] = random.randint(20, 80)  # 온도 20-80도
            self.data["D101"] = random.randint(1, 10)   # 압력 1-10bar
            self.data["D102"] = random.randint(0, 1500) # 속도 0-1500rpm
            self.data["M100"] = random.choice([True, False])
            
            await asyncio.sleep(0.1)  # 100ms 주기
    
    def stop_simulation(self):
        """시뮬레이션 중지"""
        self.running = False
    
    def read_device(self, device: str) -> Any:
        """디바이스 값 읽기"""
        return self.data.get(device, 0)
    
    def write_device(self, device: str, value: Any):
        """디바이스 값 쓰기"""
        self.data[device] = value

# 전역 시뮬레이터 인스턴스
plc_simulator = PLCSimulator()
```

### ✅ Phase 2 검증

```python
# tests/test_plc_connection.py
import pytest
from app.services.plc.connection import plc_connection
from app.services.plc.simulator import plc_simulator

@pytest.mark.asyncio
async def test_plc_connection():
    # 시뮬레이터 시작
    asyncio.create_task(plc_simulator.start_simulation())
    
    # 연결 테스트 (실제 PLC가 없으면 시뮬레이터 사용)
    result = await plc_connection.connect()
    print(f"✅ PLC 연결 테스트: {'성공' if result else '시뮬레이터 모드'}")
    
    # 정리
    plc_simulator.stop_simulation()
```

---

## 🌐 Phase 3: FastAPI 서버 구축 (60분)

### 3.1 메인 애플리케이션 (app/main.py)

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
from datetime import datetime

from app.config import settings
from app.api.v1.router import api_router
from app.services.plc.connection import plc_connection
from app.services.plc.simulator import plc_simulator

# FastAPI 앱 생성
app = FastAPI(
    title="PLC AI Assistant",
    description="PLC 프로그래밍 AI 지원 시스템",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.api_v1_str)

# WebSocket 연결 관리자
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(data))
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("🚀 PLC AI Assistant 시작")
    
    # 시뮬레이터 시작 (개발용)
    asyncio.create_task(plc_simulator.start_simulation())
    
    # 실시간 데이터 브로드캐스팅 시작
    asyncio.create_task(data_broadcasting())

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    print("🛑 PLC AI Assistant 종료")
    plc_simulator.stop_simulation()
    await plc_connection.disconnect()

async def data_broadcasting():
    """실시간 데이터 브로드캐스팅"""
    while True:
        try:
            # PLC 데이터 수집
            if plc_connection.is_connected:
                temperature = await plc_connection.read_data("D100", 1)
                pressure = await plc_connection.read_data("D101", 1)
            else:
                # 시뮬레이터 데이터 사용
                temperature = [plc_simulator.read_device("D100")]
                pressure = [plc_simulator.read_device("D101")]
            
            # 데이터 브로드캐스트
            data = {
                "timestamp": datetime.now().isoformat(),
                "plc_data": {
                    "temperature": temperature[0] if temperature else 0,
                    "pressure": pressure[0] if pressure else 0,
                },
                "status": "connected" if plc_connection.is_connected else "simulator"
            }
            
            await manager.broadcast(data)
            
        except Exception as e:
            print(f"❌ 데이터 브로드캐스팅 오류: {e}")
        
        await asyncio.sleep(0.1)  # 100ms 주기

@app.websocket("/ws/plc-data")
async def websocket_plc_data(websocket: WebSocket):
    """PLC 데이터 실시간 스트리밍"""
    await manager.connect(websocket)
    try:
        while True:
            # 클라이언트로부터 메시지 대기
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "PLC AI Assistant API", "status": "running"}

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "plc_connected": plc_connection.is_connected,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
```

### 3.2 API 엔드포인트 (app/api/v1/endpoints/plc.py)

```python
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

from app.services.plc.connection import plc_connection
from app.services.plc.simulator import plc_simulator

router = APIRouter()

class PLCReadRequest(BaseModel):
    device: str
    count: int = 1

class PLCWriteRequest(BaseModel):
    device: str
    values: List[int]

@router.get("/status")
async def get_plc_status():
    """PLC 연결 상태 확인"""
    return {
        "connected": plc_connection.is_connected,
        "host": "192.168.1.100",
        "port": 1025,
        "simulator_running": plc_simulator.running
    }

@router.post("/connect")
async def connect_plc():
    """PLC 연결"""
    success = await plc_connection.connect()
    if success:
        return {"message": "PLC 연결 성공", "connected": True}
    else:
        # 연결 실패 시 시뮬레이터 사용
        return {"message": "PLC 연결 실패 - 시뮬레이터 모드", "connected": False}

@router.post("/disconnect")
async def disconnect_plc():
    """PLC 연결 해제"""
    await plc_connection.disconnect()
    return {"message": "PLC 연결 해제", "connected": False}

@router.post("/read")
async def read_plc_data(request: PLCReadRequest):
    """PLC 데이터 읽기"""
    if plc_connection.is_connected:
        data = await plc_connection.read_data(request.device, request.count)
        if data is not None:
            return {"device": request.device, "values": data}
        else:
            raise HTTPException(status_code=500, detail="데이터 읽기 실패")
    else:
        # 시뮬레이터에서 데이터 읽기
        value = plc_simulator.read_device(request.device)
        return {"device": request.device, "values": [value] * request.count}

@router.post("/write")
async def write_plc_data(request: PLCWriteRequest):
    """PLC 데이터 쓰기"""
    if plc_connection.is_connected:
        success = await plc_connection.write_data(request.device, request.values)
        if success:
            return {"message": "데이터 쓰기 성공", "device": request.device}
        else:
            raise HTTPException(status_code=500, detail="데이터 쓰기 실패")
    else:
        # 시뮬레이터에 데이터 쓰기
        plc_simulator.write_device(request.device, request.values[0])
        return {"message": "시뮬레이터 데이터 쓰기 성공", "device": request.device}

@router.get("/monitoring")
async def get_monitoring_data():
    """모니터링 데이터 조회"""
    if plc_connection.is_connected:
        temperature = await plc_connection.read_data("D100", 1)
        pressure = await plc_connection.read_data("D101", 1)
        speed = await plc_connection.read_data("D102", 1)
    else:
        temperature = [plc_simulator.read_device("D100")]
        pressure = [plc_simulator.read_device("D101")]
        speed = [plc_simulator.read_device("D102")]
    
    return {
        "temperature": temperature[0] if temperature else 0,
        "pressure": pressure[0] if pressure else 0,
        "speed": speed[0] if speed else 0,
        "source": "plc" if plc_connection.is_connected else "simulator"
    }
```

### 3.3 라우터 통합 (app/api/v1/router.py)

```python
from fastapi import APIRouter
from app.api.v1.endpoints import plc

api_router = APIRouter()

# PLC 관련 엔드포인트
api_router.include_router(plc.router, prefix="/plc", tags=["PLC"])

@api_router.get("/")
async def api_root():
    return {"message": "PLC AI Assistant API v1"}
```

### ✅ Phase 3 검증

```bash
# 서버 실행
poetry run python app/main.py

# 다른 터미널에서 테스트
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/plc/status
curl -X POST http://localhost:8000/api/v1/plc/connect
```

---

## 📡 Phase 4: 실시간 대시보드 (90분)

### 4.1 간단한 HTML 대시보드 (frontend/index.html)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PLC AI Assistant Dashboard</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        .status { 
            display: flex; 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .card { 
            flex: 1; 
            padding: 20px; 
            background: #f8f9fa; 
            border-radius: 8px; 
            text-align: center; 
        }
        .card h3 { margin: 0 0 10px 0; color: #333; }
        .card .value { font-size: 2em; font-weight: bold; color: #007bff; }
        .card .unit { color: #666; font-size: 0.9em; }
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
        .controls { margin: 20px 0; }
        .btn { 
            padding: 10px 20px; 
            margin: 5px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px; 
        }
        .btn-primary { background: #007bff; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .log { 
            height: 300px; 
            overflow-y: auto; 
            border: 1px solid #ddd; 
            padding: 10px; 
            background: #f8f9fa; 
            font-family: monospace; 
            font-size: 14px; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏭 PLC AI Assistant Dashboard</h1>
        
        <!-- 연결 상태 -->
        <div class="status">
            <div class="card" id="connectionStatus">
                <h3>연결 상태</h3>
                <div class="value" id="connectionValue">연결 중...</div>
            </div>
            <div class="card">
                <h3>온도</h3>
                <div class="value" id="temperature">--</div>
                <div class="unit">°C</div>
            </div>
            <div class="card">
                <h3>압력</h3>
                <div class="value" id="pressure">--</div>
                <div class="unit">bar</div>
            </div>
            <div class="card">
                <h3>마지막 업데이트</h3>
                <div class="value" id="lastUpdate">--</div>
            </div>
        </div>
        
        <!-- 제어 버튼 -->
        <div class="controls">
            <button class="btn btn-primary" onclick="connectPLC()">PLC 연결</button>
            <button class="btn btn-danger" onclick="disconnectPLC()">PLC 연결 해제</button>
            <button class="btn btn-primary" onclick="getMonitoringData()">데이터 조회</button>
        </div>
        
        <!-- 로그 -->
        <h3>📊 실시간 로그</h3>
        <div class="log" id="logArea"></div>
    </div>

    <script>
        let ws = null;
        let isConnected = false;

        // WebSocket 연결
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/plc-data`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function(event) {
                addLog('✅ WebSocket 연결 성공');
                ws.send('start');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onclose = function(event) {
                addLog('❌ WebSocket 연결 종료');
                setTimeout(connectWebSocket, 5000); // 5초 후 재연결
            };
            
            ws.onerror = function(error) {
                addLog('❌ WebSocket 오류: ' + error);
            };
        }

        // 대시보드 업데이트
        function updateDashboard(data) {
            // 온도, 압력 업데이트
            document.getElementById('temperature').textContent = data.plc_data.temperature;
            document.getElementById('pressure').textContent = data.plc_data.pressure;
            
            // 연결 상태 업데이트
            const statusElement = document.getElementById('connectionStatus');
            const valueElement = document.getElementById('connectionValue');
            
            if (data.status === 'connected') {
                statusElement.className = 'card connected';
                valueElement.textContent = '연결됨';
            } else {
                statusElement.className = 'card disconnected';
                valueElement.textContent = '시뮬레이터';
            }
            
            // 마지막 업데이트 시간
            const time = new Date(data.timestamp).toLocaleTimeString();
            document.getElementById('lastUpdate').textContent = time;
        }

        // API 호출 함수들
        async function connectPLC() {
            try {
                const response = await fetch('/api/v1/plc/connect', { method: 'POST' });
                const data = await response.json();
                addLog(`🔌 ${data.message}`);
            } catch (error) {
                addLog(`❌ 연결 오류: ${error}`);
            }
        }

        async function disconnectPLC() {
            try {
                const response = await fetch('/api/v1/plc/disconnect', { method: 'POST' });
                const data = await response.json();
                addLog(`🔌 ${data.message}`);
            } catch (error) {
                addLog(`❌ 연결 해제 오류: ${error}`);
            }
        }

        async function getMonitoringData() {
            try {
                const response = await fetch('/api/v1/plc/monitoring');
                const data = await response.json();
                addLog(`📊 모니터링 데이터: 온도=${data.temperature}°C, 압력=${data.pressure}bar`);
            } catch (error) {
                addLog(`❌ 데이터 조회 오류: ${error}`);
            }
        }

        // 로그 추가
        function addLog(message) {
            const logArea = document.getElementById('logArea');
            const time = new Date().toLocaleTimeString();
            logArea.innerHTML += `<div>[${time}] ${message}</div>`;
            logArea.scrollTop = logArea.scrollHeight;
        }

        // 페이지 로드 시 WebSocket 연결
        window.onload = function() {
            addLog('🚀 대시보드 시작');
            connectWebSocket();
        };
    </script>
</body>
</html>
```

### 4.2 정적 파일 서빙 (app/main.py에 추가)

```python
# app/main.py에 추가할 코드

from fastapi.staticfiles import StaticFiles

# 정적 파일 서빙 (frontend 폴더)
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
```

### ✅ Phase 4 검증

```bash
# 서버 실행 후 브라우저에서 확인
poetry run python app/main.py
# http://localhost:8000 접속하여 대시보드 확인
```

---

## 🤖 Phase 5: AI 통합 (120분)

### 5.1 Ollama AI 클라이언트 (app/services/ai/ollama_client.py)

```python
import aiohttp
import json
from typing import Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        
    async def generate(self, prompt: str, system: str = "") -> Optional[str]:
        """AI 텍스트 생성"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False
                }
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        logger.error(f"Ollama API 오류: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"AI 생성 오류: {e}")
            return None
    
    async def analyze_ladder_code(self, code: str) -> Dict[str, Any]:
        """래더 코드 분석"""
        system_prompt = """
        당신은 PLC 래더 로직 전문가입니다. 
        주어진 래더 코드를 분석하여 다음을 제공하세요:
        1. 안전성 점수 (0-100)
        2. 최적화 제안
        3. 잠재적 문제점
        4. 코드 품질 평가
        
        응답은 JSON 형식으로 해주세요.
        """
        
        prompt = f"""
        다음 래더 코드를 분석해주세요:
        
        {code}
        
        JSON 형식으로 응답:
        {{
            "safety_score": 점수,
            "quality_score": 점수,
            "issues": ["문제점1", "문제점2"],
            "suggestions": ["제안1", "제안2"],
            "summary": "전체 평가 요약"
        }}
        """
        
        try:
            response = await self.generate(prompt, system_prompt)
            if response:
                # JSON 파싱 시도
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    # JSON이 없으면 기본 응답
                    return {
                        "safety_score": 75,
                        "quality_score": 70,
                        "issues": ["JSON 파싱 실패"],
                        "suggestions": ["코드를 다시 확인해주세요"],
                        "summary": response[:200] + "..."
                    }
            else:
                return self._get_default_analysis()
                
        except Exception as e:
            logger.error(f"코드 분석 오류: {e}")
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """기본 분석 결과"""
        return {
            "safety_score": 60,
            "quality_score": 60,
            "issues": ["AI 분석 서비스 unavailable"],
            "suggestions": ["수동으로 코드를 검토해주세요"],
            "summary": "AI 분석을 사용할 수 없습니다. Ollama 서비스를 확인해주세요."
        }
    
    async def generate_ladder_code(self, description: str) -> str:
        """자연어 설명으로부터 래더 코드 생성"""
        system_prompt = """
        당신은 PLC 프로그래밍 전문가입니다.
        자연어 설명을 받아서 안전하고 효율적인 래더 로직을 생성하세요.
        IEC 61131-3 표준을 따르고, 주석을 포함하세요.
        """
        
        prompt = f"""
        다음 요구사항에 맞는 래더 로직을 생성해주세요:
        
        {description}
        
        다음 형식으로 응답해주세요:
        1. 입출력 할당
        2. 래더 로직 (LD, AND, OR, OUT 등)
        3. 안전 고려사항
        4. 주석 설명
        """
        
        try:
            response = await self.generate(prompt, system_prompt)
            return response if response else "AI 코드 생성을 사용할 수 없습니다."
        except Exception as e:
            logger.error(f"코드 생성 오류: {e}")
            return f"코드 생성 중 오류가 발생했습니다: {e}"

# 전역 인스턴스
ollama_client = OllamaClient()
```

### 5.2 AI API 엔드포인트 (app/api/v1/endpoints/ai.py)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.services.ai.ollama_client import ollama_client

router = APIRouter()

class CodeAnalysisRequest(BaseModel):
    code: str
    
class CodeGenerationRequest(BaseModel):
    description: str

@router.post("/analyze")
async def analyze_code(request: CodeAnalysisRequest) -> Dict[str, Any]:
    """래더 코드 분석"""
    try:
        analysis = await ollama_client.analyze_ladder_code(request.code)
        return {
            "success": True,
            "analysis": analysis,
            "message": "코드 분석 완료"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

@router.post("/generate")
async def generate_code(request: CodeGenerationRequest) -> Dict[str, Any]:
    """래더 코드 생성"""
    try:
        code = await ollama_client.generate_ladder_code(request.description)
        return {
            "success": True,
            "generated_code": code,
            "message": "코드 생성 완료"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"생성 실패: {str(e)}")

@router.get("/status")
async def ai_status():
    """AI 서비스 상태 확인"""
    try:
        # 간단한 테스트 요청
        test_response = await ollama_client.generate("Hello", "")
        return {
            "available": test_response is not None,
            "model": ollama_client.model,
            "base_url": ollama_client.base_url
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "model": ollama_client.model,
            "base_url": ollama_client.base_url
        }
```

### 5.3 AI 라우터 등록 (app/api/v1/router.py 수정)

```python
from fastapi import APIRouter
from app.api.v1.endpoints import plc, ai

api_router = APIRouter()

# PLC 관련 엔드포인트
api_router.include_router(plc.router, prefix="/plc", tags=["PLC"])

# AI 관련 엔드포인트
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])

@api_router.get("/")
async def api_root():
    return {"message": "PLC AI Assistant API v1", "features": ["PLC", "AI"]}
```

### 5.4 AI 대시보드 추가 (frontend/ai.html)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PLC AI Assistant - AI 기능</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .btn { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        textarea { width: 100%; height: 200px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: monospace; }
        .result { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .score { font-size: 1.5em; font-weight: bold; margin: 10px 0; }
        .score.good { color: #28a745; }
        .score.medium { color: #ffc107; }
        .score.bad { color: #dc3545; }
        .navigation { margin-bottom: 20px; }
        .navigation a { margin-right: 10px; padding: 8px 16px; background: #6c757d; color: white; text-decoration: none; border-radius: 4px; }
        .navigation a.active { background: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <!-- 네비게이션 -->
        <div class="navigation">
            <a href="/">대시보드</a>
            <a href="/ai.html" class="active">AI 기능</a>
        </div>
        
        <h1>🤖 PLC AI Assistant</h1>
        
        <!-- AI 상태 확인 -->
        <div class="section">
            <h2>AI 서비스 상태</h2>
            <button class="btn btn-primary" onclick="checkAIStatus()">상태 확인</button>
            <div id="aiStatus" class="result" style="display:none;"></div>
        </div>
        
        <!-- 코드 분석 -->
        <div class="section">
            <h2>📊 래더 코드 분석</h2>
            <textarea id="codeInput" placeholder="래더 코드를 입력하세요 (예: LD X001&#10;AND X002&#10;OUT Y001)">LD X001
AND X002
OUT Y001
(* 시동 버튼과 운전 모드 확인 후 모터 출력 *)</textarea>
            <br>
            <button class="btn btn-success" onclick="analyzeCode()">코드 분석</button>
            <div id="analysisResult" class="result" style="display:none;"></div>
        </div>
        
        <!-- 코드 생성 -->
        <div class="section">
            <h2>⚡ 자연어로 코드 생성</h2>
            <textarea id="descriptionInput" placeholder="원하는 기능을 자연어로 설명하세요">시동 버튼(X001)을 누르고 비상정지(X002)가 해제되어 있을 때 모터(Y001)를 운전시키는 래더 로직을 만들어주세요. 안전을 위한 인터록도 포함해주세요.</textarea>
            <br>
            <button class="btn btn-success" onclick="generateCode()">코드 생성</button>
            <div id="generationResult" class="result" style="display:none;"></div>
        </div>
    </div>

    <script>
        // AI 상태 확인
        async function checkAIStatus() {
            try {
                const response = await fetch('/api/v1/ai/status');
                const data = await response.json();
                
                const statusDiv = document.getElementById('aiStatus');
                statusDiv.style.display = 'block';
                
                if (data.available) {
                    statusDiv.innerHTML = `
                        <h3>✅ AI 서비스 사용 가능</h3>
                        <p><strong>모델:</strong> ${data.model}</p>
                        <p><strong>서버:</strong> ${data.base_url}</p>
                    `;
                    statusDiv.style.background = '#d4edda';
                } else {
                    statusDiv.innerHTML = `
                        <h3>❌ AI 서비스 사용 불가</h3>
                        <p><strong>오류:</strong> ${data.error}</p>
                        <p>Ollama 서비스가 실행되고 있는지 확인하세요.</p>
                    `;
                    statusDiv.style.background = '#f8d7da';
                }
            } catch (error) {
                document.getElementById('aiStatus').innerHTML = `<h3>❌ 연결 오류: ${error}</h3>`;
                document.getElementById('aiStatus').style.display = 'block';
                document.getElementById('aiStatus').style.background = '#f8d7da';
            }
        }
        
        // 코드 분석
        async function analyzeCode() {
            const code = document.getElementById('codeInput').value;
            if (!code.trim()) {
                alert('분석할 코드를 입력하세요.');
                return;
            }
            
            try {
                const response = await fetch('/api/v1/ai/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code })
                });
                
                const data = await response.json();
                const resultDiv = document.getElementById('analysisResult');
                resultDiv.style.display = 'block';
                
                if (data.success) {
                    const analysis = data.analysis;
                    const safetyClass = analysis.safety_score >= 80 ? 'good' : analysis.safety_score >= 60 ? 'medium' : 'bad';
                    const qualityClass = analysis.quality_score >= 80 ? 'good' : analysis.quality_score >= 60 ? 'medium' : 'bad';
                    
                    resultDiv.innerHTML = `
                        <h3>📊 분석 결과</h3>
                        <div class="score ${safetyClass}">안전성 점수: ${analysis.safety_score}/100</div>
                        <div class="score ${qualityClass}">품질 점수: ${analysis.quality_score}/100</div>
                        
                        <h4>🔍 발견된 문제점:</h4>
                        <ul>${analysis.issues.map(issue => `<li>${issue}</li>`).join('')}</ul>
                        
                        <h4>💡 개선 제안:</h4>
                        <ul>${analysis.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}</ul>
                        
                        <h4>📝 요약:</h4>
                        <p>${analysis.summary}</p>
                    `;
                    resultDiv.style.background = '#d4edda';
                } else {
                    resultDiv.innerHTML = `<h3>❌ 분석 실패</h3><p>${data.message}</p>`;
                    resultDiv.style.background = '#f8d7da';
                }
            } catch (error) {
                document.getElementById('analysisResult').innerHTML = `<h3>❌ 오류: ${error}</h3>`;
                document.getElementById('analysisResult').style.display = 'block';
                document.getElementById('analysisResult').style.background = '#f8d7da';
            }
        }
        
        // 코드 생성
        async function generateCode() {
            const description = document.getElementById('descriptionInput').value;
            if (!description.trim()) {
                alert('생성할 기능을 설명하세요.');
                return;
            }
            
            try {
                const response = await fetch('/api/v1/ai/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ description: description })
                });
                
                const data = await response.json();
                const resultDiv = document.getElementById('generationResult');
                resultDiv.style.display = 'block';
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <h3>⚡ 생성된 코드</h3>
                        <pre style="background: #f1f1f1; padding: 15px; border-radius: 5px; overflow: auto;">${data.generated_code}</pre>
                        <button class="btn btn-primary" onclick="copyToClipboard('${data.generated_code.replace(/'/g, "\\'")}')">클립보드에 복사</button>
                    `;
                    resultDiv.style.background = '#d4edda';
                } else {
                    resultDiv.innerHTML = `<h3>❌ 생성 실패</h3><p>${data.message}</p>`;
                    resultDiv.style.background = '#f8d7da';
                }
            } catch (error) {
                document.getElementById('generationResult').innerHTML = `<h3>❌ 오류: ${error}</h3>`;
                document.getElementById('generationResult').style.display = 'block';
                document.getElementById('generationResult').style.background = '#f8d7da';
            }
        }
        
        // 클립보드 복사
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                alert('클립보드에 복사되었습니다!');
            });
        }
        
        // 페이지 로드 시 AI 상태 확인
        window.onload = function() {
            checkAIStatus();
        };
    </script>
</body>
</html>
```

### ✅ Phase 5 검증

```bash
# Ollama 설치 및 모델 다운로드 (별도 터미널에서)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull codegemma:7b

# 서버 실행 후 AI 기능 테스트
poetry run python app/main.py
# http://localhost:8000/ai.html 접속하여 AI 기능 테스트
```

---

## 🧪 전체 시스템 테스트

### 종합 테스트 스크립트 (tests/test_system.py)

```python
import pytest
import asyncio
import aiohttp
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    """헬스 체크 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_plc_status():
    """PLC 상태 확인 테스트"""
    response = client.get("/api/v1/plc/status")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data
    assert "simulator_running" in data

def test_plc_connect():
    """PLC 연결 테스트"""
    response = client.post("/api/v1/plc/connect")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_plc_monitoring():
    """PLC 모니터링 데이터 테스트"""
    response = client.get("/api/v1/plc/monitoring")
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert "pressure" in data
    assert "source" in data

def test_ai_status():
    """AI 상태 확인 테스트"""
    response = client.get("/api/v1/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert "model" in data

def test_ai_code_analysis():
    """AI 코드 분석 테스트"""
    test_code = "LD X001\nAND X002\nOUT Y001"
    response = client.post("/api/v1/ai/analyze", json={"code": test_code})
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "analysis" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 🚀 실행 가이드

### 빠른 시작 스크립트 (scripts/quick_start.sh)

```bash
#!/bin/bash
echo "🚀 PLC AI Assistant 빠른 시작"

# 의존성 설치
echo "📦 의존성 설치 중..."
poetry install

# 환경 변수 확인
if [ ! -f .env ]; then
    echo "📝 .env 파일 생성 중..."
    cp .env.example .env
fi

# Redis 시작 (Docker)
echo "🔧 Redis 시작 중..."
docker run -d --name plc-redis -p 6379:6379 redis:alpine

# Ollama 확인
echo "🤖 Ollama 서비스 확인 중..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama가 설치되지 않았습니다. 설치하시겠습니까? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
        ollama serve &
        ollama pull codegemma:7b
    fi
fi

# 테스트 실행
echo "🧪 시스템 테스트 중..."
poetry run pytest tests/test_system.py -v

# 서버 시작
echo "🌐 서버 시작 중..."
poetry run python app/main.py
```

### 개발 실행 스크립트 (scripts/dev.sh)

```bash
#!/bin/bash
echo "🔧 개발 모드 시작"

# 필요한 서비스들 백그라운드 실행
redis-server --daemonize yes
ollama serve &

# 개발 서버 시작 (자동 리로드)
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎯 다음 단계 가이드

### 완료 후 체크리스트
```
✅ 서버가 http://localhost:8000에서 실행됨
✅ 대시보드가 정상 표시됨
✅ PLC 시뮬레이터 데이터가 실시간 업데이트됨
✅ AI 분석 기능이 동작함
✅ WebSocket 연결이 안정적임
```

### 확장 방향
1. **실제 PLC 연결**: 시뮬레이터를 실제 미쓰비시 PLC로 교체
2. **데이터베이스 추가**: PostgreSQL로 히스토리 데이터 저장
3. **사용자 인증**: JWT 기반 사용자 관리
4. **모바일 앱**: React Native로 모바일 모니터링
5. **클라우드 배포**: Docker + Kubernetes로 프로덕션 배포

### 문제 해결
- **PLC 연결 실패**: 네트워크 설정과 방화벽 확인
- **AI 응답 없음**: Ollama 서비스 상태와 모델 다운로드 확인
- **WebSocket 끊김**: 브라우저 개발자 도구로 네트워크 상태 확인

이 가이드를 따라 단계별로 진행하면 완전히 동작하는 PLC AI 지원 시스템을 구축할 수 있습니다! 🎉