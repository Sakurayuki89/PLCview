# NOWPLAN_ENHANCED.md

## 프로젝트 목표 (Project Goal)

기존의 PLC 코드 변환 및 학습 기능을 넘어, PLC 프로그램 전체를 분석하여 비즈니스 로직의 흐름을 시각적인 순서도(Flowchart)로 제공하고, 사용자가 코드의 특정 부분에 대해 자연어로 질문하고 답변을 받을 수 있는 대화형 AI 분석 시스템을 구축합니다.

## 주요 기능 (Key Features)

### 1. **강화된 PLC 프로그램 분석 엔진**:
*   업로드된 PLC 프로그램 파일(`.gxw` 등)의 전체 로직을 파싱합니다.
*   **[신규]** 제어 흐름 명령어 지원: CJ(조건부 점프), CALL(서브루틴), END(종료), FOR/NEXT(반복문)
*   프로그램의 시작점, 분기 조건, 병렬 처리, 종료점 등을 식별하여 구조화된 데이터로 변환합니다.
*   **[개선]** 네트워크별 의존성 분석 및 실행 순서 추적 기능 추가
*   각 순서(Step) 또는 네트워크(Network) 별로 사용되는 접점(Contacts), 코일(Coils), 데이터 레지스터(Data Registers) 및 실행 조건을 추출합니다.

### 2. **지능형 순서도 시각화 (Intelligent Flowchart Visualization)**:
*   **[개선]** 단계별 구현: 기본 선형 순서도 → 조건부 분기 → 복잡한 제어 구조
*   분석된 데이터 구조를 기반으로 프로그램의 전체 흐름을 나타내는 순서도를 웹 화면에 동적으로 생성합니다.
*   **[신규]** Mermaid.js 기반 반응형 순서도 렌더링 (확대/축소, 노드 클릭 상호작용)
*   순서도의 각 기호(시작, 처리, 조건, 분기 등)는 PLC 코드의 해당 부분과 매핑됩니다.
*   **[신규]** 순서도 노드별 상세 정보 팝오버 (디바이스 정보, 실행 조건, 안전성 수준)
*   각 기호에는 해당 로직의 조건, 동작, 관련 변수 등의 요약 정보가 표시됩니다.

### 3. **컨텍스트 인식 AI Q&A 시스템 (Context-Aware AI Q&A System)**:
*   **[개선]** 단계별 AI 통합: Mock AI → Ollama(로컬) → OpenAI/Gemini(클라우드)
*   사용자가 순서도 또는 코드에 대해 궁금한 점을 텍스트로 입력할 수 있는 입력창을 제공합니다.
*   **[신규]** 실시간 WebSocket 기반 대화 인터페이스
*   AI는 분석된 PLC 프로그램의 컨텍스트(순서도, 변수, 로직 흐름)를 바탕으로 사용자의 질문에 답변합니다.
*   **[신규]** 대화 히스토리 관리 및 컨텍스트 지속성 보장
*   **[신규]** PLC 안전성 검증: 위험한 조작 명령 차단 및 안전 가이드 제공
*   예시 질문: "D100 레지스터는 어디에서 사용되나요?", "M20 코일이 ON 되는 조건은 무엇인가요?", "이 부분의 로직을 더 쉽게 설명해줘."

### 4. **통합 사용자 인터페이스 (Integrated User Interface)**:
*   **[개선]** 반응형 웹 디자인: 데스크톱, 태블릿, 모바일 지원
*   파일 업로드, 순서도 표시, Q&A 채팅창이 통합된 단일 페이지 웹 애플리케이션을 제공합니다.
*   **[신규]** 진행 상황 표시: 파일 분석 → 순서도 생성 → AI 초기화 단계별 피드백

## 기술 스택 및 변경 사항 (Tech Stack & Changes)

### **Backend (Flask) - 기존 plc-mentor 확장**:

