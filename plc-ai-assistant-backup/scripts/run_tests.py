#!/usr/bin/env python3
"""
테스트 실행 스크립트
다양한 테스트 시나리오를 위한 유틸리티
"""
import subprocess
import sys
import argparse
import os
from pathlib import Path


def run_command(cmd, description=""):
    """명령어 실행 헬퍼"""
    print(f"\n🔄 {description}")
    print(f"실행: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ 성공")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ 실패")
        if result.stderr:
            print(result.stderr)

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="PLCview 테스트 실행기")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "quick", "full"],
        default="quick",
        help="테스트 유형 선택"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="코드 커버리지 리포트 생성"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="상세 출력"
    )

    args = parser.parse_args()

    # 프로젝트 루트로 이동
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("🧪 PLCview 테스트 실행기")
    print(f"📁 작업 디렉토리: {project_root}")
    print(f"📋 테스트 유형: {args.type}")

    success = True

    # 기본 pytest 옵션
    pytest_cmd = ["python", "-m", "pytest"]

    if args.verbose:
        pytest_cmd.append("-v")

    if args.coverage:
        pytest_cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])

    # 테스트 유형별 실행
    if args.type == "quick":
        # 빠른 테스트만 실행 (하드웨어 의존성 제외)
        pytest_cmd.extend(["-m", "not hardware", "tests/"])
        success = run_command(pytest_cmd, "빠른 테스트 실행")

    elif args.type == "unit":
        # 단위 테스트만 실행
        pytest_cmd.extend(["tests/unit/"])
        success = run_command(pytest_cmd, "단위 테스트 실행")

    elif args.type == "integration":
        # 통합 테스트만 실행
        pytest_cmd.extend(["tests/integration/"])
        success = run_command(pytest_cmd, "통합 테스트 실행")

    elif args.type == "all":
        # 모든 테스트 실행 (하드웨어 테스트 포함)
        pytest_cmd.extend(["tests/"])
        success = run_command(pytest_cmd, "전체 테스트 실행")

    elif args.type == "full":
        # 전체 검증 파이프라인
        print("\n🔍 전체 검증 파이프라인 시작")

        # 1. 코드 스타일 검사
        success &= run_command(
            ["python", "-m", "black", "--check", "app/"],
            "코드 포맷팅 검사 (Black)"
        )

        # 2. 타입 검사
        success &= run_command(
            ["python", "-m", "mypy", "app/"],
            "타입 검사 (MyPy)"
        )

        # 3. 린팅
        success &= run_command(
            ["python", "-m", "flake8", "app/"],
            "린팅 검사 (Flake8)"
        )

        # 4. 보안 검사
        try:
            success &= run_command(
                ["python", "-m", "bandit", "-r", "app/"],
                "보안 검사 (Bandit)"
            )
        except:
            print("⚠️ Bandit 미설치, 보안 검사 스킵")

        # 5. 테스트 실행
        pytest_cmd.extend(["--cov=app", "--cov-report=html", "tests/"])
        success &= run_command(pytest_cmd, "전체 테스트 + 커버리지")

    # 결과 출력
    if success:
        print("\n🎉 모든 검증 통과!")
        sys.exit(0)
    else:
        print("\n💥 일부 검증 실패")
        sys.exit(1)


if __name__ == "__main__":
    main()