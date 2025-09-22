# MELSOFT GX Works2 ↔ PLCview 연결 가이드

## 🔧 MELSOFT GX Works2 설정

### 1. Connection Destination 설정
```
Online → Connection Test... 또는 Connection Destination 설정

Connection Type: Ethernet
Host Station IP: 192.168.3.39 (현재 PLC IP)
Port Number: 1025
Network Number: 0
PC Number: 255
Station Number: 0
Protocol: MC Protocol (3E Frame)
```

### 2. PLC Module 설정
```
CPU Type: Q03UDE (또는 해당 CPU 모델)
Communication Setting:
- Protocol: MC Protocol
- Port: 1025
- Timeout: 5000ms
```

### 3. Network 설정 확인
```
PLC IP: 192.168.3.39
Subnet Mask: 255.255.255.0
Gateway: 192.168.3.1 (일반적)
```

## 🌐 PLCview 웹 인터페이스 연결

### 1. 웹 브라우저에서 접속
```
메인 대시보드: http://localhost:8000
래더 미러링: http://localhost:8000/ladder.html
```

### 2. PLC 연결 절차
1. **PLC 연결** 버튼 클릭
2. **실시간 모니터링 시작** 버튼 클릭
3. 연결 상태 확인

### 3. 실시간 데이터 확인
- 온라인 메뉴의 **Monitor** → **Watch** 와 동일한 기능
- 디바이스 값 실시간 업데이트
- 래더 로직 상태 시각화

## 🔍 연결 테스트 방법

### MELSOFT에서 테스트
1. **Online** → **Connection Test**
2. **Test** 버튼 클릭
3. 연결 성공 확인

### PLCview에서 테스트
1. 브라우저에서 http://localhost:8000/health 접속
2. PLC 상태 확인
3. 래더 페이지에서 실시간 데이터 확인

## ⚠️ 문제 해결

### 연결 실패 시
1. **방화벽 설정 확인**
   - Windows 방화벽에서 1025 포트 허용
   - PLC 통신 프로그램 예외 추가

2. **네트워크 설정 확인**
   - PC와 PLC가 같은 네트워크에 있는지 확인
   - ping 192.168.3.39 명령으로 통신 테스트

3. **PLC 설정 확인**
   - PLC CPU 모듈의 Ethernet 설정 확인
   - MC Protocol 활성화 상태 확인

### 일반적인 오류
- **Connection Timeout**: 네트워크 연결 확인
- **Protocol Error**: MC Protocol 설정 확인
- **Access Denied**: PLC 보안 설정 확인

## 📊 실시간 모니터링 설정

### Monitor/Watch 기능 연동
MELSOFT의 **Monitor** → **Watch** 기능을 웹에서 구현:

```
실시간 감시 디바이스:
- D0, D2, D4, D6 (데이터 레지스터)
- X0, X204 (입력)
- Y45 (출력)
- M0, M30 (내부 릴레이)
- SM400, SM410 (시스템)
```

### 데이터 읽기/쓰기
- **Read from PLC**: PLCview에서 자동 실행
- **Write to PLC**: 웹 인터페이스에서 제어 가능
- **Verify with PLC**: 실시간 검증