#### 핵심 파일 수정:
*   **`app.py`**:
    - 새로운 라우트 추가: `/analyzer`, `/api/generate_flowchart`, `/api/ai_chat`
    - WebSocket 지원을 위한 Flask-SocketIO 통합
    - 파일 업로드 보안 강화 (파일 크기 제한, 확장자 검증)

*   **`plc-mentor/app/parser/gxw_parser.py`**:
    - **[확장]** `EnhancedGXWParser` 클래스 추가
    - 제어 흐름 분석 메서드: `extract_control_flow()`, `analyze_branches()`
    - 성능 최적화: 대용량 파일 청킹 처리

#### 신규 파일 추가:
*   **`plc-mentor/app/analyzer/flow_analyzer.py`**:
    - `FlowNode`, `FlowGraph`, `MermaidGenerator` 클래스 구현
    - 조건부 분기, 반복문, 서브루틴 감지 알고리즘
    - Mermaid.js 호환 텍스트 생성 엔진

*   **`plc-mentor/app/services/ai_chat_service.py`**:
    - `BasicAIChatService` 클래스: LLM 제공자 추상화
    - `ContextAwareAI` 클래스: 순서도 컨텍스트 기반 답변 생성
    - `PLCSafetyValidator` 클래스: AI 응답 안전성 검증

*   **`plc-mentor/app/services/llm_providers.py`**:
    - `OpenAIProvider`, `OllamaProvider`, `MockAIProvider` 클래스
    - LLM API 호출 최적화 및 오류 처리

*   **`plc-mentor/app/models/flow_models.py`**:
    - Pydantic 기반 데이터 모델: `FlowchartData`, `ChatMessage`, `PLCContext`

*   **`plc-mentor/app/educator/plc_educator.py`**:
    - **[수정]** 순서도 데이터를 AI 컨텍스트로 활용하는 기능 추가
    - 전문 PLC 지식베이스 통합: 안전 규칙, 업계 베스트 프랙티스

### **Frontend - 현대적 웹 인터페이스**:

#### 신규 템플릿:
*   **`plc-mentor/templates/analyzer_view.html`**:
    - 순서도와 Q&A 인터페이스를 담을 메인 템플릿
    - 반응형 3-패널 레이아웃: 파일 업로드 | 순서도 | 채팅
    - 접근성(Accessibility) 지원: 키보드 네비게이션, 스크린 리더 호환

#### JavaScript 라이브러리:
*   **Mermaid.js v10+**: 순서도 시각화 (CDN 사용으로 의존성 최소화)
*   **Socket.IO**: 실시간 AI 채팅
*   **Vanilla JS**: 외부 프레임워크 의존성 없는 경량 구현

#### 신규 정적 파일:
*   **`plc-mentor/static/js/flowchart_viewer.js`**: Mermaid 초기화, 노드 상호작용
*   **`plc-mentor/static/js/ai_chat.js`**: WebSocket 채팅, 메시지 렌더링
*   **`plc-mentor/static/css/analyzer.css`**: 순서도 전용 스타일링

### **의존성 관리 (Enhanced Requirements)**:

```txt
# 기존 의존성
Flask==2.3.2
Werkzeug==2.3.6

# AI/LLM 통합
openai>=1.0.0                 # OpenAI API 클라이언트
ollama>=0.1.0                 # Ollama 로컬 LLM (선택적)
google-generativeai>=0.3.0    # Gemini API (선택적)

# 실시간 통신
flask-socketio>=5.0.0         # WebSocket 지원
python-socketio>=5.0.0

# 데이터 처리 및 검증
networkx>=3.0                 # 그래프 분석 (순서도 구조 최적화)
pydantic>=2.0.0              # 데이터 모델 검증
python-dotenv>=1.0.0          # 환경 변수 관리

# 성능 최적화
redis>=4.0.0                  # 캐싱 (선택적)
gunicorn>=20.0.0             # 프로덕션 WSGI 서버

# 개발 및 테스트
pytest>=7.0.0               # 단위 테스트
pytest-flask>=1.2.0         # Flask 테스트 지원
```

