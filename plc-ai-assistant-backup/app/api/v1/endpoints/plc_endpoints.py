"""
PLC API 엔드포인트
GX Works2와 연동을 위한 REST API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
import asyncio
import random
from datetime import datetime

router = APIRouter()

# PLC 시뮬레이터 데이터 (Virtual Mode)
virtual_plc_data = {
    # 데이터 레지스터 (D)
    "D0": 25,    # 온도
    "D2": 850,   # 압력
    "D4": 1200,  # 속도
    "D6": 15,    # 카운터
    "D100": 28,  # 온도 센서
    "D106": 920, # 압력 센서
    "D110": 1350, # 속도 센서
    "D111": 1,   # 상태값

    # 비트 디바이스 (X, Y, M, SM)
    "X0": False,   # 입력
    "X204": True,  # 센서 입력
    "Y45": False,  # 출력
    "M0": True,    # 내부 릴레이
    "M30": False,  # 내부 릴레이
    "SM400": True, # 시스템 모니터
    "SM410": False # 에러 플래그
}

class PLCConnectResponse(BaseModel):
    success: bool
    message: str
    connection_info: Optional[Dict[str, Any]] = None

class PLCReadResponse(BaseModel):
    device: str
    value: Any
    timestamp: str
    source: str = "virtual_plc"

class PLCWriteRequest(BaseModel):
    value: Any

class PLCWriteResponse(BaseModel):
    success: bool
    device: str
    old_value: Any
    new_value: Any
    timestamp: str

@router.post("/connect", response_model=PLCConnectResponse)
async def connect_plc():
    """PLC 연결"""
    try:
        # Virtual PLC 연결 시뮬레이션
        await asyncio.sleep(0.1)  # 연결 지연 시뮬레이션

        return PLCConnectResponse(
            success=True,
            message="Virtual PLC 연결 성공",
            connection_info={
                "host": "127.0.0.1",
                "port": 1025,
                "protocol": "MC Protocol 3E",
                "mode": "Virtual",
                "connected_at": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연결 실패: {str(e)}")

@router.post("/disconnect", response_model=PLCConnectResponse)
async def disconnect_plc():
    """PLC 연결 해제"""
    return PLCConnectResponse(
        success=True,
        message="PLC 연결 해제됨",
        connection_info={
            "disconnected_at": datetime.now().isoformat()
        }
    )

@router.get("/status")
async def get_plc_status():
    """PLC 상태 확인"""
    return {
        "status": "connected",
        "mode": "virtual",
        "host": "127.0.0.1",
        "port": 1025,
        "protocol": "MC Protocol 3E",
        "uptime": "operational",
        "last_update": datetime.now().isoformat(),
        "device_count": len(virtual_plc_data),
        "virtual_plc_active": True
    }

@router.get("/read/{device}", response_model=PLCReadResponse)
async def read_device(device: str):
    """디바이스 값 읽기"""
    device = device.upper()

    if device not in virtual_plc_data:
        raise HTTPException(
            status_code=404,
            detail=f"디바이스 {device}를 찾을 수 없습니다"
        )

    # Virtual PLC에서 값에 약간의 변동 추가 (실제 PLC 시뮬레이션)
    value = virtual_plc_data[device]

    if device.startswith('D') and isinstance(value, (int, float)):
        # 데이터 레지스터는 약간의 랜덤 변동
        variation = random.randint(-5, 5)
        value = max(0, value + variation)
        virtual_plc_data[device] = value
    elif device.startswith(('X', 'Y', 'M', 'SM')):
        # 비트 디바이스는 가끔 상태 변경
        if random.random() < 0.1:  # 10% 확률로 상태 변경
            value = not value
            virtual_plc_data[device] = value

    return PLCReadResponse(
        device=device,
        value=value,
        timestamp=datetime.now().isoformat(),
        source="virtual_plc"
    )

@router.post("/write/{device}", response_model=PLCWriteResponse)
async def write_device(device: str, request: PLCWriteRequest):
    """디바이스 값 쓰기"""
    device = device.upper()

    if device not in virtual_plc_data:
        raise HTTPException(
            status_code=404,
            detail=f"디바이스 {device}를 찾을 수 없습니다"
        )

    old_value = virtual_plc_data[device]
    new_value = request.value

    # 값 유효성 검사
    if device.startswith(('X', 'Y', 'M', 'SM')):
        # 비트 디바이스는 Boolean 값만
        if not isinstance(new_value, bool):
            raise HTTPException(
                status_code=400,
                detail=f"비트 디바이스 {device}는 boolean 값만 허용됩니다"
            )
    elif device.startswith('D'):
        # 데이터 레지스터는 숫자 값만
        if not isinstance(new_value, (int, float)):
            raise HTTPException(
                status_code=400,
                detail=f"데이터 레지스터 {device}는 숫자 값만 허용됩니다"
            )
        # 범위 제한 (16bit signed: -32768 ~ 32767)
        if not (-32768 <= new_value <= 32767):
            raise HTTPException(
                status_code=400,
                detail=f"값 {new_value}가 범위를 벗어났습니다 (-32768 ~ 32767)"
            )

    # 값 설정
    virtual_plc_data[device] = new_value

    return PLCWriteResponse(
        success=True,
        device=device,
        old_value=old_value,
        new_value=new_value,
        timestamp=datetime.now().isoformat()
    )

@router.get("/devices")
async def list_devices():
    """사용 가능한 모든 디바이스 목록"""
    devices = {}

    for device, value in virtual_plc_data.items():
        device_type = "unknown"
        description = ""

        if device.startswith('D'):
            device_type = "data_register"
            if device in ["D0", "D100"]:
                description = "온도 센서"
            elif device in ["D2", "D106"]:
                description = "압력 센서"
            elif device in ["D4", "D110"]:
                description = "속도 센서"
            elif device == "D6":
                description = "카운터"
            else:
                description = "데이터 레지스터"
        elif device.startswith('X'):
            device_type = "input"
            description = "입력 디바이스"
        elif device.startswith('Y'):
            device_type = "output"
            description = "출력 디바이스"
        elif device.startswith('M'):
            device_type = "internal_relay"
            description = "내부 릴레이"
        elif device.startswith('SM'):
            device_type = "system"
            description = "시스템 디바이스"

        devices[device] = {
            "type": device_type,
            "value": value,
            "description": description,
            "last_update": datetime.now().isoformat()
        }

    return {
        "total_devices": len(devices),
        "devices": devices,
        "virtual_mode": True,
        "timestamp": datetime.now().isoformat()
    }