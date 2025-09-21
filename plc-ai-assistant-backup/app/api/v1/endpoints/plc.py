"""
PLC API 엔드포인트
Claude가 핵심 로직을 설계하고 Gemini API로 생성된 코드를 통합
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from app.services.plc.connection import plc_connection
from app.services.plc.simulator import plc_simulator

logger = logging.getLogger(__name__)
router = APIRouter()

# === Pydantic 모델들 (Claude 직접 작성) ===

class PLCDeviceRead(BaseModel):
    """PLC 디바이스 읽기 요청"""
    device: str = Field(..., description="디바이스 주소 (예: D100, M101)")
    count: int = Field(1, ge=1, le=100, description="읽을 데이터 개수")

class PLCDeviceWrite(BaseModel):
    """PLC 디바이스 쓰기 요청"""
    device: str = Field(..., description="디바이스 주소")
    values: List[int] = Field(..., description="쓸 데이터 값들")

class PLCBatchRead(BaseModel):
    """PLC 일괄 읽기 요청"""
    devices: Dict[str, int] = Field(..., description="디바이스와 개수 매핑")

class PLCResponse(BaseModel):
    """PLC 응답 모델"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# === 헬퍼 함수들 (Claude 직접 작성) ===

async def get_plc_source():
    """현재 PLC 데이터 소스 확인"""
    if plc_connection.is_connected:
        return "plc", plc_connection
    else:
        return "simulator", plc_simulator

def validate_device_address(device: str) -> bool:
    """디바이스 주소 유효성 검사"""
    valid_prefixes = ['D', 'M', 'X', 'Y', 'R', 'B']
    if not device or len(device) < 2:
        return False
    return device[0].upper() in valid_prefixes

# === 기본 상태 엔드포인트 (Claude 직접 작성) ===

@router.get("/status")
async def get_plc_status():
    """PLC 연결 상태 확인"""
    connection_status = await plc_connection.get_connection_status()
    simulator_stats = plc_simulator.get_statistics()

    return PLCResponse(
        success=True,
        message="PLC 상태 조회 성공",
        data={
            "connection": connection_status,
            "simulator": simulator_stats,
            "current_source": "plc" if plc_connection.is_connected else "simulator"
        }
    )

@router.post("/connect")
async def connect_plc():
    """PLC 연결"""
    try:
        success = await plc_connection.connect()
        if success:
            return PLCResponse(
                success=True,
                message="PLC 연결 성공",
                data={"connected": True, "source": "plc"}
            )
        else:
            return PLCResponse(
                success=False,
                message="PLC 연결 실패 - 시뮬레이터 모드로 동작",
                data={"connected": False, "source": "simulator"}
            )
    except Exception as e:
        logger.error(f"PLC 연결 오류: {e}")
        raise HTTPException(status_code=500, detail=f"연결 오류: {str(e)}")

@router.post("/disconnect")
async def disconnect_plc():
    """PLC 연결 해제"""
    try:
        await plc_connection.disconnect()
        return PLCResponse(
            success=True,
            message="PLC 연결 해제 완료",
            data={"connected": False}
        )
    except Exception as e:
        logger.error(f"PLC 연결 해제 오류: {e}")
        raise HTTPException(status_code=500, detail=f"연결 해제 오류: {str(e)}")

# === 데이터 읽기/쓰기 엔드포인트 (Gemini API 생성 코드를 Claude가 검토/통합) ===

@router.post("/read")
async def read_plc_data(request: PLCDeviceRead):
    """PLC 디바이스 데이터 읽기"""
    # 디바이스 주소 검증
    if not validate_device_address(request.device):
        raise HTTPException(status_code=400, detail="유효하지 않은 디바이스 주소")

    try:
        source_type, source = await get_plc_source()

        if source_type == "plc":
            # 실제 PLC에서 읽기
            data = await source.read_data(request.device, request.count)
            if data is not None:
                return PLCResponse(
                    success=True,
                    message="PLC 데이터 읽기 성공",
                    data={
                        "device": request.device,
                        "values": data,
                        "count": len(data),
                        "source": "plc"
                    }
                )
            else:
                raise HTTPException(status_code=500, detail="PLC 데이터 읽기 실패")
        else:
            # 시뮬레이터에서 읽기
            value = source.read_device(request.device)
            values = [value] * request.count
            return PLCResponse(
                success=True,
                message="시뮬레이터 데이터 읽기 성공",
                data={
                    "device": request.device,
                    "values": values,
                    "count": len(values),
                    "source": "simulator"
                }
            )

    except Exception as e:
        logger.error(f"데이터 읽기 오류: {e}")
        raise HTTPException(status_code=500, detail=f"읽기 오류: {str(e)}")

