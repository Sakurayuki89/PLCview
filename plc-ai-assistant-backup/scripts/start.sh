#!/bin/bash
# Bash 스크립트 - macOS/Linux용 PLC AI Assistant 시작 스크립트
# Claude Code가 작성한 크로스 플랫폼 지원 스크립트

set -e  # 오류 시 즉시 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 기본 설정
HOST="127.0.0.1"
PORT=8000
DEV_MODE=false
SETUP_MODE=false
CLEAN_MODE=false

# 도움말 함수
show_help() {
    echo -e "${GREEN}🚀 PLC AI Assistant - macOS/Linux 시작 스크립트${NC}"
    echo "=================================================="
    echo
    echo "사용법: $0 [옵션]"
    echo
    echo "옵션:"
    echo "  --dev           개발 모드로 시작"
    echo "  --setup         초기 설정 수행"
    echo "  --clean         임시 파일 정리"
    echo "  --host HOST     서버 호스트 (기본값: 127.0.0.1)"
    echo "  --port PORT     서버 포트 (기본값: 8000)"
    echo "  --help          이 도움말 표시"
    echo
    echo "예시:"
    echo "  $0 --setup                   # 초기 설정"
    echo "  $0 --dev                     # 개발 모드 시작"
    echo "  $0 --host 0.0.0.0 --port 8080 # 커스텀 호스트/포트"
}

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV_MODE=true
            shift
            ;;
        --setup)
            SETUP_MODE=true
            shift
            ;;
        --clean)
            CLEAN_MODE=true
            shift
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 알 수 없는 옵션: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 플랫폼 감지
detect_platform() {
    case "$(uname -s)" in
        Darwin*)
            PLATFORM="macos"
            echo -e "${BLUE}🍎 macOS 환경에서 실행${NC}"
            ;;
        Linux*)
            PLATFORM="linux"
            echo -e "${BLUE}🐧 Linux 환경에서 실행${NC}"
            ;;
        *)
            PLATFORM="unknown"
            echo -e "${YELLOW}⚠️ 알 수 없는 플랫폼${NC}"
            ;;
    esac
}

# 사전 요구사항 확인
check_prerequisites() {
    echo -e "${YELLOW}🔍 사전 요구사항 확인 중...${NC}"

    # Python 확인
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3을 찾을 수 없습니다.${NC}"
        if [[ "$PLATFORM" == "macos" ]]; then
            echo -e "${YELLOW}📥 Homebrew로 설치: brew install python3${NC}"
        else
            echo -e "${YELLOW}📥 패키지 매니저로 설치: sudo apt install python3 python3-pip${NC}"
        fi
        exit 1
    fi
    echo -e "${GREEN}✅ Python 3 확인 완료${NC}"

    # pyproject.toml 확인
    if [[ ! -f "pyproject.toml" ]]; then
        echo -e "${RED}❌ pyproject.toml을 찾을 수 없습니다.${NC}"
        echo -e "${YELLOW}📁 올바른 프로젝트 디렉토리에서 실행하세요.${NC}"
        exit 1
    fi
}

# 환경 설정 함수
setup_environment() {
    if [[ ! -f ".env" ]]; then
        echo -e "${YELLOW}📝 .env 파일 생성 중...${NC}"
        if [[ -f ".env.example" ]]; then
            cp ".env.example" ".env"
        else
            cat > .env << EOF
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
HOST=$HOST
PORT=$PORT

# AI 설정
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codegemma:7b

# 플랫폼 설정
PLATFORM=$PLATFORM
DEV_MODE=true
EOF
        fi
    fi
    echo -e "${GREEN}✅ 환경 설정 완료${NC}"
}

# 의존성 설치 함수
install_dependencies() {
    echo -e "${YELLOW}📦 의존성 설치 중...${NC}"

    # Poetry 확인
    if command -v poetry &> /dev/null; then
        echo -e "${GREEN}✅ Poetry 발견${NC}"
        poetry install
    else
        echo -e "${YELLOW}⚠️ Poetry를 찾을 수 없습니다.${NC}"

        # Poetry 설치 제안
        echo -e "${YELLOW}📥 Poetry 설치 중...${NC}"
        if [[ "$PLATFORM" == "macos" ]]; then
            if command -v brew &> /dev/null; then
                brew install poetry
            else
                curl -sSL https://install.python-poetry.org | python3 -
            fi
        else
            curl -sSL https://install.python-poetry.org | python3 -
        fi

        # PATH 업데이트
        export PATH="$HOME/.local/bin:$PATH"

        # 재시도
        if command -v poetry &> /dev/null; then
            poetry install
        else
            echo -e "${YELLOW}🔄 pip로 의존성 설치 시도...${NC}"
            if [[ -f "requirements.txt" ]]; then
                pip3 install -r requirements.txt
            else
                echo -e "${RED}❌ requirements.txt 파일이 없습니다.${NC}"
                exit 1
            fi
        fi
    fi
}

