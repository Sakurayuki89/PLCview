#!/usr/bin/env python3
"""
Cross-platform Redis setup script for PLC AI Assistant
"""
import platform
import subprocess
import sys
import os
import urllib.request
import zipfile
import shutil

def detect_platform():
    """플랫폼 감지"""
    system = platform.system().lower()
    print(f"🔍 감지된 플랫폼: {system}")
    return system

def check_command_exists(command):
    """명령어 존재 여부 확인"""
    try:
        subprocess.run([command, "--version"],
                      capture_output=True,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_redis_windows():
    """Windows Redis 설치"""
    print("🪟 Windows Redis 설치 중...")

    # Redis가 이미 설치되어 있는지 확인
    if check_command_exists("redis-server"):
        print("✅ Redis가 이미 설치되어 있습니다.")
        return True

    print("📦 Windows용 Redis 설치 옵션:")
    print("1. Chocolatey 사용: choco install redis")
    print("2. Windows Subsystem for Linux (WSL) 사용")
    print("3. Docker 사용: docker run -d --name redis -p 6379:6379 redis:alpine")
    print("4. 수동 설치")

    choice = input("선택하세요 (1-4): ").strip()

    if choice == "1":
        try:
            subprocess.run(["choco", "install", "redis"], check=True)
            print("✅ Chocolatey로 Redis 설치 완료")
            return True
        except subprocess.CalledProcessError:
            print("❌ Chocolatey가 설치되어 있지 않거나 오류가 발생했습니다.")
            return False

    elif choice == "3":
        try:
            subprocess.run([
                "docker", "run", "-d",
                "--name", "redis",
                "-p", "6379:6379",
                "redis:alpine"
            ], check=True)
            print("✅ Docker로 Redis 설치 완료")
            return True
        except subprocess.CalledProcessError:
            print("❌ Docker가 설치되어 있지 않거나 오류가 발생했습니다.")
            return False

    else:
        print("🔧 수동 설치 가이드:")
        print("1. https://github.com/microsoftarchive/redis/releases 에서 Redis 다운로드")
        print("2. 압축 해제 후 redis-server.exe 실행")
        print("3. 환경변수 PATH에 Redis 경로 추가")
        return False

def install_redis_macos():
    """macOS Redis 설치"""
    print("🍎 macOS Redis 설치 중...")

    if check_command_exists("redis-server"):
        print("✅ Redis가 이미 설치되어 있습니다.")
        return True

    # Homebrew 확인
    if check_command_exists("brew"):
        try:
            subprocess.run(["brew", "install", "redis"], check=True)
            print("✅ Homebrew로 Redis 설치 완료")

            # 서비스 시작
            subprocess.run(["brew", "services", "start", "redis"], check=True)
            print("✅ Redis 서비스 시작")
            return True
        except subprocess.CalledProcessError:
            print("❌ Homebrew Redis 설치 실패")
    else:
        print("❌ Homebrew가 설치되어 있지 않습니다.")
        print("🔧 Homebrew 설치: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")

    return False

def install_redis_linux():
    """Linux Redis 설치"""
    print("🐧 Linux Redis 설치 중...")

    if check_command_exists("redis-server"):
        print("✅ Redis가 이미 설치되어 있습니다.")
        return True

    # 패키지 매니저별 설치 시도
    try:
        # Ubuntu/Debian
        if check_command_exists("apt"):
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "redis-server"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "redis-server"], check=True)
            subprocess.run(["sudo", "systemctl", "start", "redis-server"], check=True)
            print("✅ APT로 Redis 설치 완료")
            return True

        # CentOS/RHEL/Fedora
        elif check_command_exists("dnf"):
            subprocess.run(["sudo", "dnf", "install", "-y", "redis"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "redis"], check=True)
            subprocess.run(["sudo", "systemctl", "start", "redis"], check=True)
            print("✅ DNF로 Redis 설치 완료")
            return True

        elif check_command_exists("yum"):
            subprocess.run(["sudo", "yum", "install", "-y", "redis"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "redis"], check=True)
            subprocess.run(["sudo", "systemctl", "start", "redis"], check=True)
            print("✅ YUM으로 Redis 설치 완료")
            return True

    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 매니저 설치 실패: {e}")

    # Docker 대안
    if check_command_exists("docker"):
        try:
            subprocess.run([
                "docker", "run", "-d",
                "--name", "redis",
                "-p", "6379:6379",
                "redis:alpine"
            ], check=True)
            print("✅ Docker로 Redis 설치 완료")
            return True
        except subprocess.CalledProcessError:
            print("❌ Docker Redis 설치 실패")

    return False

def test_redis_connection():
    """Redis 연결 테스트"""
    print("🔧 Redis 연결 테스트 중...")

    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis 연결 성공!")
        return True
    except ImportError:
        print("❌ redis-py 패키지가 설치되어 있지 않습니다.")
        print("📦 설치: pip install redis")
        return False
    except Exception as e:
        print(f"❌ Redis 연결 실패: {e}")
        print("🔧 Redis 서버가 실행 중인지 확인하세요.")
        return False

def main():
    """메인 함수"""
    print("🚀 PLC AI Assistant - Redis 설정")
    print("=" * 50)

    platform_name = detect_platform()

    success = False
    if platform_name == "windows":
        success = install_redis_windows()
    elif platform_name == "darwin":
        success = install_redis_macos()
    elif platform_name == "linux":
        success = install_redis_linux()
    else:
        print(f"❌ 지원하지 않는 플랫폼: {platform_name}")
        return False

    if success:
        print("\n🧪 Redis 연결 테스트...")
        test_redis_connection()

    print("\n📝 다음 단계:")
    print("1. Redis 서버가 실행 중인지 확인")
    print("2. .env 파일에서 REDIS_URL 설정 확인")
    print("3. 애플리케이션 실행")

    return success

if __name__ == "__main__":
    main()