@router.post("/write")
async def write_plc_data(request: PLCDeviceWrite):
    """PLC 디바이스 데이터 쓰기"""
    # 디바이스 주소 검증
    if not validate_device_address(request.device):
        raise HTTPException(status_code=400, detail="유효하지 않은 디바이스 주소")

    if not request.values:
        raise HTTPException(status_code=400, detail="쓸 데이터가 없습니다")

    try:
        source_type, source = await get_plc_source()

        if source_type == "plc":
            # 실제 PLC에 쓰기
            success = await source.write_data(request.device, request.values)
            if success:
                return PLCResponse(
                    success=True,
                    message="PLC 데이터 쓰기 성공",
                    data={
                        "device": request.device,
                        "values": request.values,
                        "source": "plc"
                    }
                )
            else:
                raise HTTPException(status_code=500, detail="PLC 데이터 쓰기 실패")
        else:
            # 시뮬레이터에 쓰기
            source.write_device(request.device, request.values[0])
            return PLCResponse(
                success=True,
                message="시뮬레이터 데이터 쓰기 성공",
                data={
                    "device": request.device,
                    "values": request.values,
                    "source": "simulator"
                }
            )

    except Exception as e:
        logger.error(f"데이터 쓰기 오류: {e}")
        raise HTTPException(status_code=500, detail=f"쓰기 오류: {str(e)}")

@router.post("/batch-read")
async def batch_read_plc_data(request: PLCBatchRead):
    """PLC 여러 디바이스 일괄 읽기"""
    # 모든 디바이스 주소 검증
    for device in request.devices.keys():
        if not validate_device_address(device):
            raise HTTPException(status_code=400, detail=f"유효하지 않은 디바이스 주소: {device}")

    try:
        source_type, source = await get_plc_source()
        results = {}

        if source_type == "plc":
            # 실제 PLC에서 일괄 읽기
            results = await source.batch_read_multiple(request.devices)
        else:
            # 시뮬레이터에서 일괄 읽기
            for device, count in request.devices.items():
                value = source.read_device(device)
                results[device] = [value] * count

        return PLCResponse(
            success=True,
            message="일괄 읽기 성공",
            data={
                "devices": results,
                "source": source_type,
                "total_devices": len(results)
            }
        )

    except Exception as e:
        logger.error(f"일괄 읽기 오류: {e}")
        raise HTTPException(status_code=500, detail=f"일괄 읽기 오류: {str(e)}")

# === 모니터링 엔드포인트 (Claude 직접 작성) ===

