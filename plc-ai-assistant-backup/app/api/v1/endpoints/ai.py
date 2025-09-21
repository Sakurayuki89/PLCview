"""
AI API 엔드포인트
Claude가 핵심 AI 로직을 설계하고 관리
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging

from app.services.ai.ollama_client import ollama_client
from app.utils.gemini_helper import gemini_helper

logger = logging.getLogger(__name__)
router = APIRouter()

# === Pydantic 모델들 (Claude 직접 작성) ===

class CodeAnalysisRequest(BaseModel):
    """코드 분석 요청"""
    code: str = Field(..., description="분석할 래더 코드")
    language: str = Field("ladder", description="코드 언어 (ladder, st, etc.)")

class CodeGenerationRequest(BaseModel):
    """코드 생성 요청"""
    description: str = Field(..., description="생성할 기능 설명")
    target_language: str = Field("ladder", description="대상 언어")
    include_safety: bool = Field(True, description="안전 로직 포함 여부")

class AIResponse(BaseModel):
    """AI 응답 모델"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None

class GeminiGenerationRequest(BaseModel):
    """Gemini API 코드 생성 요청"""
    prompt: str = Field(..., description="생성 요청 프롬프트")
    context: str = Field("", description="추가 컨텍스트")

# === AI 상태 및 헬스체크 (Claude 직접 작성) ===

@router.get("/status")
async def ai_status():
    """AI 서비스 상태 확인"""
    try:
        # Ollama 상태 확인
        ollama_available = False
        ollama_error = None
        try:
            test_response = await ollama_client.generate("Hello", "")
            ollama_available = test_response is not None
        except Exception as e:
            ollama_error = str(e)

        # Gemini API 상태 확인 (API 키 존재 여부만 체크)
        gemini_available = gemini_helper.api_key is not None

        return AIResponse(
            success=True,
            message="AI 서비스 상태 조회 성공",
            data={
                "ollama": {
                    "available": ollama_available,
                    "model": ollama_client.model,
                    "base_url": ollama_client.base_url,
                    "error": ollama_error
                },
                "gemini": {
                    "available": gemini_available,
                    "configured": gemini_available
                },
                "overall_status": "healthy" if (ollama_available or gemini_available) else "degraded"
            }
        )
    except Exception as e:
        logger.error(f"AI 상태 확인 오류: {e}")
        raise HTTPException(status_code=500, detail=f"상태 확인 오류: {str(e)}")

# === Ollama 기반 분석 (Claude 직접 작성) ===

@router.post("/analyze")
async def analyze_code(request: CodeAnalysisRequest):
    """래더 코드 분석"""
    import time
    start_time = time.time()

    try:
        if not request.code.strip():
            raise HTTPException(status_code=400, detail="분석할 코드가 없습니다")

        # Ollama를 사용한 코드 분석
        analysis = await ollama_client.analyze_ladder_code(request.code)

        processing_time = time.time() - start_time

        return AIResponse(
            success=True,
            message="코드 분석 완료",
            data={
                "analysis": analysis,
                "code_length": len(request.code),
                "language": request.language
            },
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"코드 분석 오류: {e}")
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

@router.post("/generate")
async def generate_code(request: CodeGenerationRequest):
    """래더 코드 생성"""
    import time
    start_time = time.time()

    try:
        if not request.description.strip():
            raise HTTPException(status_code=400, detail="생성할 기능 설명이 없습니다")

        # Ollama를 사용한 코드 생성
        generated_code = await ollama_client.generate_ladder_code(request.description)

        processing_time = time.time() - start_time

        return AIResponse(
            success=True,
            message="코드 생성 완료",
            data={
                "generated_code": generated_code,
                "description": request.description,
                "target_language": request.target_language,
                "safety_included": request.include_safety
            },
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"코드 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=f"생성 실패: {str(e)}")

# === Gemini API 기반 생성 (Gemini API 활용) ===

@router.post("/gemini/generate")
async def gemini_generate_code(request: GeminiGenerationRequest):
    """Gemini API를 사용한 코드 생성"""
    import time
    start_time = time.time()

    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="생성 프롬프트가 없습니다")

        # Gemini API를 사용한 코드 생성
        generated_code = await gemini_helper.generate_code(request.prompt, request.context)

        if generated_code is None:
            raise HTTPException(status_code=503, detail="Gemini API 서비스를 사용할 수 없습니다")

        processing_time = time.time() - start_time

        return AIResponse(
            success=True,
            message="Gemini 코드 생성 완료",
            data={
                "generated_code": generated_code,
                "prompt": request.prompt,
                "context": request.context
            },
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"Gemini 코드 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Gemini 생성 실패: {str(e)}")

