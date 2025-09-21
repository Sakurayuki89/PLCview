"""
API 라우터 - 메인 라우터
Claude Code가 직접 작성한 API 구조
"""
from fastapi import APIRouter
from app.api.v1.endpoints import plc, ai, system

api_router = APIRouter()

# PLC 관련 엔드포인트
api_router.include_router(
    plc.router,
    prefix="/plc",
    tags=["PLC"],
    responses={404: {"description": "Not found"}}
)

# AI 관련 엔드포인트
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI"],
    responses={404: {"description": "Not found"}}
)

# 시스템 관리 엔드포인트
api_router.include_router(
    system.router,
    prefix="/system",
    tags=["System"],
    responses={404: {"description": "Not found"}}
)


@api_router.get("/")
async def api_root():
    """API 루트 엔드포인트"""
    return {
        "message": "PLC AI Assistant API v1",
        "version": "0.1.0",
        "features": ["PLC Communication", "AI Analysis", "Real-time Monitoring"],
        "documentation": "/docs",
        "health_check": "/health"
    }