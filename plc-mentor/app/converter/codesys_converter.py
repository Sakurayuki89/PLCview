#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CODESYS 변환기 - 미쓰비시 GX Works2 래더 로직을 CODESYS로 변환

주니어 엔지니어가 이해하기 쉬운 형태로 변환 과정을 설명합니다.
"""

import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversionResult:
    """변환 결과"""
    structured_text: str       # ST 코드
    ladder_diagram: str        # LD 코드
    variable_declarations: str # 변수 선언
    function_blocks: str       # 함수 블록
    comments: str              # 설명 및 주석
    conversion_notes: List[str] # 변환 주의사항

class CodesysConverter:
    """
미쓰비시 GX Works2 래더 로직을 CODESYS로 변환하는 클래스
    
기능:
    - 래더 로직 → Structured Text (ST)
    - 래더 로직 → Ladder Diagram (LD)
    - 변수 선언 자동 생성
    - 교육적 설명 포함
    """
    
    def __init__(self):
        # 미쓰비시 → CODESYS 명령어 매핑
        self.instruction_mapping = {
            'LD': 'IF',           # Load → IF 조건
            'LDI': 'IF NOT',      # Load Inverse → IF NOT 조건
            'AND': 'AND',         # AND → AND
            'ANI': 'AND NOT',     # AND Inverse → AND NOT
            'OR': 'OR',           # OR → OR
            'ORI': 'OR NOT',      # OR Inverse → OR NOT
            'ANB': '',            # AND Block → 괄호 처리
            'ORB': '',            # OR Block → 괄호 처리
            'OUT': ':=',          # Output → 할당
            'SET': ':= TRUE',     # Set → TRUE 할당
            'RST': ':= FALSE',    # Reset → FALSE 할당
            'PLS': 'R_TRIG',      # Pulse → Rising Edge
            'PLF': 'F_TRIG',      # Pulse Falling → Falling Edge
        }
        
        # 디바이스 타입 매핑
        self.device_mapping = {
            'X': '%IX',           # 입력 → Input
            'Y': '%QX',           # 출력 → Output
            'M': 'M',             # 내부 릴레이 → Memory
            'D': 'D',             # 데이터 → Data Word
            'T': 'TON',           # 타이머 → Timer On
            'C': 'CTU',           # 카운터 → Counter Up
        }
        
        # CODESYS 데이터 타입 매핑
        self.data_types = {
            'INPUT': 'BOOL',
            'OUTPUT': 'BOOL', 
            'MEMORY': 'BOOL',
            'DATA': 'INT',
            'TIMER': 'TON',
            'COUNTER': 'CTU'
        }
    
    def convert(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
프로젝트 데이터를 CODESYS 코드로 변환
        
        Args:
            project_data: GXW 파서에서 추출한 프로젝트 데이터
            
        Returns:
            CODESYS 변환 결과
        """
        try:
            logger.info("CODESYS 변환 시작")
            
            # 변수 선언 생성
            variables = self._generate_variable_declarations(project_data.get('devices', []))
            
            # Structured Text 변환
            st_code = self._convert_to_structured_text(project_data.get('ladder_rungs', []))
            
            # Ladder Diagram 변환
            ld_code = self._convert_to_ladder_diagram(project_data.get('ladder_rungs', []))
            
            # 함수 블록 생성
            function_blocks = self._generate_function_blocks(project_data)
            
            # 교육적 주석 생성
            comments = self._generate_educational_comments(project_data)
            
            # 변환 주의사항
            notes = self._generate_conversion_notes(project_data)
            
            return {
                'success': True,
                'structured_text': st_code,
                'ladder_diagram': ld_code,
                'variable_declarations': variables,
                'function_blocks': function_blocks,
                'educational_comments': comments,
                'conversion_notes': notes,
                'project_template': self._generate_codesys_project_template(project_data)
            }
            
        except Exception as e:
            logger.error(f"CODESYS 변환 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'structured_text': '// 변환 오류 발생',
                'conversion_notes': [f'변환 중 오류 발생: {e}']
            }
    
    def _generate_variable_declarations(self, devices: List[Dict[str, Any]]) -> str:
        """
변수 선언 생성
        """
        var_sections = {
            'VAR_INPUT': [],
            'VAR_OUTPUT': [],
            'VAR': []
        }
        
        for device in devices:
            device_name = device['name']
            device_type = device['type']
            description = device.get('description', '')
            
            # CODESYS 변수명 변환
            codesys_name = self._convert_device_name(device_name)
            codesys_type = self.data_types.get(device_type, 'BOOL')
            
            var_line = f"    {codesys_name} : {codesys_type};  (* {description} *)"
            
            if device_type == 'INPUT':
                var_sections['VAR_INPUT'].append(var_line)
            elif device_type == 'OUTPUT':
                var_sections['VAR_OUTPUT'].append(var_line)
            else:
                var_sections['VAR'].append(var_line)
        
        # 변수 선언 조립
        declaration = ""
        
        if var_sections['VAR_INPUT']:
            declaration += "VAR_INPUT\n"
            declaration += "\n".join(var_sections['VAR_INPUT'])
            declaration += "\nEND_VAR\n\n"
        
        if var_sections['VAR_OUTPUT']:
            declaration += "VAR_OUTPUT\n"
            declaration += "\n".join(var_sections['VAR_OUTPUT'])
            declaration += "\nEND_VAR\n\n"
        
        if var_sections['VAR']:
            declaration += "VAR\n"
            declaration += "\n".join(var_sections['VAR'])
            declaration += "\nEND_VAR\n\n"
        
        return declaration
    
    def _convert_to_structured_text(self, ladder_rungs: List[Dict[str, Any]]) -> str:
        """
Structured Text (ST) 코드 생성
        """
        st_code = ""
        current_condition = ""
        
        st_code += "(* ===============================\n"
        st_code += "   미쓰비시 GX Works2에서 CODESYS ST로 변환\n"
        st_code += "   주니어 엔지니어를 위한 교육용 변환\n"
        st_code += "   =============================== *)\n\n"
        
        i = 0
        while i < len(ladder_rungs):
            rung = ladder_rungs[i]
            instruction = rung.get('instruction', '')
            device = rung.get('device', '')
            comment = rung.get('comment', '')
            
            codesys_device = self._convert_device_name(device)
            
            if instruction == 'LD':
                # 새로운 래더 런그 시작
                current_condition = codesys_device
                st_code += f"(* 런그 {rung.get('rung_number', i+1)}: {comment} *)\n"
                
            elif instruction == 'LDI':
                current_condition = f"NOT {codesys_device}"
                st_code += f"(* 런그 {rung.get('rung_number', i+1)}: {comment} *)\n"
                
            elif instruction in ['AND', 'ANI']:
                operator = 'AND NOT' if instruction == 'ANI' else 'AND'
                current_condition += f" {operator} {codesys_device}"
                
            elif instruction in ['OR', 'ORI']:
                operator = 'OR NOT' if instruction == 'ORI' else 'OR'
                current_condition += f" {operator} {codesys_device}"
                
            elif instruction == 'OUT':
                st_code += f"IF {current_condition} THEN\n"
                st_code += f"    {codesys_device} := TRUE;\n"
                st_code += f"ELSE\n"
                st_code += f"    {codesys_device} := FALSE;\n"
                st_code += f"END_IF;\n\n"
                current_condition = ""
                
            elif instruction == 'SET':
                st_code += f"IF {current_condition} THEN\n"
                st_code += f"    {codesys_device} := TRUE;\n"
                st_code += f"END_IF;\n\n"
                current_condition = ""
                
            elif instruction == 'RST':
                st_code += f"IF {current_condition} THEN\n"
                st_code += f"    {codesys_device} := FALSE;\n"
                st_code += f"END_IF;\n\n"
                current_condition = ""
            
            i += 1
        
        return st_code
    
    def _convert_to_ladder_diagram(self, ladder_rungs: List[Dict[str, Any]]) -> str:
        """
Ladder Diagram (LD) 코드 생성 (텍스트 형태)
        """
        ld_code = ""
        
        ld_code += "(* ===============================\n"
        ld_code += "   CODESYS Ladder Diagram\n"
        ld_code += "   미쓰비시 래더에서 변환된 코드\n"
        ld_code += "   =============================== *)\n\n"
        
        current_rung = []
        
        for rung in ladder_rungs:
            instruction = rung.get('instruction', '')
            device = rung.get('device', '')
            comment = rung.get('comment', '')
            
            codesys_device = self._convert_device_name(device)
            
            if instruction == 'LD':
                if current_rung:
                    ld_code += self._format_ladder_rung(current_rung)
                    current_rung = []
                
                current_rung.append(f"--[ {codesys_device} ]")
                ld_code += f"(* {comment} *)\n"
                
            elif instruction == 'LDI':
                if current_rung:
                    ld_code += self._format_ladder_rung(current_rung)
                    current_rung = []
                
                current_rung.append(f"--[/{codesys_device}]")
                ld_code += f"(* {comment} *)\n"
                
            elif instruction == 'AND':
                current_rung.append(f"--[ {codesys_device} ]")
                
            elif instruction == 'ANI':
                current_rung.append(f"--[/{codesys_device}]")
                
            elif instruction == 'OR':
                current_rung.append(f"\n\t\t\t\t\t+--[ {codesys_device} ]")
                
            elif instruction == 'ORI':
                current_rung.append(f"\n\t\t\t\t\t+--[/{codesys_device}]")
                
            elif instruction == 'OUT':
                current_rung.append(f"--( {codesys_device} )")
                ld_code += self._format_ladder_rung(current_rung)
                ld_code += "\n"
                current_rung = []
                
            elif instruction in ['SET', 'RST']:
                symbol = 'S' if instruction == 'SET' else 'R'
                current_rung.append(f"--({symbol} {codesys_device} )")
                ld_code += self._format_ladder_rung(current_rung)
                ld_code += "\n"
                current_rung = []
        
        if current_rung:
            ld_code += self._format_ladder_rung(current_rung)
        
        return ld_code
    
    def _format_ladder_rung(self, rung_elements: List[str]) -> str:
        """래더 런그 포매팅"""
        if not rung_elements:
            return ""
        
        # 간단한 래더 표현
        formatted = "|"
        for element in rung_elements:
            formatted += element
        formatted += "|\n"
        
        return formatted
    
    def _convert_device_name(self, device_name: str) -> str:
        """
미쓰비시 디바이스명을 CODESYS 형식으로 변환
        
        예: X001 -> bStartButton, Y001 -> bMotorOutput
        """
        if not device_name:
            return "unknown"
        
        # 디바이스 타입과 번호 분리
        device_type = device_name[0] if device_name else 'M'
        device_number = device_name[1:] if len(device_name) > 1 else '000'
        
        # CODESYS 표준 명명 규칙 적용
        prefix_map = {
            'X': 'bInput',
            'Y': 'bOutput', 
            'M': 'bMemory',
            'D': 'nData',
            'T': 'tTimer',
            'C': 'cCounter'
        }
        
        prefix = prefix_map.get(device_type, 'bVar')
        
        # 숫자 제거 및 의미있는 이름 생성
        try:
            number = int(device_number)
            if device_type == 'X':
                if number == 1:
                    return "bStartButton"
                elif number == 2:
                    return "bEmergencyStop"
                elif number == 3:
                    return "bStopButton"
                else:
                    return f"{prefix}{number:03d}"
            elif device_type == 'Y':
                if number == 1:
                    return "bMotorOutput"
                else:
                    return f"{prefix}{number:03d}"
            elif device_type == 'M':
                if number == 100:
                    return "bRunningStatus"
                else:
                    return f"{prefix}{number:03d}"
            elif device_type == 'T':
                return f"tDelayTimer{number:03d}"
            else:
                return f"{prefix}{number:03d}"
        except ValueError:
            return f"{prefix}{device_number}"
    
    def _generate_function_blocks(self, project_data: Dict[str, Any]) -> str:
        """
함수 블록 생성
        """
        fb_code = ""
        
        # 타이머 함수 블록 예시
        devices = project_data.get('devices', [])
        timer_devices = [d for d in devices if d['type'] == 'TIMER']
        
        if timer_devices:
            fb_code += "(* 타이머 함수 블록 *)\n"
            for timer in timer_devices:
                timer_name = self._convert_device_name(timer['name'])
                fb_code += f"{timer_name}(IN := bStartCondition, PT := T#3S);\n"
                fb_code += f"bTimerOutput := {timer_name}.Q;\n\n"
        
        return fb_code
    
    def _generate_educational_comments(self, project_data: Dict[str, Any]) -> str:
        """
교육적 주석 및 설명 생성
        """
        comments = ""
        
        comments += "(* ===============================\n"
        comments += "   주니어 엔지니어를 위한 설명\n"
        comments += "   ===============================\n\n"
        
        comments += "1. 변수 명명 규칙:\n"
        comments += "   - b + 이름: Boolean 변수 (예: bStartButton)\n"
        comments += "   - n + 이름: 숫자 변수 (예: nSpeed)\n"
        comments += "   - t + 이름: 타이머 (예: tDelayTimer)\n\n"
        
        comments += "2. 기본 데이터 타입:\n"
        comments += "   - BOOL: 참/거짓 (예: TRUE, FALSE)\n"
        comments += "   - INT: 정수 (-32768 ~ 32767)\n"
        comments += "   - REAL: 실수\n\n"
        
        comments += "3. 타이머 사용법:\n"
        comments += "   - TON: On Delay Timer\n"
        comments += "   - PT: 설정 시간 (T#3S = 3초)\n"
        comments += "   - Q: 출력 신호\n\n"
        
        comments += "4. 안전 고려사항:\n"
        comments += "   - 비상정지는 항상 최우선 처리\n"
        comments += "   - 출력 전에 모든 안전 조건 확인\n"
        comments += "   - 타이머를 이용한 부드럽게 시작\n"
        comments += "   =============================== *)\n\n"
        
        return comments
    
    def _generate_conversion_notes(self, project_data: Dict[str, Any]) -> List[str]:
        """
변환 주의사항 생성
        """
        notes = []
        
        notes.append("🎓 교육적 변환: 이해하기 쉬운 코드로 변환했습니다")
        notes.append("⚠️ 안전: 실제 운용 전에 안전 검토가 필요합니다")
        notes.append("🔧 수정: CODESYS IDE에서 추가 수정이 필요할 수 있습니다")
        notes.append("📝 변수명: 의미있는 이름으로 변경하여 사용하세요")
        
        # 기본 데이터 분석
        devices = project_data.get('devices', [])
        if len(devices) > 10:
            notes.append("📈 복잡도: 디바이스가 많습니다. 모듈화를 고려해보세요")
        
        timer_count = len([d for d in devices if d['type'] == 'TIMER'])
        if timer_count > 3:
            notes.append("⏰ 타이머: 타이머가 많습니다. 성능에 주의하세요")
        
        return notes
    
    def _generate_codesys_project_template(self, project_data: Dict[str, Any]) -> str:
        """
완전한 CODESYS 프로젝트 템플릿 생성
        """
        project_info = project_data.get('project_info', {})
        project_name = project_info.get('name', 'ConvertedProject')
        
        template = f"""
(* ===============================
   CODESYS 프로젝트: {project_name}
   미쓰비시 GX Works2에서 변환
   변환 날짜: 2024-01-01
   =============================== *)

PROGRAM PLC_PRG

{self._generate_variable_declarations(project_data.get('devices', []))}

(* 메인 로직 *)
{self._convert_to_structured_text(project_data.get('ladder_rungs', []))}

{self._generate_function_blocks(project_data)}

END_PROGRAM

{self._generate_educational_comments(project_data)}
        """
        
        return template.strip()

    def convert_with_options(self, project_data: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        옵션을 적용하여 CODESYS 코드로 변환

        Args:
            project_data: GXW 파서에서 추출한 프로젝트 데이터
            options: 변환 옵션
                - comment_style: 'korean'|'english' (기본값: 'korean')
                - naming_style: 'descriptive'|'original'|'compact' (기본값: 'descriptive')
                - include_safety: Boolean (기본값: True)
                - output_format: 'st'|'ld'|'both' (기본값: 'both')
                - optimization_level: 'educational'|'production' (기본값: 'educational')

        Returns:
            변환 옵션이 적용된 CODESYS 코드
        """
        if options is None:
            options = {}

        # 기본 옵션 설정
        default_options = {
            'comment_style': 'korean',
            'naming_style': 'descriptive',
            'include_safety': True,
            'output_format': 'both',
            'optimization_level': 'educational'
        }

        # 옵션 병합
        merged_options = {**default_options, **options}

        try:
            logger.info(f"옵션 적용 CODESYS 변환 시작: {merged_options}")

            # 옵션에 따른 전처리
            processed_data = self._apply_conversion_options(project_data, merged_options)

            # 기본 변환 수행
            base_result = self.convert(processed_data)

            if not base_result.get('success', False):
                return base_result

            # 옵션별 후처리
            result = self._post_process_with_options(base_result, merged_options)

            # 추가 정보 포함
            result['conversion_options'] = merged_options
            result['documentation'] = self._generate_option_based_documentation(merged_options)

            return result

        except Exception as e:
            logger.error(f"옵션 적용 변환 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'structured_text': '// 옵션 적용 변환 오류 발생',
                'conversion_notes': [f'옵션 적용 중 오류 발생: {e}']
            }

    def _apply_conversion_options(self, project_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """변환 옵션을 프로젝트 데이터에 적용"""
        processed_data = project_data.copy()

        # 이름 변환 스타일 적용
        if options['naming_style'] == 'original':
            # 원본 미쓰비시 이름 유지
            self._preserve_original_names = True
        elif options['naming_style'] == 'compact':
            # 간단한 이름 사용
            self._use_compact_names = True

        return processed_data

    def _post_process_with_options(self, result: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """옵션에 따른 후처리"""

        # 영어 주석으로 변환
        if options['comment_style'] == 'english':
            result['structured_text'] = self._translate_comments_to_english(result['structured_text'])
            result['ladder_diagram'] = self._translate_comments_to_english(result['ladder_diagram'])

        # 안전 코드 제거 (요청시)
        if not options['include_safety']:
            result['structured_text'] = self._remove_safety_code(result['structured_text'])

        # 출력 형식 필터링
        if options['output_format'] == 'st':
            result['ladder_diagram'] = '(* Ladder Diagram not requested *)'
        elif options['output_format'] == 'ld':
            result['structured_text'] = '(* Structured Text not requested *)'

        # 프로덕션 최적화
        if options['optimization_level'] == 'production':
            result['structured_text'] = self._optimize_for_production(result['structured_text'])

        return result

    def _translate_comments_to_english(self, code: str) -> str:
        """한국어 주석을 영어로 변환"""
        translations = {
            '미쓰비시': 'Mitsubishi',
            '변환': 'Conversion',
            '주니어 엔지니어': 'Junior Engineer',
            '교육용': 'Educational',
            '런그': 'Rung',
            '타이머': 'Timer',
            '안전': 'Safety',
            '시작': 'Start',
            '정지': 'Stop',
            '비상정지': 'Emergency Stop'
        }

        translated = code
        for korean, english in translations.items():
            translated = translated.replace(korean, english)

        return translated

    def _remove_safety_code(self, code: str) -> str:
        """안전 관련 코드 제거"""
        # 안전 관련 주석과 코드 라인 제거
        lines = code.split('\n')
        filtered_lines = []

        for line in lines:
            if not any(keyword in line.lower() for keyword in ['안전', 'safety', 'emergency', '비상']):
                filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    def _optimize_for_production(self, code: str) -> str:
        """프로덕션용 최적화"""
        # 교육용 주석 제거
        lines = code.split('\n')
        optimized_lines = []

        skip_section = False
        for line in lines:
            if '교육' in line or '설명' in line:
                skip_section = True
            elif line.strip().startswith('(*') and line.strip().endswith('*)'):
                skip_section = False
                continue
            elif not skip_section:
                optimized_lines.append(line)

        return '\n'.join(optimized_lines)

    def _generate_option_based_documentation(self, options: Dict[str, Any]) -> str:
        """옵션 기반 문서 생성"""
        doc = "=== 변환 옵션 적용 결과 ===\n\n"

        doc += f"주석 언어: {options['comment_style']}\n"
        doc += f"명명 규칙: {options['naming_style']}\n"
        doc += f"안전 코드 포함: {'예' if options['include_safety'] else '아니오'}\n"
        doc += f"출력 형식: {options['output_format']}\n"
        doc += f"최적화 수준: {options['optimization_level']}\n\n"

        if options['optimization_level'] == 'production':
            doc += "⚠️ 프로덕션 최적화가 적용되었습니다. 실제 운용 전 검토가 필요합니다.\n"

        if not options['include_safety']:
            doc += "⚠️ 안전 코드가 제거되었습니다. 실제 사용 시 안전 기능을 별도로 구현하세요.\n"

        return doc