@router.get("/monitoring")
async def get_monitoring_data():
    """PLC 모니터링 데이터 조회"""
    try:
        source_type, source = await get_plc_source()

        # 주요 모니터링 디바이스들
        monitoring_devices = {
            "D100": 1,  # 온도
            "D101": 1,  # 압력
            "D102": 1,  # 속도
            "D103": 1,  # 생산량
            "M100": 1,  # 시스템 상태
            "M101": 1,  # 알람
        }

        if source_type == "plc":
            data = await source.batch_read_multiple(monitoring_devices)
            # 데이터 포맷 정리
            formatted_data = {
                "temperature": data.get("D100", [0])[0],
                "pressure": data.get("D101", [0])[0],
                "speed": data.get("D102", [0])[0],
                "production_count": data.get("D103", [0])[0],
                "system_running": bool(data.get("M100", [False])[0]),
                "alarm_active": bool(data.get("M101", [False])[0]),
            }
        else:
            formatted_data = {
                "temperature": source.read_device("D100"),
                "pressure": source.read_device("D101"),
                "speed": source.read_device("D102"),
                "production_count": source.read_device("D103"),
                "system_running": source.read_device("M100"),
                "alarm_active": source.read_device("M101"),
            }

        return PLCResponse(
            success=True,
            message="모니터링 데이터 조회 성공",
            data={
                "monitoring": formatted_data,
                "source": source_type
            }
        )

    except Exception as e:
        logger.error(f"모니터링 데이터 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"모니터링 조회 오류: {str(e)}")

# === 시뮬레이터 제어 엔드포인트 ===

@router.post("/simulator/reset")
async def reset_simulator():
    """시뮬레이터 리셋"""
    try:
        plc_simulator.reset_counters()
        return PLCResponse(
            success=True,
            message="시뮬레이터 리셋 완료",
            data={"action": "reset"}
        )
    except Exception as e:
        logger.error(f"시뮬레이터 리셋 오류: {e}")
        raise HTTPException(status_code=500, detail=f"리셋 오류: {str(e)}")

@router.get("/simulator/devices")
async def get_simulator_devices():
    """시뮬레이터 디바이스 목록 조회"""
    try:
        device_list = plc_simulator.get_device_list()
        all_data = plc_simulator.get_all_data()

        return PLCResponse(
            success=True,
            message="시뮬레이터 디바이스 조회 성공",
            data={
                "device_list": device_list,
                "device_count": len(device_list),
                "current_values": all_data
            }
        )
    except Exception as e:
        logger.error(f"디바이스 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"조회 오류: {str(e)}")

# === 웹 인터페이스용 GET 엔드포인트 추가 ===

# Virtual PLC 데이터 (웹 인터페이스용)
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

@router.get("/device/{device}")
async def read_device_simple(device: str):
    """단일 디바이스 읽기 (웹 인터페이스용)"""
    device = device.upper()

    if device not in virtual_plc_data:
        raise HTTPException(
            status_code=404,
            detail=f"디바이스 {device}를 찾을 수 없습니다"
        )

    # 시뮬레이션을 위한 약간의 변동
    value = virtual_plc_data[device]

    if device.startswith('D') and isinstance(value, (int, float)):
        import random
        variation = random.randint(-5, 5)
        value = max(0, value + variation)
        virtual_plc_data[device] = value
    elif device.startswith(('X', 'Y', 'M', 'SM')):
        import random
        if random.random() < 0.1:  # 10% 확률로 상태 변경
            value = not value
            virtual_plc_data[device] = value

    return {
        "success": True,
        "device": device,
        "value": value,
        "timestamp": "2025-09-20T14:58:00Z",
        "source": "virtual_plc"
    }

@router.post("/device/{device}/write")
async def write_device_simple(device: str, value: dict):
    """단일 디바이스 쓰기 (웹 인터페이스용)"""
    device = device.upper()

    if device not in virtual_plc_data:
        raise HTTPException(
            status_code=404,
            detail=f"디바이스 {device}를 찾을 수 없습니다"
        )

    new_value = value.get("value")
    old_value = virtual_plc_data[device]

    # 값 유효성 검사
    if device.startswith(('X', 'Y', 'M', 'SM')):
        if not isinstance(new_value, bool):
            raise HTTPException(
                status_code=400,
                detail=f"비트 디바이스 {device}는 boolean 값만 허용됩니다"
            )
    elif device.startswith('D'):
        if not isinstance(new_value, (int, float)):
            raise HTTPException(
                status_code=400,
                detail=f"데이터 레지스터 {device}는 숫자 값만 허용됩니다"
            )
        if not (-32768 <= new_value <= 32767):
            raise HTTPException(
                status_code=400,
                detail=f"값 {new_value}가 범위를 벗어났습니다 (-32768 ~ 32767)"
            )

    virtual_plc_data[device] = new_value

    return {
        "success": True,
        "device": device,
        "old_value": old_value,
        "new_value": new_value,
        "timestamp": "2025-09-20T14:58:00Z"
    }

@router.get("/devices")
async def get_all_devices():
    """모든 디바이스 목록과 값 조회"""
    return {
        "success": True,
        "total_devices": len(virtual_plc_data),
        "devices": virtual_plc_data,
        "virtual_mode": True,
        "timestamp": "2025-09-20T14:58:00Z"
    }