## 단계별 실행 계획 (Phase-by-Phase Execution Plan)

### **Phase 1: 기반 인프라 구축 (1-2주)**
**목표**: 기존 시스템을 순서도 생성 가능한 수준으로 확장

**1.1 GXW 파서 확장**:
*   `EnhancedGXWParser` 클래스 구현
*   제어 흐름 명령어 매핑 추가 (CJ, CALL, END, FEND)
*   기본 분기 감지 로직 구현
*   **성공 지표**: 기존 GXW 파일에서 제어 흐름 요소 추출 성공

**1.2 기본 순서도 생성엔진**:
*   `BasicFlowGenerator` 클래스 구현
*   선형 Mermaid 순서도 텍스트 생성
*   **성공 지표**: 간단한 PLC 로직 → Mermaid 순서도 변환 성공

**1.3 개발 환경 설정**:
*   의존성 설치 및 가상환경 구성
*   환경 변수 설정 (.env 파일)
*   **위험도**: 🟢 낮음 (기존 구조 활용)

### **Phase 2: 웹 인터페이스 구현 (1-2주)**
**목표**: 순서도 시각화 웹 인터페이스 완성

**2.1 Flask 라우트 확장**:
*   `/analyzer` 뷰 및 `/api/generate_flowchart` API 구현
*   파일 업로드 및 검증 로직
*   **성공 지표**: 웹에서 GXW 파일 업로드 → 순서도 표시 성공

**2.2 프론트엔드 템플릿 개발**:
*   `analyzer_view.html` 템플릿 구현
*   Mermaid.js 통합 및 동적 렌더링
*   반응형 UI 구성
*   **성공 지표**: 다양한 브라우저에서 순서도 정상 표시

**2.3 사용자 경험 최적화**:
*   로딩 인디케이터, 에러 처리, 파일 드래그앤드롭
*   **위험도**: 🟡 중간 (브라우저 호환성 이슈 가능)

### **Phase 3: 기본 AI 대화 시스템 (2-3주)**
**목표**: 순서도 기반 AI Q&A 시스템 구현

**3.1 AI 서비스 아키텍처**:
*   `BasicAIChatService` 및 LLM 제공자 추상화 구현
*   Mock → Ollama → OpenAI 단계별 전환
*   **성공 지표**: 개발 환경에서 모의 AI 응답 성공

**3.2 WebSocket 실시간 채팅**:
*   Flask-SocketIO 통합
*   채팅 UI 및 메시지 처리 로직
*   **성공 지표**: 실시간 질문-답변 통신 성공

**3.3 PLC 컨텍스트 통합**:
*   순서도 데이터를 AI 프롬프트에 포함
*   기본 PLC 전문 지식 프롬프트 템플릿
*   **성공 지표**: 순서도 기반 의미있는 AI 답변 생성
*   **위험도**: 🟡 중간 (AI API 연동 복잡성)

### **Phase 4: 고급 분석 및 AI 기능 (3-4주)**
**목표**: 복잡한 PLC 로직 분석 및 전문적 AI 응답

**4.1 고급 순서도 분석**:
*   `AdvancedFlowAnalyzer` 구현
*   조건부 분기, 반복문, 서브루틴 감지
*   복잡한 Mermaid 순서도 생성 (서브그래프, 조건부 경로)
*   **성공 지표**: 복잡한 실제 PLC 프로그램의 정확한 순서도 생성

**4.2 컨텍스트 인식 AI**:
*   `ContextAwareAI` 클래스 구현
*   대화 히스토리 관리
*   순서도 노드별 상세 컨텍스트 생성
*   **성공 지표**: 전문적이고 정확한 PLC 기술 답변 제공

**4.3 안전성 검증 시스템**:
*   `PLCSafetyValidator` 구현
*   위험한 PLC 조작 명령 차단
*   산업 안전 표준 준수 가이드
*   **성공 지표**: 안전하지 않은 AI 조언 자동 차단
*   **위험도**: 🔴 높음 (복잡한 로직 분석, AI 신뢰성)

