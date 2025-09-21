"""
MELSOFT GX Works2 디바이스 매핑 설정
래더 다이어그램의 디바이스를 웹 인터페이스에 연동
"""

# 이미지에서 확인된 디바이스들
DEVICE_MAPPING = {
    # 입력 디바이스 (X)
    "inputs": {
        "X0": {"name": "입력 X0", "type": "bool", "description": "외부 입력 신호"},
        "X204": {"name": "센서 입력", "type": "bool", "description": "센서 감지 신호"},
    },

    # 출력 디바이스 (Y)
    "outputs": {
        "Y45": {"name": "출력 Y45", "type": "bool", "description": "액추에이터 제어"},
        "M0": {"name": "내부 릴레이 M0", "type": "bool", "description": "내부 제어 신호"},
    },

    # 데이터 레지스터 (D)
    "data_registers": {
        "D0": {"name": "데이터 D0", "type": "int16", "description": "온도 데이터", "unit": "°C"},
        "D2": {"name": "데이터 D2", "type": "int16", "description": "압력 데이터", "unit": "kPa"},
        "D4": {"name": "데이터 D4", "type": "int16", "description": "속도 데이터", "unit": "RPM"},
        "D6": {"name": "데이터 D6", "type": "int16", "description": "카운터 값"},
        "D100": {"name": "온도 센서", "type": "int16", "description": "메인 온도 센서", "unit": "°C"},
        "D106": {"name": "압력 센서", "type": "int16", "description": "메인 압력 센서", "unit": "kPa"},
        "D110": {"name": "속도 센서", "type": "int16", "description": "모터 속도", "unit": "RPM"},
        "D111": {"name": "상태 값", "type": "int16", "description": "시스템 상태"},
    },

    # 카운터 (C)
    "counters": {
        "K30": {"name": "카운터 설정값", "type": "int16", "description": "목표 카운트", "preset": 30},
        "K500": {"name": "타이머 설정값", "type": "int16", "description": "지연 시간", "preset": 500},
        "K3000": {"name": "대기 시간", "type": "int16", "description": "대기 카운트", "preset": 3000},
        "K4000": {"name": "리셋 시간", "type": "int16", "description": "리셋 지연", "preset": 4000},
    },

    # 특수 디바이스
    "special": {
        "SM400": {"name": "시스템 모니터", "type": "bool", "description": "시스템 상태 모니터"},
        "SM410": {"name": "에러 플래그", "type": "bool", "description": "시스템 에러 상태"},
    }
}

# 래더 로직 매핑 (이미지 기반)
LADDER_LOGIC = {
    "rung_0": {
        "description": "메인 제어 로직",
        "conditions": ["D2", "K3000", "D2", "K3000"],
        "outputs": ["M0V", "K300", "D2"]
    },
    "rung_29": {
        "description": "비교 로직",
        "conditions": ["D0", "K500"],
        "outputs": ["M30"]
    },
    "rung_36": {
        "description": "상태 제어",
        "conditions": ["D0", "K10", "D10"],
        "outputs": ["D10", "K10", "D11"]
    },
    "rung_43": {
        "description": "센서 처리",
        "conditions": ["X204", "SM410", "D6", "K30", "Y45"],
        "outputs": ["D+P", "D4", "D2", "D4"]
    },
    "rung_68": {
        "description": "모터 제어",
        "conditions": ["X0", "M0"],
        "outputs": ["MOV", "K0", "D4"]
    }
}

# 실시간 모니터링 대상 디바이스
REALTIME_DEVICES = [
    "D100",  # 온도
    "D106",  # 압력
    "D110",  # 속도
    "X0",    # 입력 신호
    "Y45",   # 출력 신호
    "M0",    # 내부 릴레이
    "SM400", # 시스템 상태
]

# 알람/경고 설정
ALARM_CONDITIONS = {
    "D100": {"min": 0, "max": 100, "alarm_msg": "온도 이상"},
    "D106": {"min": 0, "max": 1000, "alarm_msg": "압력 이상"},
    "D110": {"min": 0, "max": 3000, "alarm_msg": "속도 이상"},
}