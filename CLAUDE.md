# PLCview 프로젝트 운영 가이드

이 문서는 **PLC 순서도 시각화 및 AI 대화 시스템** 개발을 위한 Claude Code와 Gemini CLI 협업 가이드입니다.
최소 단위 개발로 안정성을 확보하고, 5단계 Phase별 점진적 구현을 통해 프로젝트 목표를 달성합니다.

## 🎯 프로젝트 목표

**핵심 미션**: PLC 프로그램 → 순서도 시각화 → AI 기반 Q&A 시스템 구축

### 주요 기능
1. **GXW 파일 분석**: 제어 흐름 및 비즈니스 로직 추출
2. **Mermaid.js 순서도**: 동적 시각화 및 상호작용 지원
3. **컨텍스트 인식 AI**: 순서도 기반 전문적 PLC 질답
4. **통합 웹 인터페이스**: 파일 업로드 → 분석 → 시각화 → 대화

## 📋 진행 원칙

### 5단계 Phase 접근법
```
Phase 1: 기반 구조 구축     (1-2주) ← 현재 위치
Phase 2: 웹 인터페이스     (1-2주)
Phase 3: 기본 AI 대화      (2-3주)
Phase 4: 고급 분석 기능    (3-4주)
Phase 5: 통합 및 최적화    (2-3주)
```

### 단계별 검증 원칙
- **각 Phase 완료 시 필수 검증**: 기능 테스트 → 코드 품질 → 사용자 피드백
- **10% 진행률 체크포인트**: NOWPLAN_ENHANCED.md 기준 방향성 확인
- **백워드 호환성 보장**: 기존 plc-mentor 기능 유지

### 코드 품질 관리
- **최소 단위 구현**: 클래스별, 메서드별 완전 구현 후 통합
- **테스트 우선**: 각 기능 구현 후 즉시 테스트 실행
- **문서 동기화**: 코드 변경 시 관련 문서 즉시 업데이트

## 📁 문서 체계

**핵심 문서**:
- **NOWPLAN_ENHANCED.md**: 마스터 설계도 및 5단계 로드맵
- **BUILD.md**: 현재 Phase 진행 상황 및 완성도 추적
- **HISTORY.md**: 단계별 완료 내역 및 학습 사항 기록
- **REPAIR.md**: 오류 해결 과정 및 트러블슈팅 가이드
- **Order.txt**: Gemini CLI 명령 관리 시스템 (본 협업의 핵심)

**기술 문서** (docs/ 폴더):
- 연결 가이드, 보안 정책, 문제 해결 등

## 🤖 AI 역할 분담

### Gemini CLI (코드 생성 엔진)
**주요 역할**: Order.txt 기반 구체적 코드 블록 생성

**전문 영역**:
- **PLC 분석 클래스**: EnhancedGXWParser, FlowAnalyzer 등
- **순서도 생성기**: BasicFlowGenerator, MermaidGenerator
- **Flask 라우트 확장**: /analyzer, /api/generate_flowchart 등
- **AI 서비스 레이어**: AIChatService, LLMProviders
- **프론트엔드 컴포넌트**: JavaScript, HTML 템플릿

**사용 방법**:
```bash
# Gemini CLI Flash 모델 사용
gemini-cli --model=gemini-flash

# Order.txt에서 명령 복사 → CLI에 붙여넣기
# 결과를 Claude에게 피드백 → 다음 명령 업데이트
```

### Claude Code (아키텍트 & 검토자)
**주요 역할**: 프로젝트 전체 설계, 코드 검토, 진행 관리

**핵심 담당 영역**:
- **프로젝트 아키텍처**: Phase별 진행 전략 및 의존성 관리
- **Order.txt 관리**: Gemini CLI 명령 생성 및 5회 제한 관리
- **코드 품질 관리**: 생성된 코드의 통합, 최적화, 검증
- **문서 동기화**: BUILD.md, HISTORY.md 진행률 추적
- **핵심 설정 파일**: Flask app.py, requirements.txt, 환경 설정

**품질 관리 기준**:
- 생성된 모든 코드의 문법 검증 및 최적화
- PLC 도메인 로직의 정확성 확인
- Mermaid.js 호환성 및 브라우저 렌더링 테스트
- AI 안전성 검증 (잘못된 PLC 조작 방지)

## 🔄 협업 워크플로우

### Order.txt 중심 협업 사이클
```
1. Claude가 Order.txt에 구체적 명령 작성 (최대 5개)
2. 사용자가 명령을 복사하여 Gemini CLI에 입력
3. Gemini가 요청된 코드 블록 생성
4. 사용자가 결과를 Claude에게 공유
5. Claude가 코드 검토, 통합, 최적화 수행
6. 5개 명령 완료 시 Order.txt 초기화 → 새 사이클 시작
```

### Phase별 작업 흐름
```
🎯 Phase 계획 → 📝 Order.txt 명령 → 🤖 Gemini 코드생성 → 🔍 Claude 검토 → ✅ 통합 테스트
     ↓                   ↓                    ↓                ↓              ↓
NOWPLAN 기준      5개 명령 관리        구체적 클래스/함수     품질 보증      다음 Phase
```

### 코드 생성 우선순위
**Gemini CLI 담당** (반복적, 패턴 기반):
- **PLC 파서 확장**: EnhancedGXWParser 클래스
- **순서도 생성기**: BasicFlowGenerator, MermaidGenerator
- **Flask 라우트**: /analyzer, API 엔드포인트들
- **AI 서비스**: AIChatService, LLMProviders
- **프론트엔드**: JavaScript, HTML 템플릿, CSS