### **Phase 5: 성능 최적화 및 통합 (2-3주)**
**목표**: 프로덕션 준비 및 전체 시스템 최적화

**5.1 성능 최적화**:
*   대용량 PLC 파일 처리 최적화
*   Redis 캐싱 시스템 (파싱 결과, AI 응답)
*   비동기 처리 개선
*   **성공 지표**: 10MB+ GXW 파일 30초 이내 처리

**5.2 통합 테스트 및 검증**:
*   End-to-End 테스트 슈트
*   다양한 PLC 제조사 파일 호환성 테스트
*   부하 테스트 (동시 사용자 처리)
*   **성공 지표**: 전체 워크플로우 안정성 확인

**5.3 배포 준비**:
*   Gunicorn + Nginx 프로덕션 설정
*   Docker 컨테이너화 (선택적)
*   모니터링 및 로깅 시스템
*   **위험도**: 🟡 중간 (배포 환경 복잡성)

## 위험 관리 및 대안 계획 (Risk Management & Contingency Plans)

### **기술적 위험**:

**1. PLC 파일 포맷 호환성 문제**
*   **위험도**: 🔴 높음
*   **완화책**: 다단계 파싱 전략 (ZIP → XML → 바이너리 → 예시 데이터)
*   **대안**: 사용자가 직접 래더 로직 정보 입력할 수 있는 수동 모드 제공

**2. AI API 안정성 및 비용**
*   **위험도**: 🟡 중간
*   **완화책**: 다중 LLM 제공자 지원, 로컬 Ollama 우선 사용
*   **대안**: 사전 정의된 FAQ 시스템으로 폴백

**3. 복잡한 PLC 로직 분석 정확도**
*   **위험도**: 🔴 높음
*   **완화책**: 단계별 검증 시스템, 사용자 피드백 수집
*   **대안**: 단순화된 순서도 + 상세 설명 방식

### **비즈니스 위험**:

**1. 개발 일정 지연**
*   **완화책**: 각 Phase별 MVP(Minimum Viable Product) 접근
*   **대안**: Phase 4 고급 기능을 v2.0으로 연기

**2. 사용자 채택률 저조**
*   **완화책**: Phase 2 완료 후 조기 사용자 테스트
*   **대안**: 기존 plc-mentor 기능과의 점진적 통합

### **백워드 호환성 보장**:
```python
# 기존 기능 보존
@app.route('/legacy')           # 기존 plc-mentor 기능
@app.route('/convert')          # 기존 변환 기능
@app.route('/learn')            # 기존 학습 기능
@app.route('/analyzer')         # 신규 순서도 분석 기능
```

## 성공 지표 및 검증 방법 (Success Metrics & Validation)

### **기술적 성공 지표**:
*   **순서도 생성 정확도**: 85% 이상 (전문가 검토 기준)
*   **파일 처리 성능**: 5MB GXW 파일 15초 이내 처리
*   **AI 응답 품질**: 사용자 만족도 4.0/5.0 이상
*   **시스템 안정성**: 99% 업타임, 오류율 1% 미만

### **사용자 경험 지표**:
*   **직관성**: 신규 사용자 5분 이내 기본 기능 사용 가능
*   **접근성**: WCAG 2.1 AA 수준 준수
*   **다중 브라우저 지원**: Chrome, Firefox, Safari, Edge 호환

### **비즈니스 지표**:
*   **사용자 채택률**: 기존 plc-mentor 사용자의 60% 이상 신규 기능 사용
*   **세션 지속 시간**: 평균 10분 이상 (현재 대비 2배 증가)
*   **리턴 유저 비율**: 70% 이상

## 예상 파일 변경/추가 (Anticipated File Changes/Additions)

