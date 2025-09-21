#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLC Mentor - 래더 로직 시각화 엔진
주니어 엔지니어를 위한 직관적인 래더 다이어그램 시각화
"""

class LadderVisualizer:
    """래더 로직을 시각적으로 표현하는 클래스"""

    def __init__(self):
        self.symbols = {
            # 기본 심볼
            'contact_open': '--[ ]--',      # 상시 열린 접점
            'contact_closed': '--[/]--',    # 상시 닫힌 접점
            'coil': '---( )---',           # 출력 코일
            'set_coil': '---(S)---',       # 셋 코일
            'reset_coil': '---(R)---',     # 리셋 코일
            'timer_on': '--[TON]--',       # 온 딜레이 타이머
            'timer_off': '--[TOF]--',      # 오프 딜레이 타이머
            'counter_up': '--[CTU]--',     # 업 카운터
            'counter_down': '--[CTD]--',   # 다운 카운터
            'compare_gt': '--[>]--',       # 크다 비교
            'compare_lt': '--[<]--',       # 작다 비교
            'compare_eq': '--[=]--',       # 같다 비교

            # 연결선
            'horizontal': '------',         # 수평선
            'vertical': '|',               # 수직선
            'junction': '+',               # 접점
            'left_rail': '|',              # 왼쪽 레일
            'right_rail': '|',             # 오른쪽 레일
        }

        # 디바이스 타입별 색상 (HTML 출력용)
        self.device_colors = {
            'X': '#28a745',  # 입력 - 녹색
            'Y': '#007bff',  # 출력 - 파란색
            'M': '#ffc107',  # 메모리 - 노란색
            'T': '#dc3545',  # 타이머 - 빨간색
            'C': '#17a2b8',  # 카운터 - 청록색
            'D': '#6f42c1',  # 데이터 - 보라색
        }

    def visualize_ladder(self, ladder_data, output_format='ascii'):
        """
        래더 로직을 시각화

        Args:
            ladder_data: 파싱된 래더 로직 데이터
            output_format: 출력 형식 ('ascii', 'html', 'svg')

        Returns:
            시각화된 래더 다이어그램 문자열
        """
        if output_format == 'ascii':
            return self._generate_ascii_ladder(ladder_data)
        elif output_format == 'html':
            return self._generate_html_ladder(ladder_data)
        elif output_format == 'svg':
            return self._generate_svg_ladder(ladder_data)
        else:
            raise ValueError(f"지원하지 않는 출력 형식: {output_format}")

    def _generate_ascii_ladder(self, ladder_data):
        """ASCII 형식의 래더 다이어그램 생성"""
        if not ladder_data or 'networks' not in ladder_data:
            return self._get_example_ascii_ladder()

        result = []
        result.append("=" * 80)
        result.append(" " * 25 + "래더 다이어그램")
        result.append("=" * 80)

        for i, network in enumerate(ladder_data['networks'], 1):
            result.append(f"\n// 네트워크 {i}: {network.get('comment', '설명 없음')}")
            ladder_line = self._build_network_ascii(network)
            result.append(ladder_line)

        result.append("\n" + "=" * 80)
        result.append("범례:")
        result.append("[ ] : 상시 열린 접점    [/] : 상시 닫힌 접점")
        result.append("( ) : 출력 코일        (S) : 셋 코일")
        result.append("(R) : 리셋 코일        TON : 온 딜레이 타이머")
        result.append("CTU : 업 카운터        > : 크다 비교")
        result.append("=" * 80)

        return '\n'.join(result)

    def _build_network_ascii(self, network):
        """개별 네트워크의 ASCII 표현 생성"""
        if not network or 'elements' not in network:
            return "|--[예제]--+--[접점]----------(출력)--|"

        # 기본 구조: 좌측 레일 + 로직 + 출력 + 우측 레일
        line = "|"

        elements = network['elements']
        for i, element in enumerate(elements):
            if element.get('type') == 'contact':
                device = element.get('device', 'X000')
                if element.get('inverted', False):
                    line += f"--[/{device}]"
                else:
                    line += f"--[{device}]"

            elif element.get('type') == 'coil':
                device = element.get('device', 'Y000')
                if element.get('set', False):
                    line += f"---(S {device})---"
                elif element.get('reset', False):
                    line += f"---(R {device})---"
                else:
                    line += f"---({device})---"

            elif element.get('type') == 'timer':
                device = element.get('device', 'T0')
                preset = element.get('preset', 'K50')
                line += f"--[TON {device}]--"
                line += f"\n|    PT:{preset}      "

            elif element.get('type') == 'counter':
                device = element.get('device', 'C0')
                preset = element.get('preset', 'K10')
                line += f"--[CTU {device}]--"
                line += f"\n|    SV:{preset}      "

            elif element.get('type') == 'compare':
                operation = element.get('operation', '>')
                operand1 = element.get('operand1', 'D0')
                operand2 = element.get('operand2', 'K100')
                line += f"--[{operand1}{operation}{operand2}]"

            # 연결선 추가
            if i < len(elements) - 1:
                line += "--"

        line += "--|"
        return line

    def _generate_html_ladder(self, ladder_data):
        """HTML 형식의 래더 다이어그램 생성"""
        if not ladder_data or 'networks' not in ladder_data:
            return self._get_example_html_ladder()

        html = ['<div class="ladder-container">']

        for i, network in enumerate(ladder_data['networks'], 1):
            html.append(f'<div class="network" id="network-{i}">')
            html.append(f'<div class="network-header">네트워크 {i}: {network.get("comment", "설명 없음")}</div>')
            html.append('<div class="ladder-line">')

            # 좌측 레일
            html.append('<span class="rail left-rail">|</span>')

            # 로직 요소들
            if 'elements' in network:
                for element in network['elements']:
                    html.append(self._element_to_html(element))

            # 우측 레일
            html.append('<span class="rail right-rail">|</span>')
            html.append('</div>')
            html.append('</div>')

        html.append('</div>')

        # CSS 스타일 추가
        html.append(self._get_ladder_css())

        return '\n'.join(html)

    def _element_to_html(self, element):
        """개별 요소를 HTML로 변환"""
        element_type = element.get('type', 'contact')
        device = element.get('device', 'X000')
        device_type = device[0] if device else 'X'
        color = self.device_colors.get(device_type, '#6c757d')

        if element_type == 'contact':
            symbol = '[/]' if element.get('inverted', False) else '[ ]'
            return f'<span class="contact" style="color: {color}">--{symbol}--</span>'

        elif element_type == 'coil':
            if element.get('set', False):
                symbol = f'(S {device})'
            elif element.get('reset', False):
                symbol = f'(R {device})'
            else:
                symbol = f'({device})'
            return f'<span class="coil" style="color: {color}">--{symbol}--</span>'

        elif element_type == 'timer':
            preset = element.get('preset', 'K50')
            return f'<span class="timer" style="color: {color}">[TON {device} PT:{preset}]</span>'

        elif element_type == 'counter':
            preset = element.get('preset', 'K10')
            return f'<span class="counter" style="color: {color}">[CTU {device} SV:{preset}]</span>'

        elif element_type == 'compare':
            operation = element.get('operation', '>')
            operand1 = element.get('operand1', 'D0')
            operand2 = element.get('operand2', 'K100')
            return f'<span class="compare">[{operand1}{operation}{operand2}]</span>'

        return '<span class="unknown">--[?]--</span>'

    def _get_ladder_css(self):
        """래더 다이어그램용 CSS 스타일"""
        return '''
<style>
.ladder-container {
    font-family: 'Courier New', monospace;
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    border: 2px solid #dee2e6;
}

.network {
    margin-bottom: 20px;
    padding: 15px;
    background-color: white;
    border-radius: 5px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.network-header {
    font-weight: bold;
    color: #495057;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1px solid #dee2e6;
}

.ladder-line {
    font-size: 16px;
    line-height: 1.5;
    white-space: nowrap;
    overflow-x: auto;
}

.rail {
    font-weight: bold;
    color: #343a40;
}

.contact, .coil, .timer, .counter, .compare {
    font-weight: bold;
    margin: 0 2px;
}

.contact:hover, .coil:hover, .timer:hover, .counter:hover, .compare:hover {
    background-color: #e9ecef;
    border-radius: 3px;
    cursor: pointer;
}
</style>
        '''

    def _generate_svg_ladder(self, ladder_data):
        """SVG 형식의 래더 다이어그램 생성"""
        if not ladder_data or 'networks' not in ladder_data:
            return self._get_example_svg_ladder()

        # SVG 구현은 복잡하므로 기본 구조만 제공
        svg = [
            '<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">',
            '<rect width="100%" height="100%" fill="#f8f9fa"/>',
            '<text x="400" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold">래더 다이어그램</text>',
        ]

        y_pos = 60
        for i, network in enumerate(ladder_data['networks'], 1):
            # 네트워크 제목
            svg.append(f'<text x="50" y="{y_pos}" font-family="Arial" font-size="14" fill="#495057">네트워크 {i}</text>')
            y_pos += 30

            # 좌측 레일
            svg.append(f'<line x1="50" y1="{y_pos}" x2="50" y2="{y_pos + 40}" stroke="#343a40" stroke-width="2"/>')

            # 수평선
            svg.append(f'<line x1="50" y1="{y_pos + 20}" x2="750" y2="{y_pos + 20}" stroke="#343a40" stroke-width="2"/>')

            # 우측 레일
            svg.append(f'<line x1="750" y1="{y_pos}" x2="750" y2="{y_pos + 40}" stroke="#343a40" stroke-width="2"/>')

            y_pos += 80

        svg.append('</svg>')
        return '\n'.join(svg)

    def _get_example_ascii_ladder(self):
        """예제 ASCII 래더 다이어그램"""
        return '''
================================================================================
                         래더 다이어그램 (예제)
================================================================================

// 네트워크 1: 기본 모터 제어
|--[X000]--[X001]--+--[X002]----------(Y000)--|
|                   |                          |
|                   +--[X003]--[T0]------------|

// 네트워크 2: 타이머 제어
|--[Y000]---------------------------[TON T0]--|
|                                   PT:K50    |

// 네트워크 3: 카운터 제어
|--[X004]---------------------------[CTU C0]--|
|                                   SV:K10    |

// 네트워크 4: 카운터 출력
|--[C0]--------------------------------(Y001)--|

================================================================================
범례:
[ ] : 상시 열린 접점    [/] : 상시 닫힌 접점
( ) : 출력 코일        (S) : 셋 코일
(R) : 리셋 코일        TON : 온 딜레이 타이머
CTU : 업 카운터        > : 크다 비교
================================================================================
        '''

    def _get_example_html_ladder(self):
        """예제 HTML 래더 다이어그램"""
        return '''
<div class="ladder-container">
    <div class="network">
        <div class="network-header">네트워크 1: 기본 모터 제어</div>
        <div class="ladder-line">
            <span class="rail left-rail">|</span>
            <span class="contact" style="color: #28a745">--[X000]--</span>
            <span class="contact" style="color: #28a745">--[X001]--</span>
            <span class="coil" style="color: #007bff">--(Y000)--</span>
            <span class="rail right-rail">|</span>
        </div>
    </div>

    <div class="network">
        <div class="network-header">네트워크 2: 타이머 제어</div>
        <div class="ladder-line">
            <span class="rail left-rail">|</span>
            <span class="contact" style="color: #007bff">--[Y000]--</span>
            <span class="timer" style="color: #dc3545">--[TON T0 PT:K50]--</span>
            <span class="rail right-rail">|</span>
        </div>
    </div>
</div>
''' + self._get_ladder_css()

    def _get_example_svg_ladder(self):
        """예제 SVG 래더 다이어그램"""
        return '''
<svg width="800" height="300" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#f8f9fa"/>
    <text x="400" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="bold">래더 다이어그램 (예제)</text>

    <!-- 네트워크 1 -->
    <text x="50" y="70" font-family="Arial" font-size="14" fill="#495057">네트워크 1: 기본 모터 제어</text>

    <!-- 좌측 레일 -->
    <line x1="50" y1="90" x2="50" y2="130" stroke="#343a40" stroke-width="2"/>

    <!-- 수평선 -->
    <line x1="50" y1="110" x2="700" y2="110" stroke="#343a40" stroke-width="2"/>

    <!-- 접점들 -->
    <rect x="100" y="100" width="60" height="20" fill="white" stroke="#28a745" stroke-width="2"/>
    <text x="130" y="115" text-anchor="middle" font-family="Arial" font-size="12" fill="#28a745">X000</text>

    <rect x="200" y="100" width="60" height="20" fill="white" stroke="#28a745" stroke-width="2"/>
    <text x="230" y="115" text-anchor="middle" font-family="Arial" font-size="12" fill="#28a745">X001</text>

    <!-- 출력 코일 -->
    <circle cx="600" cy="110" r="15" fill="white" stroke="#007bff" stroke-width="2"/>
    <text x="600" y="115" text-anchor="middle" font-family="Arial" font-size="12" fill="#007bff">Y000</text>

    <!-- 우측 레일 -->
    <line x1="700" y1="90" x2="700" y2="130" stroke="#343a40" stroke-width="2"/>
</svg>
        '''

    def analyze_ladder_complexity(self, ladder_data):
        """래더 로직의 복잡도 분석"""
        if not ladder_data or 'networks' not in ladder_data:
            return {
                'complexity_level': 'simple',
                'total_networks': 0,
                'total_elements': 0,
                'device_types': {},
                'recommendations': ['예제 데이터를 사용하여 학습을 시작하세요.']
            }

        networks = ladder_data['networks']
        total_networks = len(networks)
        total_elements = 0
        device_types = {}

        for network in networks:
            if 'elements' in network:
                total_elements += len(network['elements'])
                for element in network['elements']:
                    device = element.get('device', '')
                    if device:
                        device_type = device[0]
                        device_types[device_type] = device_types.get(device_type, 0) + 1

        # 복잡도 계산
        if total_elements < 10:
            complexity_level = 'simple'
        elif total_elements < 30:
            complexity_level = 'intermediate'
        else:
            complexity_level = 'complex'

        # 권장사항 생성
        recommendations = self._generate_recommendations(complexity_level, device_types)

        return {
            'complexity_level': complexity_level,
            'total_networks': total_networks,
            'total_elements': total_elements,
            'device_types': device_types,
            'recommendations': recommendations
        }

    def _generate_recommendations(self, complexity_level, device_types):
        """복잡도에 따른 학습 권장사항 생성"""
        recommendations = []

        if complexity_level == 'simple':
            recommendations.append("초보자에게 적합한 간단한 로직입니다.")
            recommendations.append("기본 접점과 코일의 동작을 이해해보세요.")
        elif complexity_level == 'intermediate':
            recommendations.append("중급 수준의 로직입니다.")
            recommendations.append("타이머와 카운터의 활용을 학습해보세요.")
        else:
            recommendations.append("고급 수준의 복잡한 로직입니다.")
            recommendations.append("단계별로 나누어 분석하는 것을 권장합니다.")

        # 디바이스 타입별 권장사항
        if 'T' in device_types:
            recommendations.append("타이머 명령어가 포함되어 있습니다. 시간 제어 학습을 권장합니다.")
        if 'C' in device_types:
            recommendations.append("카운터 명령어가 포함되어 있습니다. 카운팅 로직을 학습해보세요.")
        if len(device_types) > 3:
            recommendations.append("다양한 디바이스가 사용되었습니다. 각 디바이스의 역할을 확인해보세요.")

        return recommendations


def create_visualizer():
    """래더 시각화기 인스턴스 생성"""
    return LadderVisualizer()


if __name__ == "__main__":
    # 테스트
    visualizer = LadderVisualizer()

    # 예제 데이터로 테스트
    example_data = {
        'networks': [
            {
                'comment': '기본 모터 제어',
                'elements': [
                    {'type': 'contact', 'device': 'X000'},
                    {'type': 'contact', 'device': 'X001'},
                    {'type': 'coil', 'device': 'Y000'}
                ]
            }
        ]
    }

    print("ASCII 형식:")
    print(visualizer.visualize_ladder(example_data, 'ascii'))

    print("\n복잡도 분석:")
    analysis = visualizer.analyze_ladder_complexity(example_data)
    print(f"복잡도: {analysis['complexity_level']}")
    print(f"총 네트워크: {analysis['total_networks']}")
    print(f"총 요소: {analysis['total_elements']}")