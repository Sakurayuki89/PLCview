#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLC 교육자 - 주니어 엔지니어를 위한 PLC 학습 도구

PLC 코드를 이해하기 쉬운 형태로 설명하고,
단계별 학습 커리큘럼을 제공합니다.
"""

import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InstructionExplanation:
    """명령어 설명"""
    instruction: str        # 명령어 (LD, AND, OUT 등)
    korean_name: str        # 한글 명칭
    purpose: str            # 목적
    usage: str              # 사용법
    example: str            # 예시
    common_mistakes: List[str]  # 흔한 실수
    safety_notes: List[str]     # 안전 주의사항

@dataclass
class Tutorial:
    """튜토리얼 데이터"""
    title: str
    level: str              # BEGINNER, INTERMEDIATE, ADVANCED
    description: str
    steps: List[Dict[str, str]]
    example_code: str
    quiz: Dict[str, Any]

class PLCEducator:
    """
주니어 엔지니어를 위한 PLC 교육 전문가 클래스
    
기능:
    - PLC 명령어 상세 설명
    - 단계별 학습 커리큘럼
    - 실시간 코드 분석 및 조언
    - 안전 가이드라인
    """
    
    def __init__(self):
        # 미쓰비시 PLC 명령어 설명 데이터당
        self.instruction_database = {
            'LD': InstructionExplanation(
                instruction='LD',
                korean_name='로드 (접점 읽기)',
                purpose='래더 로직의 시작점. 지정된 디바이스의 상태를 읽어서 전류를 시작합니다.',
                usage='LD X001 - X001 입력이 ON이면 전류가 흐릅니다.',
                example='시동 버튼, 센서 입력 발생 시 사용',
                common_mistakes=[
                    '래더 중간에 LD 명령어 사용',
                    '다중 LD 명령어를 연속으로 사용'
                ],
                safety_notes=[
                    '비상정지 신호는 항상 최우선으로 배치',
                    '입력 신호의 안정성 확인 필수'
                ]
            ),
            'LDI': InstructionExplanation(
                instruction='LDI',
                korean_name='로드 인버스 (반전 접점 읽기)',
                purpose='지정된 디바이스가 OFF일 때 전류가 흐릅니다.',
                usage='LDI X001 - X001 입력이 OFF이면 전류가 흐릅니다.',
                example='비상정지 버튼 (뢌면 정지, 떨어지면 동작)',
                common_mistakes=['논리 혼동으로 인한 오동작'],
                safety_notes=['비상정지는 반드시 NC 접점 사용']
            ),
            'AND': InstructionExplanation(
                instruction='AND',
                korean_name='그리고 (직렬 연결)',
                purpose='이전 조건과 현재 조건이 모두 참일 때 전류가 흐릅니다.',
                usage='LD X001 \u2192 AND X002 : X001과 X002가 모두 ON일 때 만 전류 통과',
                example='시동버튼 AND 비상정지해제 → 안전한 시동',
                common_mistakes=['논리 조건의 순서 오류'],
                safety_notes=['모든 안전 조건을 AND로 연결']
            ),
            'ANI': InstructionExplanation(
                instruction='ANI',
                korean_name='그리고 인버스',
                purpose='이전 조건이 참이고 현재 조건이 거짓일 때 전류가 흐릅니다.',
                usage='LD X001 \u2192 ANI X002 : X001이 ON이고 X002가 OFF일 때',
                example='정상동작 AND 비정상없음 → 계속 동작',
                common_mistakes=['논리 혼동'],
                safety_notes=['부정 논리는 신중하게 사용']
            ),
            'OR': InstructionExplanation(
                instruction='OR',
                korean_name='또는 (병렬 연결)',
                purpose='여러 조건 중 하나라도 참이면 전류가 흐릅니다.',
                usage='여러 방법으로 동일한 동작을 실행',
                example='수동버튼 OR 자동모드 → 어느 조건이든 동작',
                common_mistakes=['너무 많은 OR 조건으로 복잡도 증가'],
                safety_notes=['예상치 못한 동작 방지를 위해 조건 제한']
            ),
            'OUT': InstructionExplanation(
                instruction='OUT',
                korean_name='출력',
                purpose='조건이 참일 때 지정된 디바이스를 ON시킵니다.',
                usage='래더 로직의 최종 결과를 출력합니다.',
                example='조건 만족 시 모터 가동, LED 점등',
                common_mistakes=['여러 곳에서 동일 출력 사용'],
                safety_notes=['출력 전 모든 안전 조건 최종 확인']
            ),
            'SET': InstructionExplanation(
                instruction='SET',
                korean_name='셋 (래치)',
                purpose='조건이 참이 되는 순간 디바이스를 ON시키고 계속 유지합니다.',
                usage='한 번 동작하면 계속 유지되는 기능',
                example='알람 랜프, 고장 표시',
                common_mistakes=['RST 명령어와 쌍 사용 안 함'],
                safety_notes=['비상시 SET 된 상태 해제 방법 필수']
            ),
            'RST': InstructionExplanation(
                instruction='RST',
                korean_name='리셋 (해제)',
                purpose='조건이 참일 때 디바이스를 강제로 OFF시킵니다.',
                usage='SET된 상태를 해제하거나 강제 정지',
                example='비상정지, 알람 해제',
                common_mistakes=['중요한 출력을 예상치 못하게 RST'],
                safety_notes=['비상정지는 항상 RST 가능하게 설계']
            )
        }
        
        # 디바이스 타입별 설명
        self.device_explanations = {
            'INPUT': {
                'description': '외부에서 들어오는 신호',
                'examples': ['버튼', '센서', '리미트 스위치'],
                'safety': '입력 신호의 안정성 확인 필수',
                'color_code': '녹색(시동), 빨간색(비상정지)'
            },
            'OUTPUT': {
                'description': '외부 기기를 제어하는 신호',
                'examples': ['모터', 'LED', '졬레노이드 밸브'],
                'safety': '출력 전 안전 조건 반드시 확인',
                'color_code': '파란색 또는 회색'
            },
            'MEMORY': {
                'description': 'PLC 내부에서 사용하는 가상 스위치',
                'examples': ['운전 상태', '모드 선택', '인터록'],
                'safety': '중요한 메모리는 전원 껴짐 시 초기화',
                'color_code': '한글 또는 영문 라벨'
            },
            'TIMER': {
                'description': '시간 지연을 위한 장치',
                'examples': ['모터 시동 지연', '경보 지연'],
                'safety': '비상시 타이머 무시 가능하게 설계',
                'color_code': '시간 단위 명기 (초, 분)'
            }
        }
        
        # 학습 커리큘럼
        self.tutorials = self._create_tutorials()
    
    def explain_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
프로젝트 전체를 교육적으로 설명
        
        Args:
            project_data: GXW 파서에서 추출한 프로젝트 데이터
            
        Returns:
            교육적 설명 데이터
        """
        try:
            logger.info("프로젝트 교육적 설명 생성 시작")
            
            explanations = {
                'project_overview': self._explain_project_overview(project_data),
                'device_analysis': self._analyze_devices(project_data.get('devices', [])),
                'ladder_explanation': self._explain_ladder_logic(project_data.get('ladder_rungs', [])),
                'safety_analysis': self._analyze_safety(project_data),
                'learning_suggestions': self._generate_learning_suggestions(project_data),
                'common_patterns': self._identify_common_patterns(project_data),
                'improvement_tips': self._suggest_improvements(project_data)
            }
            
            return explanations
            
        except Exception as e:
            logger.error(f"교육적 설명 생성 오류: {e}")
            return {'error': f'설명 생성 중 오류: {e}'}
    
    def _explain_project_overview(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """프로젝트 개요 설명"""
        project_info = project_data.get('project_info', {})
        analysis = project_data.get('analysis', {})
        
        overview = {
            'title': f"\ud83c\udfed {project_info.get('name', 'PLC 프로젝트')} 개요",
            'complexity': self._assess_complexity(analysis),
            'purpose': self._guess_project_purpose(project_data),
            'main_components': self._identify_main_components(project_data),
            'beginner_explanation': self._create_beginner_explanation(project_data)
        }
        
        return overview
    
    def _analyze_devices(self, devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """디바이스 분석 및 설명"""
        device_analysis = {
            'total_count': len(devices),
            'by_type': {},
            'detailed_explanations': [],
            'safety_critical': [],
            'naming_suggestions': []
        }
        
        # 타입별 분류
        for device in devices:
            device_type = device.get('type', 'UNKNOWN')
            if device_type not in device_analysis['by_type']:
                device_analysis['by_type'][device_type] = []
            device_analysis['by_type'][device_type].append(device)
        
        # 상세 설명 생성
        for device in devices:
            explanation = self._explain_single_device(device)
            device_analysis['detailed_explanations'].append(explanation)
            
            # 안전 중요 디바이스 식별
            if device.get('safety_level') == 'CRITICAL':
                device_analysis['safety_critical'].append(device['name'])
        
        return device_analysis
    
    def _explain_ladder_logic(self, ladder_rungs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """래더 로직 상세 설명"""
        ladder_explanation = {
            'total_rungs': len(ladder_rungs),
            'step_by_step': [],
            'flow_diagram': self._create_flow_diagram(ladder_rungs),
            'instruction_summary': self._summarize_instructions(ladder_rungs),
            'potential_issues': self._identify_potential_issues(ladder_rungs)
        }
        
        # 단계별 설명
        for i, rung in enumerate(ladder_rungs):
            step_explanation = self._explain_single_rung(rung, i + 1)
            ladder_explanation['step_by_step'].append(step_explanation)
        
        return ladder_explanation
    
    def _explain_single_device(self, device: Dict[str, Any]) -> Dict[str, Any]:
        """개별 디바이스 상세 설명"""
        device_name = device.get('name', '')
        device_type = device.get('type', '')
        description = device.get('description', '')
        
        type_info = self.device_explanations.get(device_type, {})
        
        explanation = {
            'device': device_name,
            'type': device_type,
            'korean_description': description,
            'what_it_does': type_info.get('description', ''),
            'typical_examples': type_info.get('examples', []),
            'safety_note': type_info.get('safety', ''),
            'color_coding': type_info.get('color_code', ''),
            'usage_frequency': device.get('used_count', 0),
            'beginner_tip': self._generate_beginner_tip(device)
        }
        
        return explanation
    
    def _explain_single_rung(self, rung: Dict[str, Any], step_number: int) -> Dict[str, Any]:
        """개별 런그 상세 설명"""
        instruction = rung.get('instruction', '')
        device = rung.get('device', '')
        comment = rung.get('comment', '')
        
        instruction_info = self.instruction_database.get(instruction, None)
        
        explanation = {
            'step': step_number,
            'instruction': instruction,
            'device': device,
            'comment': comment,
            'korean_name': instruction_info.korean_name if instruction_info else instruction,
            'what_happens': instruction_info.purpose if instruction_info else '설명 없음',
            'detailed_explanation': f"발그 들어가우자. 여기서 {instruction} 명령어는 {device}를 대상으로 합니다. "
                                   f"{comment}으로 버력 오는데요, 이것은 {instruction_info.purpose if instruction_info else '알 수 없는 동작'}을 의미합니다.",
            'safety_notes': instruction_info.safety_notes if instruction_info else [],
            'common_mistakes': instruction_info.common_mistakes if instruction_info else []
        }
        
        return explanation
    
    def _generate_beginner_tip(self, device: Dict[str, Any]) -> str:
        """초보자를 위한 팁"""
        device_type = device.get('type', '')
        device_name = device.get('name', '')
        
        tips = {
            'INPUT': f"{device_name}은 외부에서 들어오는 신호입니다. 실제 버튼을 누르거나 센서가 동작할 때 ON됩니다.",
            'OUTPUT': f"{device_name}은 PLC가 외부 기기를 제어할 때 사용합니다. 예를 들어 모터를 돌리거나 LED를 켜는 식으로요.",
            'MEMORY': f"{device_name}은 PLC 내부의 가상 스위치입니다. 마치 컴퓨터의 변수처럼 생각하시면 됩니다.",
            'TIMER': f"{device_name}은 시간을 재는 타이머입니다. 설정된 시간이 지나면 동작합니다."
        }
        
        return tips.get(device_type, f"{device_name}에 대한 기본 정보를 확인하세요.")
    
    def _assess_complexity(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """복잡도 평가"""
        complexity_level = analysis.get('complexity_level', 'BEGINNER')
        
        complexity_map = {
            'BEGINNER': {
                'level': '초보자',
                'description': 'PLC를 처음 배우는 사람도 이해할 수 있습니다.',
                'learning_time': '1-2시간',
                'emoji': '👶'
            },
            'INTERMEDIATE': {
                'level': '중급자',
                'description': '기본 PLC 지식이 있으면 이해할 수 있습니다.',
                'learning_time': '3-5시간',
                'emoji': '🎓'
            },
            'ADVANCED': {
                'level': '고급자',
                'description': '숙련된 PLC 엔지니어에게 적합합니다.',
                'learning_time': '5-10시간',
                'emoji': '🚀'
            }
        }
        
        return complexity_map.get(complexity_level, complexity_map['BEGINNER'])
    
    def _create_tutorials(self) -> List[Tutorial]:
        """학습 커리큘럼 생성"""
        tutorials = [
            Tutorial(
                title="PLC 기초: 래더 로직이란?",
                level="BEGINNER",
                description="래더 로직의 기본 개념과 동작 원리를 배운니다.",
                steps=[
                    {"step": 1, "title": "래더 다이어그램이란?", "content": "전기 회로를 그림으로 나타낸 것"},
                    {"step": 2, "title": "LD 명령어 이해", "content": "접점을 읽는 기본 명령어"},
                    {"step": 3, "title": "AND 조건 이해", "content": "여러 조건을 동시에 만족"},
                    {"step": 4, "title": "OUT 출력 이해", "content": "조건이 맞으면 결과 출력"}
                ],
                example_code="LD X001\nAND X002\nOUT Y001",
                quiz={
                    "question": "X001과 X002가 모두 ON일 때 Y001의 상태는?",
                    "options": ["ON", "OFF", "대기", "알 수 없음"],
                    "answer": 0,
                    "explanation": "AND 조건이므로 모든 입력이 ON일 때 Y001도 ON됩니다."
                }
            ),
            Tutorial(
                title="모터 제어 회로 만들기",
                level="INTERMEDIATE",
                description="실제 모터를 안전하게 제어하는 회로를 만들어보세요.",
                steps=[
                    {"step": 1, "title": "비상정지 회로", "content": "안전을 위한 필수 요소"},
                    {"step": 2, "title": "시동 회로", "content": "정상적인 모터 시동 순서"},
                    {"step": 3, "title": "인터록 회로", "content": "다양한 안전 조건 추가"}
                ],
                example_code="LD X001\nANI X999\nAND M100\nOUT Y001",
                quiz={
                    "question": "비상정지 버튼(X999)이 눌린 상태에서 모터가 동작할 수 있나요?",
                    "options": ["예", "아니오", "조건에 따라", "알 수 없음"],
                    "answer": 1,
                    "explanation": "ANI X999 조건으로 비상정지가 눌리면(즉, X999가 ON이면) 모터는 동작하지 않습니다."
                }
            )
        ]
        
        return tutorials
    
    def get_tutorials(self) -> List[Dict[str, Any]]:
        """학습 커리큘럼 반환"""
        return [{
            'title': t.title,
            'level': t.level,
            'description': t.description,
            'steps_count': len(t.steps),
            'example_code': t.example_code
        } for t in self.tutorials]
    
    def _analyze_safety(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """안전성 분석"""
        safety_analysis = {
            'overall_score': project_data.get('analysis', {}).get('safety_score', 75),
            'critical_devices': [],
            'safety_violations': [],
            'recommendations': []
        }
        
        # 비상정지 확인
        devices = project_data.get('devices', [])
        emergency_stops = [d for d in devices if '비상정지' in d.get('description', '')]
        
        if not emergency_stops:
            safety_analysis['safety_violations'].append('비상정지 버튼이 없습니다')
            safety_analysis['recommendations'].append('비상정지 버튼(X002)을 추가하세요')
        
        return safety_analysis
    
    def _generate_learning_suggestions(self, project_data: Dict[str, Any]) -> List[str]:
        """학습 제안"""
        suggestions = [
            "🎓 래더 로직 기초 커리큘럼으로 시작하세요",
            "🔧 실제 PLC 시뮬레이터로 연습해보세요",
            "📚 IEC 61131-3 표준 문서를 참고하세요",
            "⚠️ 안전 가이드라인을 반드시 숨기세요"
        ]
        
        return suggestions
    
    def _identify_common_patterns(self, project_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """일반적인 패턴 식별"""
        patterns = [
            {
                'pattern': '시동-정지 회로',
                'description': '기본적인 모터 제어 패턴',
                'when_to_use': '단순한 모터 제어에 사용'
            },
            {
                'pattern': '비상정지 인터록',
                'description': '안전을 위한 필수 회로',
                'when_to_use': '모든 위험 기계에 반드시 필요'
            }
        ]
        
        return patterns
    
    def _suggest_improvements(self, project_data: Dict[str, Any]) -> List[str]:
        """개선 제안"""
        improvements = [
            "📝 변수명을 더 명확하게 지어보세요",
            "📝 주석을 더 상세하게 작성하세요",
            "⚙️ 디바이스를 기능별로 그룹화해보세요",
            "🔄 재사용 가능한 함수 블록 고려"
        ]
        
        return improvements
    
    def _guess_project_purpose(self, project_data: Dict[str, Any]) -> str:
        """프로젝트 목적 추정"""
        devices = project_data.get('devices', [])
        
        motor_count = len([d for d in devices if '모터' in d.get('description', '')])
        if motor_count > 0:
            return f"모터 {motor_count}대를 사용한 자동화 시스템"
        
        return "일반적인 PLC 제어 시스템"
    
    def _identify_main_components(self, project_data: Dict[str, Any]) -> List[str]:
        """주요 구성요소 식별"""
        components = []
        devices = project_data.get('devices', [])
        
        input_count = len([d for d in devices if d.get('type') == 'INPUT'])
        output_count = len([d for d in devices if d.get('type') == 'OUTPUT'])
        
        components.append(f"입력 신호 {input_count}개")
        components.append(f"출력 신호 {output_count}개")
        
        return components
    
    def _create_beginner_explanation(self, project_data: Dict[str, Any]) -> str:
        """초보자를 위한 쉽게 설명"""
        return (
            "👶 초보자도 이해할 수 있는 설명\n\n"
            "이 PLC 프로그램은 마치 전자레인지의 아랑이처럼 동작합니다. "
            "버튼을 누르면 (입력) 원하는 동작이 실행되고 (출력), "
            "안전장치가 작동하여 위험한 상황에서는 자동으로 멈춘니다."
        )
    
    def _create_flow_diagram(self, ladder_rungs: List[Dict[str, Any]]) -> str:
        """동작 흐름도 생성"""
        if not ladder_rungs:
            return "동작 흐름이 없습니다."
        
        flow = "🔄 동작 흐름\n"
        for i, rung in enumerate(ladder_rungs):
            instruction = rung.get('instruction', '')
            device = rung.get('device', '')
            
            if instruction == 'LD':
                flow += f"{i+1}. {device} 입력 상태 확인 \u2192 "
            elif instruction in ['AND', 'ANI']:
                flow += f"{device} 조건 추가 \u2192 "
            elif instruction == 'OUT':
                flow += f"{device} 출력 실행\n"
        
        return flow
    
    def _summarize_instructions(self, ladder_rungs: List[Dict[str, Any]]) -> Dict[str, int]:
        """명령어 사용 통계"""
        summary = {}
        for rung in ladder_rungs:
            instruction = rung.get('instruction', '')
            summary[instruction] = summary.get(instruction, 0) + 1
        return summary
    
    def _identify_potential_issues(self, ladder_rungs: List[Dict[str, Any]]) -> List[str]:
        """잠재적 문제 식별"""
        issues = []
        
        # 기본적인 문제 검사
        if len(ladder_rungs) > 20:
            issues.append("프로그램이 너무 꺁니다. 모듈화를 고려해보세요.")
        
        # 비상정지 검사
        emergency_found = any('비상정지' in rung.get('comment', '') for rung in ladder_rungs)
        if not emergency_found:
            issues.append("비상정지 회로가 보이지 않습니다.")
        
        return issues