**Claude 직접 작성** (핵심 로직, 아키텍처):
- **프로젝트 설정**: Flask app.py 메인 구조
- **핵심 비즈니스 로직**: PLC 안전성 검증, 데이터 흐름 제어
- **통합 및 최적화**: 생성된 코드들의 연결과 성능 최적화
- **문서 및 설정**: requirements.txt, 환경 변수, 배포 설정

## 💾 백업 및 버전 관리

### Git 브랜치 전략
```bash
main                    # 안정적인 릴리즈 버전
├── phase1-parser       # Phase 1: Enhanced GXW Parser
├── phase2-frontend     # Phase 2: 웹 인터페이스
├── phase3-ai           # Phase 3: AI 대화 시스템
├── phase4-advanced     # Phase 4: 고급 분석
└── phase5-optimize     # Phase 5: 최적화
```

### 커밋 정책
- **Phase 완료 시점**: 필수 커밋 (기능 테스트 통과 후)
- **Order.txt 사이클 완료**: 5개 명령 완료 시 중간 커밋
- **10% 진행률 달성**: NOWPLAN_ENHANCED.md 기준 진행률 커밋
- **백워드 호환성**: 기존 plc-mentor 기능 보존 상태 확인

### 자동 백업 시스템
```bash
# 로컬 백업 (Phase별)
project-root/backup/phase1/YYYYMMDD_HHMM.zip
project-root/backup/phase2/YYYYMMDD_HHMM.zip

# Git 태그 기반 마일스톤
git tag v1.0-phase1-complete
git tag v1.1-phase2-complete
```

### 회복 절차
1. **Phase 롤백**: `git checkout phase1-parser`
2. **특정 커밋**: `git checkout <commit_id>`
3. **로컬 백업**: `unzip backup/phase1/latest.zip`
4. **긴급 복구**: plc-ai-assistant-backup 참조

## 🚀 5단계 실행 절차

### Phase 1: 기반 구조 구축 (1-2주) ← **현재**
**목표**: 기존 plc-mentor를 순서도 생성 가능한 수준으로 확장

**Claude 직접 작업**:
- NOWPLAN_ENHANCED.md 기준 Phase 1 상세 계획 수립
- Order.txt에 Enhanced GXW Parser 명령 작성
- Flask 라우트 설계 및 기본 구조 확장
- 개발 환경 설정 (requirements.txt 업데이트)

**Gemini CLI 협업**:
- EnhancedGXWParser 클래스 구현 (제어 흐름 분석)
- BasicFlowGenerator 클래스 구현 (Mermaid 텍스트 생성)
- 기본 Flask 라우트 확장 (/analyzer 엔드포인트)

**완료 기준**: 간단한 GXW 파일 → 기본 Mermaid 순서도 생성 성공

### Phase 2: 웹 인터페이스 구현 (1-2주)
**목표**: 순서도 시각화 웹 인터페이스 완성

**Gemini CLI 주요 작업**:
- analyzer_view.html 템플릿 구현
- JavaScript 순서도 뷰어 (Mermaid.js 통합)
- 파일 업로드 및 진행 상황 UI
- 반응형 CSS 스타일링

**완료 기준**: 웹에서 GXW 업로드 → 순서도 표시 성공

### Phase 3: 기본 AI 대화 시스템 (2-3주)
**목표**: 순서도 기반 AI Q&A 시스템 구현

**Gemini CLI 주요 작업**:
- AIChatService 클래스 (LLM 제공자 추상화)
- WebSocket 채팅 인터페이스
- PLC 컨텍스트 프롬프트 생성기

**완료 기준**: 순서도 기반 실시간 AI 질답 성공

### Phase 4: 고급 분석 및 AI 기능 (3-4주)
**목표**: 복잡한 PLC 로직 분석 및 전문적 AI 응답

**Gemini CLI 주요 작업**:
- AdvancedFlowAnalyzer (조건부 분기, 반복문 감지)
- ContextAwareAI (대화 히스토리, 상세 컨텍스트)
- PLCSafetyValidator (안전성 검증 시스템)

**완료 기준**: 복잡한 실제 PLC 프로그램의 정확한 분석

### Phase 5: 통합 및 최적화 (2-3주)
**목표**: 프로덕션 준비 및 성능 최적화

**Claude & Gemini 협업**:
- 성능 최적화 (캐싱, 비동기 처리)
- End-to-End 테스트 스위트
- 배포 설정 및 모니터링

**완료 기준**: 전체 시스템 안정성 및 성능 목표 달성

## 📊 진행률 관리

### Order.txt 사이클 관리
- **5개 명령 완료**: Order.txt 초기화 → 새 명령 세트
- **명령 실행 로그**: 날짜, 결과, 다음 액션 기록
- **코드 품질 체크**: 각 생성 코드의 통합 및 최적화

### 문서 동기화
- **BUILD.md**: Phase별 진행 상황 실시간 업데이트
- **HISTORY.md**: 완료된 단계별 성과 및 학습 사항
- **REPAIR.md**: 오류 해결 과정 및 예방 방안 축적

### 성공 지표 추적
- 각 Phase별 기술적 완성도 (85% 이상)
- 사용자 테스트 피드백 점수 (4.0/5.0 이상)
- 시스템 안정성 및 성능 목표 달성

---
**다음 액션**: Order.txt의 첫 번째 명령을 Gemini CLI로 실행하여 Enhanced GXW Parser 구현 시작