### **신규 파일**:
```
C:/code/PLCview/NOWPLAN_ENHANCED.md (본 문서)
C:/code/PLCview/plc-mentor/app/analyzer/
├── __init__.py
├── flow_analyzer.py              # 순서도 분석 엔진
└── advanced_flow_analyzer.py     # 고급 분석 기능

C:/code/PLCview/plc-mentor/app/services/
├── __init__.py
├── ai_chat_service.py            # AI 채팅 서비스
├── llm_providers.py              # LLM 제공자 추상화
└── performance_optimizer.py     # 성능 최적화

C:/code/PLCview/plc-mentor/app/models/
├── __init__.py
├── flow_models.py               # 순서도 데이터 모델
└── chat_models.py               # 채팅 데이터 모델

C:/code/PLCview/plc-mentor/templates/
└── analyzer_view.html           # 순서도 분석 메인 페이지

C:/code/PLCview/plc-mentor/static/
├── js/
│   ├── flowchart_viewer.js      # Mermaid.js 순서도 뷰어
│   ├── ai_chat.js              # 실시간 채팅 인터페이스
│   └── file_upload.js          # 파일 업로드 핸들러
└── css/
    ├── analyzer.css            # 순서도 전용 스타일
    └── chat.css               # 채팅 인터페이스 스타일

C:/code/PLCview/plc-mentor/tests/
├── integration/
│   └── test_full_workflow.py   # End-to-End 테스트
├── unit/
│   ├── test_flow_analyzer.py   # 순서도 분석 테스트
│   └── test_ai_service.py      # AI 서비스 테스트
└── fixtures/
    └── sample_plc_files/       # 테스트용 PLC 파일들
```

### **수정 파일**:
```
C:/code/PLCview/plc-mentor/app.py                    # 새로운 라우트 및 WebSocket 추가
C:/code/PLCview/plc-mentor/app/parser/gxw_parser.py  # 제어 흐름 분석 기능 확장
C:/code/PLCview/plc-mentor/app/educator/plc_educator.py # AI 컨텍스트 통합
C:/code/PLCview/plc-mentor/templates/base.html       # 네비게이션 메뉴 확장
C:/code/PLCview/plc-mentor/requirements.txt         # 새로운 의존성 추가
C:/code/PLCview/plc-mentor/.env.example             # 환경 변수 예시 업데이트
```

### **설정 파일**:
```
C:/code/PLCview/plc-mentor/.env                     # 환경 변수 (API 키, 설정)
C:/code/PLCview/plc-mentor/config.py                # 애플리케이션 설정
C:/code/PLCview/plc-mentor/docker-compose.yml       # 개발 환경 (선택적)
C:/code/PLCview/plc-mentor/nginx.conf               # 프로덕션 설정 (선택적)
```

---

## 결론 및 다음 단계 (Conclusion & Next Steps)

이 개선된 계획은 **현실적이고 단계적인 접근**을 통해 위험을 최소화하면서 목표를 달성할 수 있도록 구성되었습니다.

### **즉시 시작 가능한 작업**:
1. **Phase 1 준비**: 개발 환경 설정 및 의존성 설치
2. **기존 코드 분석**: 현재 `GXWParser` 클래스 상세 검토
3. **Mermaid.js 학습**: 순서도 문법 및 고급 기능 숙지
4. **AI 제공자 계정**: OpenAI API 키 발급 및 Ollama 설치

### **우선순위 권장사항**:
- **Phase 1-2 집중**: 기본 순서도 생성 기능 완성이 핵심
- **단계별 검증**: 각 Phase 완료 후 사용자 피드백 수집
- **위험 모니터링**: 복잡한 PLC 파일 분석 정확도 지속 확인

### **장기적 확장 계획**:
- **v2.0**: 다중 PLC 제조사 지원 (Allen-Bradley, Schneider Electric)
- **v3.0**: 3D 시각화, VR/AR 인터페이스
- **Enterprise**: 팀 협업, 버전 관리, 클라우드 배포

**검토 후 Phase 1부터 단계적으로 진행하시길 권장합니다.**