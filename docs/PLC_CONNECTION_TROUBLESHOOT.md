# MELSOFT PLC 연결 문제 해결 가이드

## 🚨 오류: "Unable to communicate with the specified CPU or station"

### 즉시 해결 순서

#### 1. Connection Destination 재설정
```
1. Online → Connection Destination... 선택
2. Connection Test... 대신 직접 설정 변경

설정값:
- Connection Type: Ethernet
- Host Station: 192.168.3.39
- Port Number: 1025 → 5007로 변경 시도
- Timeout: 5000ms → 10000ms로 증가
```

#### 2. 네트워크 연결 확인
```
Windows 명령프롬프트에서:
ping 192.168.3.39

응답이 없으면:
- 네트워크 케이블 확인
- PLC 전원 상태 확인
- 라우터/스위치 확인
```

#### 3. PLC 모듈 설정 확인
```
가능한 포트 번호들:
- 1025 (MC Protocol)
- 5007 (MELSOFT Connection)
- 8501 (HTTP)
- 80 (Web Interface)

Protocol 설정:
- MC Protocol (3E Frame) ← 기본
- MC Protocol (4E Frame) ← 시도
- SLMP (Seamless Message Protocol)
```

#### 4. Windows 방화벽 설정
```
1. Windows 보안 → 방화벽 및 네트워크 보호
2. 방화벽을 통해 앱 허용
3. MELSOFT 관련 프로그램들 허용:
   - GX Works2
   - MC Protocol
   - 포트 1025, 5007 허용
```

#### 5. PLC CPU 모듈 상태 확인
```
확인 사항:
- CPU 모듈 RUN 상태 (LED 녹색)
- Ethernet 모듈 LINK 상태 (LED 점등)
- Error LED 상태 확인
- DIP 스위치 설정 확인
```

## 🔄 대안 연결 방법

### Option 1: 시뮬레이터 연결 (즉시 테스트)
1. MELSOFT GX Simulator 실행
2. PLCview에서 localhost 연결
3. 시뮬레이터 환경에서 테스트

### Option 2: OPC Server 연결
1. MELSOFT OPC Server 설정
2. OPC Client로 데이터 교환
3. 간접 연결 방식

### Option 3: 직렬 통신 (RS-232C)
1. Serial 케이블 연결
2. COM 포트 설정
3. 시리얼 통신으로 연결

## 🌐 PLCview 설정 수정

### IP 주소 변경
```
만약 PLC IP가 다르다면:
1. .env 파일에서 PLC_HOST 수정
2. 실제 PLC IP 주소 확인
3. 네트워크 스캔으로 PLC 찾기
```

### 포트 번호 변경
```
.env 파일 수정:
PLC_PORT=5007  # 또는 다른 포트
```

## 📊 연결 성공 확인 방법

### MELSOFT 확인
1. Online 상태 표시 (연결됨)
2. Device Monitor 동작
3. 오류 메시지 없음

### PLCview 확인
1. PLC 상태: Connected
2. 실시간 데이터 수신
3. 래더 다이어그램 활성화

## 🚨 일반적인 오류 코드

### ES:0180840b
- 네트워크 타임아웃
- 잘못된 IP 주소
- 방화벽 차단

### 해결책
1. 타임아웃 시간 증가
2. IP 주소 재확인
3. 방화벽 설정 변경
4. PLC 리부팅
5. PC 네트워크 어댑터 재시작