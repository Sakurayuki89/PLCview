# PowerShell 스크립트 - Windows용 PLC AI Assistant 시작 스크립트
# Claude Code가 작성한 크로스 플랫폼 지원 스크립트

param(
    [switch]$Dev,
    [switch]$Setup,
    [switch]$Clean,
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000
)

Write-Host "🚀 PLC AI Assistant - Windows 시작 스크립트" -ForegroundColor Green
Write-Host "=" * 50

# 에러 처리 설정
$ErrorActionPreference = "Stop"

# 가상환경 활성화 함수
function Activate-VirtualEnv {
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        Write-Host "📦 가상환경 활성화 중..." -ForegroundColor Yellow
        & .\venv\Scripts\Activate.ps1
    }
    elseif (Test-Path ".\.venv\Scripts\Activate.ps1") {
        Write-Host "📦 가상환경 활성화 중..." -ForegroundColor Yellow
        & .\.venv\Scripts\Activate.ps1
    }
    else {
        Write-Host "⚠️ 가상환경을 찾을 수 없습니다. Poetry를 사용합니다." -ForegroundColor Yellow
    }
}

# 의존성 설치 함수
function Install-Dependencies {
    Write-Host "📦 의존성 설치 중..." -ForegroundColor Yellow

    # Poetry 확인
    try {
        poetry --version | Out-Null
        Write-Host "✅ Poetry 발견" -ForegroundColor Green
        poetry install
    }
    catch {
        Write-Host "❌ Poetry를 찾을 수 없습니다." -ForegroundColor Red
        Write-Host "📥 Poetry 설치: https://python-poetry.org/docs/#installation" -ForegroundColor Yellow

        # pip 대안
        Write-Host "🔄 pip로 의존성 설치 시도..." -ForegroundColor Yellow
        if (Test-Path "requirements.txt") {
            pip install -r requirements.txt
        }
        else {
            Write-Host "❌ requirements.txt 파일이 없습니다." -ForegroundColor Red
            exit 1
        }
    }
}