# Redis 시작 함수
start_redis() {
    echo -e "${YELLOW}🔧 Redis 상태 확인 중...${NC}"

    # Redis 프로세스 확인
    if pgrep -f redis-server > /dev/null; then
        echo -e "${GREEN}✅ Redis가 이미 실행 중입니다.${NC}"
        return
    fi

    # Redis 시작 시도
    if command -v redis-server &> /dev/null; then
        echo -e "${YELLOW}🚀 Redis 시작 중...${NC}"
        redis-server --daemonize yes
        sleep 2
    elif command -v docker &> /dev/null; then
        echo -e "${YELLOW}🐳 Docker Redis 시작 중...${NC}"
        docker run -d --name plc-redis -p 6379:6379 redis:alpine > /dev/null 2>&1 || true
    else
        echo -e "${YELLOW}⚠️ Redis를 찾을 수 없습니다.${NC}"
        if [[ "$PLATFORM" == "macos" ]]; then
            echo -e "${YELLOW}📥 Homebrew로 설치: brew install redis${NC}"
        else
            echo -e "${YELLOW}📥 패키지 매니저로 설치: sudo apt install redis-server${NC}"
        fi
    fi
}

# Ollama 확인 함수
check_ollama() {
    echo -e "${YELLOW}🤖 Ollama 상태 확인 중...${NC}"

    if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ollama 서비스 실행 중${NC}"
    else
        echo -e "${YELLOW}⚠️ Ollama 서비스를 찾을 수 없습니다.${NC}"
        if [[ "$PLATFORM" == "macos" ]]; then
            echo -e "${YELLOW}📥 설치: brew install ollama${NC}"
            echo -e "${YELLOW}또는 https://ollama.ai/download/mac${NC}"
        else
            echo -e "${YELLOW}📥 설치: curl -fsSL https://ollama.ai/install.sh | sh${NC}"
        fi
    fi
}

# 정리 함수
clean_project() {
    echo -e "${CYAN}🧹 정리 모드${NC}"

    # Python 캐시 정리
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

    # 로그 파일 정리
    find . -type f -name "*.log" -delete 2>/dev/null || true

    echo -e "${GREEN}✅ 정리 완료${NC}"
}

# 서버 시작 함수
start_server() {
    echo -e "${GREEN}🌐 서버 시작 중...${NC}"
    echo -e "${GREEN}📍 주소: http://$HOST:$PORT${NC}"
    echo -e "${GREEN}📖 API 문서: http://$HOST:$PORT/docs${NC}"
    echo -e "${YELLOW}🛑 중지: Ctrl+C${NC}"
    echo

    if [[ "$DEV_MODE" == "true" ]]; then
        echo -e "${CYAN}🔧 개발 모드로 시작 중...${NC}"
        if command -v poetry &> /dev/null; then
            poetry run python app/main.py
        else
            python3 app/main.py
        fi
    else
        echo -e "${CYAN}🚀 프로덕션 모드로 시작 중...${NC}"
        if command -v poetry &> /dev/null; then
            poetry run uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
        else
            uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
        fi
    fi
}

# 메인 실행 로직
main() {
    echo -e "${GREEN}🚀 PLC AI Assistant - macOS/Linux 시작 스크립트${NC}"
    echo "=================================================="

    # 플랫폼 감지
    detect_platform

    # 정리 모드
    if [[ "$CLEAN_MODE" == "true" ]]; then
        clean_project
        exit 0
    fi

    # 사전 요구사항 확인
    check_prerequisites

    # 셋업 모드
    if [[ "$SETUP_MODE" == "true" ]]; then
        echo -e "${CYAN}🔧 초기 설정 모드${NC}"
        install_dependencies
        setup_environment
        start_redis
        check_ollama
        echo -e "${GREEN}✅ 설정 완료! 이제 --dev 플래그로 서버를 시작하세요.${NC}"
        exit 0
    fi

    # 환경 설정
    setup_environment

    # 서비스 시작 (개발 모드가 아닐 때)
    if [[ "$DEV_MODE" != "true" ]]; then
        start_redis
        check_ollama
    fi

    # 서버 시작
    start_server
}

# 트랩 설정 (Ctrl+C 처리)
trap 'echo -e "\n${YELLOW}🛑 PLC AI Assistant 종료${NC}"; exit 0' INT

# 스크립트 실행
main "$@"