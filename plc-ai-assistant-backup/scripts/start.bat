@echo off
REM Windows Batch 스크립트 - PLC AI Assistant 시작
REM Claude Code가 작성한 크로스 플랫폼 지원 스크립트

echo 🚀 PLC AI Assistant - Windows 배치 스크립트
echo ==================================================

REM 변수 설정
set HOST=127.0.0.1
set PORT=8000
set DEV_MODE=false

REM 인자 처리
:parse_args
if "%1"=="--dev" set DEV_MODE=true
if "%1"=="--setup" goto setup_mode
if "%1"=="--clean" goto clean_mode
if "%1"=="--host" (
    set HOST=%2
    shift
)
if "%1"=="--port" (
    set PORT=%2
    shift
)
shift
if not "%1"=="" goto parse_args

REM 사전 요구사항 확인
echo 🔍 사전 요구사항 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python을 찾을 수 없습니다.
    echo 📥 Python 설치: https://www.python.org/downloads/windows/
    pause
    exit /b 1
)
echo ✅ Python 확인 완료

REM pyproject.toml 확인
if not exist "pyproject.toml" (
    echo ❌ pyproject.toml을 찾을 수 없습니다.
    echo 📁 올바른 프로젝트 디렉토리에서 실행하세요.
    pause
    exit /b 1
)

REM .env 파일 생성
if not exist ".env" (
    echo 📝 .env 파일 생성 중...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
    ) else (
        echo # PLC 설정 > .env
        echo PLC_HOST=192.168.1.100 >> .env
        echo PLC_PORT=1025 >> .env
        echo PLC_TIMEOUT=5 >> .env
        echo. >> .env
        echo # Redis 설정 >> .env
        echo REDIS_URL=redis://localhost:6379 >> .env
        echo. >> .env
        echo # 애플리케이션 설정 >> .env
        echo DEBUG=true >> .env
        echo LOG_LEVEL=INFO >> .env
        echo API_V1_STR=/api/v1 >> .env
        echo HOST=%HOST% >> .env
        echo PORT=%PORT% >> .env
        echo. >> .env
        echo # AI 설정 >> .env
        echo OLLAMA_BASE_URL=http://localhost:11434 >> .env
        echo OLLAMA_MODEL=codegemma:7b >> .env
        echo. >> .env
        echo # 플랫폼 설정 >> .env
        echo PLATFORM=windows >> .env
        echo DEV_MODE=true >> .env
    )
    echo ✅ 환경 설정 완료
)

REM 의존성 설치
echo 📦 의존성 확인 중...
poetry --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Poetry를 찾을 수 없습니다. pip를 사용합니다.
    if exist "requirements.txt" (
        pip install -r requirements.txt
    ) else (
        echo ❌ requirements.txt 파일이 없습니다.
        echo 📥 Poetry 설치를 권장합니다: https://python-poetry.org/docs/
        pause
        exit /b 1
    )
) else (
    echo ✅ Poetry 발견
    poetry install
)

REM Redis 시작 (선택적)
echo 🔧 Redis 확인 중...
tasklist | find "redis-server" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Redis가 실행되지 않고 있습니다.

    REM Redis 시작 시도
    redis-server --version >nul 2>&1
    if not errorlevel 1 (
        echo 🚀 Redis 시작 중...
        start /min redis-server
        timeout /t 3 /nobreak >nul
    ) else (
        REM Docker로 Redis 시작 시도
        docker --version >nul 2>&1
        if not errorlevel 1 (
            echo 🐳 Docker Redis 시작 중...
            docker run -d --name plc-redis -p 6379:6379 redis:alpine >nul 2>&1
        ) else (
            echo ⚠️ Redis를 찾을 수 없습니다. 애플리케이션은 Redis 없이 시작됩니다.
        )
    )
) else (
    echo ✅ Redis 실행 중
)

REM Ollama 확인
echo 🤖 Ollama 확인 중...
curl -s http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Ollama 서비스를 찾을 수 없습니다.
    echo 📥 Ollama 설치: https://ollama.ai/download/windows
) else (
    echo ✅ Ollama 서비스 실행 중
)

REM 서버 시작
echo.
echo 🌐 서버 시작 중...
echo 📍 주소: http://%HOST%:%PORT%
echo 📖 API 문서: http://%HOST%:%PORT%/docs
echo 🛑 중지: Ctrl+C
echo.

if "%DEV_MODE%"=="true" (
    echo 🔧 개발 모드로 시작 중...
    poetry run python app/main.py
) else (
    echo 🚀 프로덕션 모드로 시작 중...
    poetry run uvicorn app.main:app --host %HOST% --port %PORT% --reload
)

goto end

:setup_mode
echo 🔧 초기 설정 모드
echo.
echo 📦 의존성 설치 중...
poetry install
echo.
echo 📝 환경 설정 중...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env"
    )
)
echo.
echo ✅ 설정 완료! 이제 start.bat --dev로 서버를 시작하세요.
pause
exit /b 0

:clean_mode
echo 🧹 정리 모드
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist ".pytest_cache" rmdir /s /q ".pytest_cache"
del /s /q "*.pyc" >nul 2>&1
echo ✅ 정리 완료
pause
exit /b 0

:end
echo.
echo 🛑 PLC AI Assistant 종료
pause