# Redis 시작 함수
function Start-Redis {
    Write-Host "🔧 Redis 상태 확인 중..." -ForegroundColor Yellow

    # Redis 프로세스 확인
    $redisProcess = Get-Process redis-server -ErrorAction SilentlyContinue
    if ($redisProcess) {
        Write-Host "✅ Redis가 이미 실행 중입니다." -ForegroundColor Green
        return
    }

    # Redis 실행 시도
    try {
        # Chocolatey Redis
        if (Get-Command redis-server -ErrorAction SilentlyContinue) {
            Write-Host "🚀 Redis 시작 중..." -ForegroundColor Yellow
            Start-Process redis-server -WindowStyle Hidden
            Start-Sleep 3
        }
        # Docker Redis
        elseif (Get-Command docker -ErrorAction SilentlyContinue) {
            Write-Host "🐳 Docker Redis 시작 중..." -ForegroundColor Yellow
            docker run -d --name plc-redis -p 6379:6379 redis:alpine
        }
        else {
            Write-Host "⚠️ Redis를 찾을 수 없습니다. 애플리케이션은 Redis 없이 시작됩니다." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️ Redis 시작 실패: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Ollama 상태 확인 함수
function Check-Ollama {
    Write-Host "🤖 Ollama 상태 확인 중..." -ForegroundColor Yellow

    try {
        $ollamaTest = Invoke-RestMethod -Uri "http://localhost:11434/api/version" -Method Get -TimeoutSec 5
        Write-Host "✅ Ollama 서비스 실행 중" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Ollama 서비스를 찾을 수 없습니다." -ForegroundColor Yellow
        Write-Host "📥 Ollama 설치: https://ollama.ai/download/windows" -ForegroundColor Yellow
    }
}

# 환경변수 설정 함수
function Set-Environment {
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Write-Host "📝 .env 파일 생성 중..." -ForegroundColor Yellow
            Copy-Item ".env.example" ".env"
        }
        else {
            Write-Host "📝 기본 .env 파일 생성 중..." -ForegroundColor Yellow
            @"
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
HOST=$Host
PORT=$Port

# AI 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codegemma:7b

# 플랫폼 설정
PLATFORM=windows
DEV_MODE=true
"@ | Out-File -FilePath ".env" -Encoding UTF8
        }
    }
    Write-Host "✅ 환경 설정 완료" -ForegroundColor Green
}

# 프리 체크 함수
function Test-Prerequisites {
    Write-Host "🔍 사전 요구사항 확인 중..." -ForegroundColor Yellow

    # Python 확인
    try {
        $pythonVersion = python --version
        Write-Host "✅ $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Python을 찾을 수 없습니다." -ForegroundColor Red
        Write-Host "📥 Python 설치: https://www.python.org/downloads/windows/" -ForegroundColor Yellow
        exit 1
    }

    # PowerShell 실행 정책 확인
    $executionPolicy = Get-ExecutionPolicy
    if ($executionPolicy -eq "Restricted") {
        Write-Host "⚠️ PowerShell 실행 정책이 제한되어 있습니다." -ForegroundColor Yellow
        Write-Host "🔧 다음 명령어로 변경하세요: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    }
}

# 메인 실행 로직
try {
    # 사전 요구사항 확인
    Test-Prerequisites

    # 셋업 모드
    if ($Setup) {
        Write-Host "🔧 초기 설정 모드" -ForegroundColor Cyan
        Install-Dependencies
        Set-Environment
        Start-Redis
        Check-Ollama
        Write-Host "✅ 설정 완료! 이제 -Dev 플래그로 서버를 시작하세요." -ForegroundColor Green
        exit 0
    }

    # 클린 모드
    if ($Clean) {
        Write-Host "🧹 정리 모드" -ForegroundColor Cyan

        # 임시 파일 정리
        if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }
        if (Test-Path "*.pyc") { Remove-Item -Force "*.pyc" }
        if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }

        Write-Host "✅ 정리 완료" -ForegroundColor Green
        exit 0
    }

    # 환경 설정
    Set-Environment

    # 의존성 확인 및 설치
    if (-not (Test-Path "pyproject.toml")) {
        Write-Host "❌ pyproject.toml을 찾을 수 없습니다." -ForegroundColor Red
        exit 1
    }

    # 가상환경 활성화
    Activate-VirtualEnv

    # 서비스 시작
    if (-not $Dev) {
        Start-Redis
        Check-Ollama
    }

    # 서버 시작
    Write-Host "🌐 서버 시작 중..." -ForegroundColor Green
    Write-Host "📍 주소: http://$Host`:$Port" -ForegroundColor Green
    Write-Host "📖 API 문서: http://$Host`:$Port/docs" -ForegroundColor Green
    Write-Host "🛑 중지: Ctrl+C" -ForegroundColor Yellow

    if ($Dev) {
        # 개발 모드
        Write-Host "🔧 개발 모드로 시작 중..." -ForegroundColor Cyan
        if (Get-Command poetry -ErrorAction SilentlyContinue) {
            poetry run python app/main.py
        }
        else {
            python app/main.py
        }
    }
    else {
        # 프로덕션 모드
        Write-Host "🚀 프로덕션 모드로 시작 중..." -ForegroundColor Cyan
        if (Get-Command poetry -ErrorAction SilentlyContinue) {
            poetry run uvicorn app.main:app --host $Host --port $Port --reload
        }
        else {
            uvicorn app.main:app --host $Host --port $Port --reload
        }
    }
}
catch {
    Write-Host "❌ 오류 발생: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "📋 스택 트레이스:" -ForegroundColor Yellow
    Write-Host $_.ScriptStackTrace -ForegroundColor Yellow
    exit 1
}
finally {
    Write-Host "🛑 PLC AI Assistant 종료" -ForegroundColor Yellow
}