"""
Ollama AI 클라이언트
Claude Code가 직접 작성한 핵심 AI 서비스
"""
import aiohttp
import json
from typing import Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Ollama AI 클라이언트 클래스"""

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