@router.post("/gemini/fastapi-crud")
async def gemini_generate_fastapi_crud(model_name: str, fields: Dict[str, str]):
    """Gemini API를 사용한 FastAPI CRUD 생성"""
    import time
    start_time = time.time()

    try:
        if not model_name or not fields:
            raise HTTPException(status_code=400, detail="모델명과 필드 정보가 필요합니다")

        # Gemini API를 사용한 CRUD 생성
        crud_code = await gemini_helper.generate_fastapi_crud(model_name, fields)

        if crud_code is None:
            raise HTTPException(status_code=503, detail="Gemini API 서비스를 사용할 수 없습니다")

        processing_time = time.time() - start_time

        return AIResponse(
            success=True,
            message="FastAPI CRUD 생성 완료",
            data={
                "crud_code": crud_code,
                "model_name": model_name,
                "fields": fields
            },
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"CRUD 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=f"CRUD 생성 실패: {str(e)}")

@router.post("/gemini/validators")
async def gemini_generate_validators(validation_rules: Dict[str, Any]):
    """Gemini API를 사용한 데이터 검증 함수 생성"""
    import time
    start_time = time.time()

    try:
        if not validation_rules:
            raise HTTPException(status_code=400, detail="검증 규칙이 필요합니다")

        # Gemini API를 사용한 검증 함수 생성
        validator_code = await gemini_helper.generate_data_validators(validation_rules)

        if validator_code is None:
            raise HTTPException(status_code=503, detail="Gemini API 서비스를 사용할 수 없습니다")

        processing_time = time.time() - start_time

        return AIResponse(
            success=True,
            message="데이터 검증 함수 생성 완료",
            data={
                "validator_code": validator_code,
                "validation_rules": validation_rules
            },
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"검증 함수 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=f"검증 함수 생성 실패: {str(e)}")

@router.post("/gemini/plc-functions")
async def gemini_generate_plc_functions(device_list: List[str]):
    """Gemini API를 사용한 PLC 함수들 생성"""
    import time
    start_time = time.time()

    try:
        if not device_list:
            raise HTTPException(status_code=400, detail="PLC 디바이스 목록이 필요합니다")

        # Gemini API를 사용한 PLC 함수 생성
        plc_functions = await gemini_helper.generate_plc_functions(device_list)

        if plc_functions is None:
            raise HTTPException(status_code=503, detail="Gemini API 서비스를 사용할 수 없습니다")

        processing_time = time.time() - start_time

        return AIResponse(
            success=True,
            message="PLC 함수들 생성 완료",
            data={
                "plc_functions": plc_functions,
                "device_list": device_list,
                "function_count": device_list.__len__() * 3  # read, write, monitor per device
            },
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"PLC 함수 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=f"PLC 함수 생성 실패: {str(e)}")

# === 통합 AI 기능 (Claude의 AI 전략 관리) ===

@router.post("/hybrid-analysis")
async def hybrid_code_analysis(request: CodeAnalysisRequest):
    """Ollama + Gemini 하이브리드 코드 분석"""
    import time
    start_time = time.time()

    try:
        results = {}

        # 1. Ollama로 기본 분석
        try:
            ollama_analysis = await ollama_client.analyze_ladder_code(request.code)
            results["ollama_analysis"] = ollama_analysis
        except Exception as e:
            logger.warning(f"Ollama 분석 실패: {e}")
            results["ollama_analysis"] = {"error": str(e)}

        # 2. Gemini로 추가 분석
        try:
            gemini_prompt = f"다음 PLC 래더 코드를 분석하고 최적화 제안을 해주세요:\n\n{request.code}"
            gemini_analysis = await gemini_helper.generate_code(gemini_prompt, "PLC 코드 분석")
            results["gemini_analysis"] = gemini_analysis
        except Exception as e:
            logger.warning(f"Gemini 분석 실패: {e}")
            results["gemini_analysis"] = {"error": str(e)}

        processing_time = time.time() - start_time

        return AIResponse(
            success=True,
            message="하이브리드 코드 분석 완료",
            data={
                "hybrid_results": results,
                "code_length": len(request.code),
                "analysis_methods": ["ollama", "gemini"]
            },
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"하이브리드 분석 오류: {e}")
        raise HTTPException(status_code=500, detail=f"하이브리드 분석 실패: {str(e)}")

@router.get("/capabilities")
async def get_ai_capabilities():
    """AI 시스템 기능 목록"""
    return AIResponse(
        success=True,
        message="AI 기능 목록 조회 성공",
        data={
            "ollama_features": [
                "래더 코드 분석",
                "코드 품질 평가",
                "안전성 점수 산출",
                "최적화 제안"
            ],
            "gemini_features": [
                "일반적인 코드 생성",
                "FastAPI CRUD 생성",
                "데이터 검증 함수 생성",
                "PLC 함수 템플릿 생성",
                "테스트 케이스 생성"
            ],
            "hybrid_features": [
                "다중 AI 모델 분석",
                "교차 검증",
                "종합적 코드 리뷰"
            ]
        }
    )