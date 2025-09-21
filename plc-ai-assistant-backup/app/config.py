from pydantic_settings import BaseSettings
from typing import Optional
import platform as platform_module
import os

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
    host: str = "0.0.0.0"
    port: int = 8000

    # AI 설정
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "codegemma:7b"

    # Gemini AI 설정
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-1.5-flash"
    gemini_cli_mode: bool = True

    # 플랫폼 설정
    platform: str = "auto"
    platform_name: str = platform_module.system().lower()

    # 개발 모드
    dev_mode: bool = True

    class Config:
        env_file = ".env"

    @property
    def is_windows(self) -> bool:
        return self.platform_name == "windows"

    @property
    def is_macos(self) -> bool:
        return self.platform_name == "darwin"

    @property
    def is_linux(self) -> bool:
        return self.platform_name == "linux"

    def get_redis_command(self) -> str:
        """플랫폼별 Redis 실행 명령어 반환"""
        if self.is_windows:
            return "redis-server.exe"
        else:
            return "redis-server"

    def get_python_command(self) -> str:
        """플랫폼별 Python 명령어 반환"""
        if self.is_windows:
            return "python"
        else:
            return "python3"

settings = Settings()