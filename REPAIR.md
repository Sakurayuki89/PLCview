# REPAIR.md - PLC 순서도 시각화 프로젝트 오류 해결 가이드

## 📝 형식 규칙

- **오류 발생 시 즉시 기록**: Phase별, Order.txt 사이클별 오류 추적
- **구조화된 기록**: 증상 → 원인 → 해결 → 예방법 → 참고자료
- **프로젝트 특화**: PLC 분석, Mermaid.js, Gemini CLI 관련 오류 중심

## 🛠️ 예시 템플릿

```
[날짜] 오류 #번호 - 오류 제목

증상: 구체적인 오류 현상 기술
원인: 근본 원인 분석
해결: 적용한 해결 방법
참고: 관련 코드, 링크, 명령어
예방법: 향후 동일 문제 방지 방안
```

---

## 🚨 일반적인 PLC 순서도 프로젝트 오류들

### [예시] 오류 #1 - Enhanced GXW Parser 임포트 실패

**증상**: `from app.analyzer.enhanced_gxw_parser import EnhancedGXWParser` 시 ModuleNotFoundError

**원인**:
- analyzer 디렉토리 또는 `__init__.py` 파일 누락
- PYTHONPATH 설정 문제

**해결**:
```bash
# 1. 디렉토리 구조 확인
mkdir -p plc-mentor/app/analyzer
touch plc-mentor/app/analyzer/__init__.py

# 2. 파일 존재 확인
ls -la plc-mentor/app/analyzer/enhanced_gxw_parser.py

# 3. 임포트 경로 수정
cd plc-mentor
python -c "from app.analyzer.enhanced_gxw_parser import EnhancedGXWParser"
```

**예방법**: Order.txt 명령 실행 전 항상 디렉토리 구조 확인

### [예시] 오류 #2 - Mermaid.js 렌더링 실패

**증상**: 웹 페이지에서 순서도가 텍스트로만 표시되고 다이어그램으로 렌더링되지 않음

**원인**:
- Mermaid.js CDN 로드 실패
- `mermaid.initialize()` 호출 누락
- 잘못된 Mermaid 문법

**해결**:
```html
<!-- CDN 확인 -->
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>

<!-- 초기화 확인 -->
<script>
  mermaid.initialize({startOnLoad: true});
</script>

<!-- 문법 검증 -->
<div class="mermaid">
flowchart TD
  A[Start] --> B[Process]
  B --> C[End]
</div>
```

**예방법**: Mermaid Live Editor에서 문법 사전 검증

### [예시] 오류 #3 - Gemini CLI 응답 없음

**증상**: Order.txt 명령을 Gemini CLI에 입력했지만 응답이 생성되지 않음

**원인**:
- API 키 만료 또는 할당량 초과
- 프롬프트가 너무 길거나 복잡함
- 네트워크 연결 문제

**해결**:
```bash
# 1. API 키 확인
gemini-cli --version
export GEMINI_API_KEY="your_api_key"

# 2. 간단한 테스트
echo "Hello" | gemini-cli

# 3. 프롬프트 단순화
# 긴 프롬프트를 여러 개의 짧은 명령으로 분할
```

**예방법**: Order.txt 명령을 간결하게 작성, API 키 주기적 갱신

### [예시] 오류 #4 - Flask 라우트 404 에러

**증상**: `/analyzer` 엔드포인트 접근 시 404 Not Found

**원인**:
- 라우트 등록 누락
- Flask 앱 재시작 필요
- URL 경로 오타

**해결**:
```python
# app.py 확인
@app.route('/analyzer')
def analyzer_view():
    return render_template('analyzer_view.html')

# 서버 재시작
flask run --debug

# URL 확인
curl http://localhost:5000/analyzer
```

**예방법**: 새 라우트 추가 후 항상 테스트

### [예시] 오류 #5 - GXW 파일 파싱 실패

**증상**: 업로드된 GXW 파일에서 데이터 추출 실패, 빈 결과 반환

**원인**:
- 지원하지 않는 GXW 버전
- 파일 손상 또는 인코딩 문제
- 파서 로직 버그

**해결**:
```python
# 1. 파일 무결성 확인
with open('test.gxw', 'rb') as f:
    data = f.read()
    print(f"파일 크기: {len(data)} bytes")
    print(f"매직 헤더: {data[:4]}")

# 2. 예외 처리 강화
try:
    parser = EnhancedGXWParser()
    result = parser.parse(filepath)
except Exception as e:
    logger.error(f"파싱 오류: {e}")
    return fallback_example_data()

# 3. 로그 레벨 증가
import logging
logging.basicConfig(level=logging.DEBUG)
```

**예방법**: 다양한 GXW 파일로 테스트, 예외 처리 강화

---

## 🔄 Order.txt 사이클 관련 오류

### [예시] 오류 #6 - Order.txt 명령 초기화 누락

**증상**: 5개 명령 완료 후에도 Order.txt가 초기화되지 않음

**원인**: 수동 초기화 절차 누락

**해결**:
```bash
# Order.txt 백업
cp Order.txt Order.txt.backup.$(date +%Y%m%d)

# 초기화 실행
# (Claude가 새로운 Order.txt 내용으로 업데이트)
```

**예방법**: 5개 명령 완료 시 자동 체크리스트 도입

---

## 📊 통계 및 패턴 분석

**자주 발생하는 오류 유형**:
1. 임포트/모듈 경로 문제 (30%)
2. JavaScript/프론트엔드 통합 문제 (25%)
3. API 연동 문제 (20%)
4. 파일 파싱 문제 (15%)
5. 환경 설정 문제 (10%)

**해결 시간 평균**:
- 경로/임포트 문제: 5-10분
- 프론트엔드 문제: 15-30분
- API 문제: 10-20분
- 파싱 문제: 30-60분

---

## 🛡️ 예방 체크리스트

**Order.txt 명령 실행 전**:
- [ ] 디렉토리 구조 확인
- [ ] 의존성 설치 상태 확인
- [ ] 기존 코드와의 호환성 검토

**코드 통합 전**:
- [ ] 문법 오류 확인
- [ ] 임포트 경로 검증
- [ ] 간단한 기능 테스트

**Phase 완료 전**:
- [ ] 전체 워크플로우 테스트
- [ ] 에러 로그 확인
- [ ] 성능 지표 측정

---

**다음 업데이트**: Phase 1 진행 중 실제 오류 발생 시