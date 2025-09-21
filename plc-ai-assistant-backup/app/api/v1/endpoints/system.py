"""
시스템 관리 API 엔드포인트
Claude가 직접 작성한 시스템 관리 로직
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import platform
import psutil
import logging
import asyncio
from datetime import datetime

from app.config import settings
from app.services.websocket_manager import connection_manager

logger = logging.getLogger(__name__)
router = APIRouter()

# === Pydantic 모델들 ===

class SystemResponse(BaseModel):
    """시스템 응답 모델"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class SystemAlert(BaseModel):
    """시스템 알림"""
    level: str = Field(..., description="알림 레벨 (info, warning, error)")
    message: str = Field(..., description="알림 메시지")

# === 시스템 정보 엔드포인트 ===

@router.get("/info")
async def get_system_info():
    """시스템 정보 조회"""
    try:
        # 플랫폼 정보
        platform_info = {
            "system": platform.system(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()
        }

        # 시스템 리소스 정보
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        resource_info = {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        }

        # 네트워크 정보
        network_info = {
            "hostname": platform.node(),
            "network_interfaces": list(psutil.net_if_addrs().keys())
        }

        # 애플리케이션 정보
        app_info = {
            "debug_mode": settings.debug,
            "log_level": settings.log_level,
            "api_version": settings.api_v1_str,
            "host": settings.host,
            "port": settings.port,
            "plc_host": settings.plc_host,
            "plc_port": settings.plc_port,
            "redis_url": settings.redis_url
        }

        return SystemResponse(
            success=True,
            message="시스템 정보 조회 성공",
            data={
                "platform": platform_info,
                "resources": resource_info,
                "network": network_info,
                "application": app_info
            }
        )

    except Exception as e:
        logger.error(f"시스템 정보 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"시스템 정보 조회 실패: {str(e)}")

@router.get("/health")
async def detailed_health_check():
    """상세 헬스 체크"""
    try:
        health_data = {}

        # CPU 상태
        cpu_percent = psutil.cpu_percent(interval=1)
        health_data["cpu"] = {
            "usage_percent": cpu_percent,
            "status": "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
        }

        # 메모리 상태
        memory = psutil.virtual_memory()
        health_data["memory"] = {
            "usage_percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2),
            "status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
        }

        # 디스크 상태
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        health_data["disk"] = {
            "usage_percent": round(disk_percent, 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "status": "healthy" if disk_percent < 80 else "warning" if disk_percent < 95 else "critical"
        }

        # WebSocket 연결 상태
        health_data["websocket"] = {
            "active_connections": connection_manager.get_connection_count(),
            "status": "healthy"
        }

        # 전체 상태 결정
        all_statuses = [health_data[key]["status"] for key in health_data.keys()]
        if "critical" in all_statuses:
            overall_status = "critical"
        elif "warning" in all_statuses:
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return SystemResponse(
            success=True,
            message=f"시스템 상태: {overall_status}",
            data={
                "overall_status": overall_status,
                "components": health_data
            }
        )

    except Exception as e:
        logger.error(f"헬스 체크 오류: {e}")
        raise HTTPException(status_code=500, detail=f"헬스 체크 실패: {str(e)}")

# === 시스템 모니터링 ===

@router.get("/monitoring")
async def get_system_monitoring():
    """실시간 시스템 모니터링 데이터"""
    try:
        # CPU 코어별 사용률
        cpu_per_core = psutil.cpu_percent(percpu=True, interval=1)

        # 메모리 상세 정보
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # 네트워크 I/O
        network = psutil.net_io_counters()

        # 디스크 I/O
        disk_io = psutil.disk_io_counters()

        # 프로세스 정보
        current_process = psutil.Process()

        monitoring_data = {
            "cpu": {
                "overall_percent": psutil.cpu_percent(),
                "per_core": cpu_per_core,
                "core_count": len(cpu_per_core)
            },
            "memory": {
                "virtual": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent
                }
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            "disk_io": {
                "read_bytes": disk_io.read_bytes,
                "write_bytes": disk_io.write_bytes,
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count
            } if disk_io else {},
            "process": {
                "pid": current_process.pid,
                "memory_percent": current_process.memory_percent(),
                "cpu_percent": current_process.cpu_percent(),
                "num_threads": current_process.num_threads(),
                "create_time": current_process.create_time()
            }
        }

        return SystemResponse(
            success=True,
            message="시스템 모니터링 데이터 조회 성공",
            data=monitoring_data
        )

    except Exception as e:
        logger.error(f"모니터링 데이터 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"모니터링 데이터 조회 실패: {str(e)}")

# === WebSocket 관리 ===

@router.get("/websocket/status")
async def get_websocket_status():
    """WebSocket 연결 상태"""
    try:
        return SystemResponse(
            success=True,
            message="WebSocket 상태 조회 성공",
            data={
                "active_connections": connection_manager.get_connection_count(),
                "connection_manager_active": True
            }
        )
    except Exception as e:
        logger.error(f"WebSocket 상태 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"WebSocket 상태 조회 실패: {str(e)}")

@router.post("/websocket/broadcast")
async def broadcast_message(alert: SystemAlert):
    """모든 WebSocket 연결에 메시지 브로드캐스트"""
    try:
        await connection_manager.broadcast_alert(alert.level, alert.message)

        return SystemResponse(
            success=True,
            message="브로드캐스트 전송 성공",
            data={
                "level": alert.level,
                "message": alert.message,
                "sent_to": connection_manager.get_connection_count()
            }
        )
    except Exception as e:
        logger.error(f"브로드캐스트 오류: {e}")
        raise HTTPException(status_code=500, detail=f"브로드캐스트 실패: {str(e)}")

# === 로그 관리 ===

@router.get("/logs/level")
async def get_log_level():
    """현재 로그 레벨 조회"""
    return SystemResponse(
        success=True,
        message="로그 레벨 조회 성공",
        data={
            "current_level": settings.log_level,
            "available_levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        }
    )

@router.post("/logs/level/{level}")
async def set_log_level(level: str):
    """로그 레벨 변경"""
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    if level.upper() not in valid_levels:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 로그 레벨. 사용 가능: {valid_levels}")

    try:
        # 로그 레벨 변경
        logging.getLogger().setLevel(level.upper())

        return SystemResponse(
            success=True,
            message=f"로그 레벨을 {level.upper()}로 변경했습니다",
            data={
                "old_level": settings.log_level,
                "new_level": level.upper()
            }
        )
    except Exception as e:
        logger.error(f"로그 레벨 변경 오류: {e}")
        raise HTTPException(status_code=500, detail=f"로그 레벨 변경 실패: {str(e)}")

# === 설정 관리 ===

@router.get("/config")
async def get_current_config():
    """현재 애플리케이션 설정 조회"""
    config_data = {
        "platform": {
            "name": settings.platform_name,
            "is_windows": settings.is_windows,
            "is_macos": settings.is_macos,
            "is_linux": settings.is_linux
        },
        "application": {
            "debug": settings.debug,
            "dev_mode": settings.dev_mode,
            "host": settings.host,
            "port": settings.port,
            "log_level": settings.log_level,
            "api_v1_str": settings.api_v1_str
        },
        "plc": {
            "host": settings.plc_host,
            "port": settings.plc_port,
            "timeout": settings.plc_timeout
        },
        "ai": {
            "ollama_base_url": settings.ollama_base_url,
            "ollama_model": settings.ollama_model
        },
        "redis": {
            "url": settings.redis_url
        }
    }

    return SystemResponse(
        success=True,
        message="설정 조회 성공",
        data=config_data
    )

# === 시스템 유틸리티 ===

@router.post("/restart")
async def restart_application():
    """애플리케이션 재시작 (개발용)"""
    if not settings.dev_mode:
        raise HTTPException(status_code=403, detail="프로덕션 모드에서는 재시작할 수 없습니다")

    try:
        # 개발 모드에서만 재시작 신호 전송
        await connection_manager.broadcast_status("restarting", {"reason": "manual_restart"})

        # 실제 재시작은 외부 프로세스 매니저에 의존
        return SystemResponse(
            success=True,
            message="재시작 요청이 전송되었습니다",
            data={"dev_mode": True}
        )
    except Exception as e:
        logger.error(f"재시작 요청 오류: {e}")
        raise HTTPException(status_code=500, detail=f"재시작 요청 실패: {str(e)}")

@router.get("/version")
async def get_version_info():
    """버전 정보 조회"""
    return SystemResponse(
        success=True,
        message="버전 정보 조회 성공",
        data={
            "application_version": "0.1.0",
            "api_version": "v1",
            "python_version": platform.python_version(),
            "platform": platform.system(),
            "build_info": {
                "framework": "FastAPI",
                "ai_engines": ["Ollama", "Gemini"],
                "plc_protocol": "MC Protocol (Type 3E)"
            }
        }
    )