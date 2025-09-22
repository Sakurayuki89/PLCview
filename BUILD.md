# BUILD.md - PLC 순서도 시각화 시스템 빌드 가이드

> **Order.txt 기반 개발**: Claude Code와 Gemini CLI 협업으로 효율적인 단계별 구현을 제공합니다.

## 🎯 빌드 철학

1. **5단계 Phase 접근**: NOWPLAN_ENHANCED.md 기준 체계적 진행
2. **Order.txt 협업**: Gemini CLI 명령 기반 코드 생성
3. **최소 단위 구현**: 클래스별 완전 구현 후 통합
4. **백워드 호환성**: 기존 plc-mentor 기능 보존

## 📋 빌드 진행률 추적

```
□ Phase 1: 기반 구조 구축     (1-2주) ← 현재 위치
  ├─ □ Enhanced GXW Parser 구현
  ├─ □ Basic Flow Generator 생성
  └─ □ Flask 라우트 확장

□ Phase 2: 웹 인터페이스     (1-2주)
  ├─ □ analyzer_view.html 템플릿
  ├─ □ Mermaid.js 통합
  └─ □ 파일 업로드 UI

□ Phase 3: 기본 AI 대화      (2-3주)
  ├─ □ AI Chat Service
  ├─ □ WebSocket 채팅
  └─ □ PLC 컨텍스트 생성

□ Phase 4: 고급 분석 기능    (3-4주)
  ├─ □ Advanced Flow Analyzer
  ├─ □ Context Aware AI
  └─ □ Safety Validator

□ Phase 5: 통합 및 최적화    (2-3주)
  ├─ □ 성능 최적화
  ├─ □ End-to-End 테스트
  └─ □ 배포 준비
```

---

## 🚀 Phase 1: 기반 구조 구축 (1-2주)

**목표**: 기존 plc-mentor를 순서도 생성 가능한 수준으로 확장

### 1.1 Order.txt 기반 작업 흐름

```bash
# 1. Order.txt에서 첫 번째 명령 복사
# 2. Gemini CLI에 붙여넣기 실행
# 3. 결과를 Claude에게 공유
# 4. Claude가 코드 검토 및 통합
# 5. 다음 명령으로 진행
```

### 1.2 필수 디렉토리 구조

```bash
plc-mentor/
├── app/
│   ├── analyzer/              # 신규: 순서도 분석 엔진
│   │   ├── __init__.py
│   │   ├── enhanced_gxw_parser.py
│   │   └── basic_flow_generator.py
│   ├── services/             # 신규: 서비스 레이어
│   │   ├── __init__.py
│   │   ├── ai_chat_service.py
│   │   └── llm_providers.py
│   ├── models/               # 신규: 데이터 모델
│   │   ├── __init__.py
│   │   └── flow_models.py
│   └── parser/               # 기존: 확장 예정
│       └── gxw_parser.py
├── static/
│   ├── js/                   # 신규: JavaScript
│   │   ├── flowchart_viewer.js
│   │   └── ai_chat.js
│   └── css/                  # 신규: 스타일
│       └── analyzer.css
├── templates/
│   └── analyzer_view.html    # 신규: 메인 분석 페이지
└── requirements.txt          # 확장: 새 의존성 추가
```

### 1.3 Order.txt 명령 실행 순서

**현재 대기 중인 명령들**:
1. **Enhanced GXW Parser 구현** (Order.txt 명령 1)
2. **Basic Flow Generator 구현** (Order.txt 명령 2)
3. **Flask 라우트 확장** (Order.txt 명령 3)

### ✅ Phase 1 완료 기준

```bash
# 테스트 실행
cd plc-mentor
python -c "from app.analyzer.enhanced_gxw_parser import EnhancedGXWParser; print('✅ Enhanced Parser 로드 성공')"
python -c "from app.analyzer.basic_flow_generator import BasicFlowGenerator; print('✅ Flow Generator 로드 성공')"

# 기본 순서도 생성 테스트
# 간단한 GXW 파일 → Mermaid 텍스트 출력 확인
```

---

## 🌐 Phase 2: 웹 인터페이스 구현 (1-2주)

**목표**: 순서도 시각화 웹 인터페이스 완성

### 2.1 Flask 애플리케이션 확장

```python
# app.py에 추가할 라우트들
@app.route('/analyzer')
def analyzer_view():
    return render_template('analyzer_view.html')

@app.route('/api/generate_flowchart', methods=['POST'])
def generate_flowchart():
    # Enhanced GXW Parser + Basic Flow Generator 활용
    pass
```

