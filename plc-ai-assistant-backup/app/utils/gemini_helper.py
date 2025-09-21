"""
Gemini CLI API 헬퍼 함수
Claude Code에서 Gemini API를 호출하여 코드 생성을 요청하는 유틸리티
"""
import json
import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GeminiAPIHelper:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-pro"

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. API calls will fail.")

    async def generate_code(self, prompt: str, context: str = "") -> Optional[str]:
        """
        Gemini API를 호출하여 코드 생성

        Args:
            prompt: 생성할 코드에 대한 구체적인 요청
            context: 추가 컨텍스트 정보

        Returns:
            생성된 코드 문자열 또는 None
        """
        if not self.api_key:
            logger.error("Gemini API key not available")
            return None

        full_prompt = f"""
        {context}

        요청: {prompt}

        다음 조건을 만족하는 코드를 생성해주세요:
        1. Python 코드로 작성
        2. 타입 힌트 포함
        3. 적절한 주석 추가
        4. PEP 8 스타일 준수
        5. 오류 처리 포함

        코드만 반환하고 설명은 제외해주세요.
        """

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "contents": [{
                        "parts": [{"text": full_prompt}]
                    }]
                }

                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }

                url = f"{self.base_url}/{self.model}:generateContent"

                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("candidates", [{}])[0].get("content", {})
                        text = content.get("parts", [{}])[0].get("text", "")

                        # 코드 블록 추출 (```python ... ``` 형태)
                        if "```python" in text:
                            start = text.find("```python") + 9
                            end = text.find("```", start)
                            if end != -1:
                                return text[start:end].strip()

                        return text.strip()
                    else:
                        logger.error(f"Gemini API error: {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Failed to call Gemini API: {e}")
            return None

    async def generate_fastapi_crud(self, model_name: str, fields: Dict[str, str]) -> Optional[str]:
        """
        FastAPI CRUD 엔드포인트 생성

        Args:
            model_name: 모델 이름 (예: "User", "Product")
            fields: 필드 정의 {"field_name": "field_type"}

        Returns:
            생성된 CRUD 코드
        """
        fields_str = ", ".join([f"{name}: {type_}" for name, type_ in fields.items()])

        prompt = f"""
        {model_name} 모델에 대한 FastAPI CRUD 엔드포인트를 생성해주세요.

        모델 필드: {fields_str}

        다음을 포함해주세요:
        1. Pydantic 모델 (Create, Update, Response)
        2. CRUD 함수들 (create, read, update, delete)
        3. FastAPI 라우터 엔드포인트들
        4. 적절한 HTTP 상태 코드
        5. 오류 처리
        """

        return await self.generate_code(prompt)

    async def generate_data_validators(self, validation_rules: Dict[str, Any]) -> Optional[str]:
        """
        데이터 검증 함수들 생성

        Args:
            validation_rules: 검증 규칙들

        Returns:
            생성된 검증 함수들
        """
        rules_str = json.dumps(validation_rules, indent=2)

        prompt = f"""
        다음 검증 규칙에 따른 데이터 검증 함수들을 생성해주세요:

        {rules_str}

        각 검증 함수는 다음을 포함해야 합니다:
        1. 입력값 검증
        2. 적절한 예외 발생
        3. 타입 힌트
        4. 문서화 문자열
        """

        return await self.generate_code(prompt)

    async def generate_test_cases(self, function_name: str, function_code: str) -> Optional[str]:
        """
        테스트 케이스 생성

        Args:
            function_name: 테스트할 함수 이름
            function_code: 함수 코드

        Returns:
            생성된 테스트 코드
        """
        prompt = f"""
        다음 함수에 대한 pytest 테스트 케이스들을 생성해주세요:

        함수명: {function_name}

        ```python
        {function_code}
        ```

        다음을 포함하는 테스트를 생성해주세요:
        1. 정상 케이스 테스트
        2. 경계값 테스트
        3. 예외 상황 테스트
        4. Mock 사용 (필요한 경우)
        5. 비동기 함수인 경우 @pytest.mark.asyncio 사용
        """

        return await self.generate_code(prompt)

    async def generate_plc_functions(self, device_list: list) -> Optional[str]:
        """
        PLC 디바이스별 읽기/쓰기 함수들 생성

        Args:
            device_list: PLC 디바이스 목록 ["D100", "M101", ...]

        Returns:
            생성된 PLC 함수들
        """
        devices_str = ", ".join(device_list)

        prompt = f"""
        다음 PLC 디바이스들에 대한 읽기/쓰기 함수들을 생성해주세요:

        디바이스 목록: {devices_str}

        각 디바이스마다 다음 함수들을 생성해주세요:
        1. read_[device_name]() - 디바이스 값 읽기
        2. write_[device_name](value) - 디바이스 값 쓰기
        3. monitor_[device_name]() - 실시간 모니터링

        함수 특징:
        - 비동기 함수로 작성
        - 타입 힌트 포함
        - 오류 처리 포함
        - pymcprotocol 라이브러리 사용
        """

        return await self.generate_code(prompt)

# 전역 인스턴스
gemini_helper = GeminiAPIHelper()