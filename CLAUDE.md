이 문서는 초보 개발자가 Vibe Coding 기법을 활용하여 Claude Code 환경에서 프로젝트를 구축할 때,
최소 단위로 안정적으로 개발하고 오류를 줄이며 AI Agent의 도움을 받을 수 있도록 안내하는 프로젝트 운영 가이드이다.

진행 원칙

단계적 진행 (Step-by-Step)

프로젝트는 반드시 1단계식으로 진행한다.

한 단계가 완료되면 테스트를 수행하고, 문제가 없을 때만 다음 단계로 넘어간다.

코드 최소화

함수와 변수는 따로 정리하여 재사용성을 확보한다.

불필요한 중복 코드를 줄이고, 최소 단위 기능부터 쌓아 올린다.

10% 검증 규칙

프로젝트의 진행도가 10% 이상 증가할 때마다 반드시 BUILD.md를 기준으로 검증한다.

만약 방향성이 벗어나면 즉시 수정하고 기록한다.

문서 관리

BUILD.md : 프로젝트의 설계도 및 목표 구조.

HISTORY.md : 단계별 진행 내역 기록.

REPAIR.md : 오류 발생 시 해결 과정 및 대안 기록.

CLAUDE.md : 프로젝트 전체 운영 원칙과 절차 안내 (본 문서).

AI 역할 분담

Gemini CLI API (작성자 역할)

- API 호출을 통한 코드 생성 및 수정 담당
- 함수/변수 단위로 최소화된 코드를 빠르게 작성
- 반복적이고 패턴이 있는 코드 생성에 특화
- Claude가 요청하는 구체적인 코드 블록을 생성

Gemini CLI 설정 및 사용:
```bash
# .env 파일 설정 (프로젝트 루트/plc-ai-assistant/.env)
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-pro
GEMINI_CLI_MODE=true

# Gemini CLI 직접 사용 예시
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent" \
  -H "Content-Type: application/json" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -d '{
    "contents": [{
      "parts": [{"text": "Python FastAPI PLC 데이터 읽기 함수 생성"}]
    }]
  }'

# 또는 Python을 통한 Gemini API 호출
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('FastAPI 엔드포인트 코드 생성')
print(response.text)
"
```

Claude Code (검토자/핵심코드 담당)

- 프로젝트 전체 아키텍처 설계 및 진행 관리
- Gemini가 생성한 코드의 검토, 통합, 최적화
- 핵심 비즈니스 로직과 중요한 설정 파일 직접 작성
- BUILD.md와 HISTORY.md 기준 진행률 관리 및 검증
- 오류 분석 및 REPAIR.md 기록 관리
- 10% 진행률마다 검증 루프 실행

핵심 담당 영역:
- config.py (설정 관리)
- main.py (애플리케이션 진입점)
- 데이터베이스 모델 및 스키마
- API 라우터 구조
- 보안 및 인증 로직

협업 방식

1. Claude가 Gemini CLI API에 구체적인 코드 생성 요청
2. Gemini CLI API가 요청된 코드 블록을 생성
3. Claude가 생성된 코드를 검토, 통합, 최적화
4. Claude가 핵심 코드와 아키텍처 설계 직접 작성
5. 10% 진행률마다 Claude가 전체 검증 수행

작업 흐름:
```
Claude 설계 → Gemini API 코드생성 → Claude 검토 → Claude 핵심코드 → 통합 테스트
    ↓                                    ↓
  요구사항 분석                        오류 수정 및 최적화
```

API 호출 예시:
- 반복 코드: "PLC 데이터 읽기 함수 10개 생성"
- 템플릿 코드: "FastAPI CRUD 엔드포인트 생성"
- 유틸리티 함수: "데이터 검증 헬퍼 함수들"

Claude 직접 작성:
- 프로젝트 구조 및 설정
- 비즈니스 로직 핵심 부분
- 보안 및 인증 시스템
- 데이터베이스 모델링

백업 및 코드 회복

GitHub 버전 관리

모든 작업은 Git을 사용해 버전 관리한다.

커밋 단위는 "단계별 완료" 또는 "10% 진행" 시점으로 제한한다.

로컬 백업

하루 1회 이상 project-root/backup/날짜/ 디렉토리에 압축 저장.

코드 회복 절차

GitHub: git checkout <commit_id>

로컬 백업: unzip backup_YYYYMMDD.zip -d ./restore/

자동 백업 루프

진행률 10% 증가 시 GitHub push + 로컬 zip 백업을 동시에 수행.

절차

1단계: 초기 설정 (Claude 주도)
- BUILD.md 검토 및 프로젝트 구조 설계
- .env 파일 설정 (Gemini API 키 포함)
- 핵심 설정 파일 (config.py, pyproject.toml) 직접 작성
- Gemini CLI 연동 테스트 및 검증
- 기본 디렉토리 구조 생성
- 환경 설정 및 의존성 관리
- GitHub 초기 커밋 및 로컬 백업

2단계: 기능 단위 개발 (협업)
- Claude가 요구사항 분석 및 코드 명세 작성
- Gemini CLI API 호출하여 반복/템플릿 코드 생성
- Claude가 생성된 코드 검토, 통합, 최적화
- Claude가 핵심 비즈니스 로직 직접 작성
- 테스트 성공 후 HISTORY.md 업데이트
- GitHub commit + 로컬 백업

3단계: 오류 처리 (Claude 주도)
- Claude가 오류 원인 분석 및 디버깅
- 필요시 Gemini CLI API로 수정 코드 생성 요청
- Claude가 최종 오류 수정 및 검증
- 해결 과정을 REPAIR.md에 상세 기록

4단계: 검증 루프 (Claude 전담)
- 10%, 20%, ... 진행률마다 Claude가 전체 검증
- 아키텍처 일관성 및 코드 품질 검토
- 성능 및 보안 검증
- 검증 통과 후 백업 수행

5단계: 완성 (Claude 주도)
- Claude가 최종 통합 테스트 및 검증
- 배포 준비 및 문서 정리
- Gemini CLI API로 필요시 문서 생성 보조
- 프로젝트 완료 및 배포

Gemini CLI API 활용 영역:
- 반복적인 CRUD 함수들
- 데이터 검증 헬퍼 함수들
- 테스트 케이스 생성
- API 엔드포인트 템플릿
- 문서 및 주석 생성