# 🔒 보안 가이드라인

## API 키 관리

### ⚠️ 중요: API 키 보안
- **절대로** API 키를 Git에 커밋하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있습니다
- `.env.example`을 복사하여 실제 키를 입력하세요

### 설정 방법
```bash
# 1. 템플릿 복사
cp plc-ai-assistant/.env.example plc-ai-assistant/.env

# 2. 실제 API 키 입력
# .env 파일을 편집하여 your_gemini_api_key_here를 실제 키로 변경
```

### Gemini API 키 발급
1. [Google AI Studio](https://aistudio.google.com/app/apikey) 방문
2. API 키 생성
3. `.env` 파일의 `GEMINI_API_KEY`에 입력

### 환경별 설정
- **개발환경**: `.env` 파일 사용
- **프로덕션**: 환경변수 또는 보안 키 관리 시스템 사용
- **CI/CD**: GitHub Secrets, Azure Key Vault 등 사용

### 보안 체크리스트
- [ ] `.env` 파일이 `.gitignore`에 포함됨
- [ ] API 키가 코드에 하드코딩되지 않음
- [ ] 프로덕션에서는 보안 키 관리 시스템 사용
- [ ] API 키 정기적 교체 (3개월마다 권장)

## 네트워크 보안

### PLC 연결 보안
- PLC 네트워크를 별도 VLAN으로 분리 권장
- 방화벽 규칙으로 접근 제한
- PLC 통신 로그 모니터링

### 웹 인터페이스 보안
- HTTPS 사용 (프로덕션 환경)
- CORS 설정 검토
- WebSocket 연결 인증 구현 권장

## 배포 보안

### Docker 컨테이너
```bash
# 비root 사용자로 실행
USER plcuser

# 최소 권한 설정
RUN chmod 755 /app
```

### 시스템 서비스
```bash
# systemd 서비스에서 환경변수 분리
Environment="GEMINI_API_KEY=actual_key_here"
```

## 사고 대응

### API 키 노출 시
1. 즉시 Google AI Studio에서 키 비활성화
2. 새 키 생성 및 교체
3. Git 히스토리에서 키 제거 (필요시)
4. 영향 범위 분석

### 연락처
- 보안 문제 발견 시: 프로젝트 관리자에게 즉시 보고
- 긴급 상황: 즉시 API 키 비활성화 후 보고