### 2.2 프론트엔드 통합

**Mermaid.js CDN 사용**:
```html
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
```

**핵심 JavaScript 컴포넌트**:
- `flowchart_viewer.js`: Mermaid 렌더링 및 상호작용
- `file_upload.js`: GXW 파일 업로드 처리

### ✅ Phase 2 완료 기준

```
✅ 웹에서 GXW 파일 업로드 성공
✅ 기본 순서도 Mermaid 렌더링 성공
✅ 파일 업로드 → 순서도 표시 전체 플로우 동작
```

---

## 🤖 Phase 3: 기본 AI 대화 시스템 (2-3주)

**목표**: 순서도 기반 AI Q&A 시스템 구현

### 3.1 AI 서비스 아키텍처

```python
# app/services/ai_chat_service.py
class BasicAIChatService:
    def __init__(self):
        self.llm_provider = self._init_llm_provider()

    def answer_question(self, question: str, plc_context: dict):
        # 순서도 컨텍스트를 포함한 AI 답변 생성
        pass
```

### 3.2 WebSocket 실시간 채팅

```python
# Flask-SocketIO 통합
from flask_socketio import SocketIO, emit

@socketio.on('ask_question')
def handle_question(data):
    # AI 서비스 호출 및 실시간 응답
    pass
```

### ✅ Phase 3 완료 기준

```
✅ 순서도 업로드 후 AI와 실시간 대화 가능
✅ PLC 컨텍스트 기반 전문적 답변 제공
✅ WebSocket 연결 안정성 확보
```

---

## 🔬 Phase 4: 고급 분석 기능 (3-4주)

**목표**: 복잡한 PLC 로직 분석 및 전문적 AI 응답

### 4.1 고급 제어 흐름 분석

```python
# app/analyzer/advanced_flow_analyzer.py
class AdvancedFlowAnalyzer:
    def analyze_complex_flow(self, ladder_rungs):
        # 조건부 분기, 반복문, 서브루틴 분석
        pass
```

### 4.2 AI 안전성 검증

```python
# app/services/safety_validator.py
class PLCSafetyValidator:
    def validate_instruction_advice(self, response: str) -> bool:
        # 위험한 PLC 조작 명령 차단
        pass
```

### ✅ Phase 4 완료 기준

```
✅ 복잡한 실제 PLC 프로그램의 정확한 순서도 생성
✅ 조건부 분기 및 반복문 올바른 시각화
✅ AI 응답 안전성 검증 시스템 동작
```

---

## ⚡ Phase 5: 통합 및 최적화 (2-3주)

**목표**: 프로덕션 준비 및 성능 최적화

### 5.1 성능 최적화

```python
# app/utils/performance.py
class PerformanceOptimizer:
    def optimize_large_files(self, file_data):
        # 대용량 PLC 파일 최적화 처리
        pass
```

### 5.2 End-to-End 테스트

```bash
# tests/integration/test_full_workflow.py
pytest tests/integration/ -v --cov=app
```

### ✅ Phase 5 완료 기준

```
✅ 5MB+ GXW 파일을 15초 이내 처리
✅ 전체 워크플로우 안정성 확보
✅ 순서도 생성 정확도 85% 이상
✅ 사용자 만족도 4.0/5.0 이상
```

---

## 🔄 Order.txt 사이클 관리

### 명령 실행 로그

```
□ 명령 1: Enhanced GXW Parser (실행일: )
□ 명령 2: Basic Flow Generator (실행일: )
□ 명령 3: Flask 라우트 확장 (실행일: )
□ 명령 4: analyzer_view.html (실행일: )
□ 명령 5: Mermaid.js 통합 (실행일: )

--- Order.txt 초기화 (5개 명령 완료) ---

□ 명령 6: AI Chat Service (실행일: )
...
```

### 검증 체크포인트

- **각 Order.txt 사이클 완료 시**: 코드 통합 및 테스트
- **Phase 완료 시**: BUILD.md 진행률 업데이트
- **10% 진행률 달성 시**: NOWPLAN_ENHANCED.md 기준 검증

---

## 📊 현재 상태

**전체 진행률**: 0% (Phase 1 준비 단계)

**다음 액션**:
1. Order.txt의 첫 번째 명령 실행
2. Enhanced GXW Parser 구현
3. 코드 검토 및 통합

**예상 완료일**: Phase 1 - 2주 후

---

**참고**: 상세한 기술 사양은 NOWPLAN_ENHANCED.md 참조