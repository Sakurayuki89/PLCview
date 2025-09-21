#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLC Mentor - 주니어 엔지니어를 위한 PLC 코드 학습 도구
간단하고 직관적인 Flask 웹 애플리케이션
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from app.parser.gxw_parser import GXWParser
from app.converter.codesys_converter import CodesysConverter
from app.educator.plc_educator import PLCEducator
from app.visualizer.ladder_visualizer import LadderVisualizer
import json

# Flask 앱 초기화
app = Flask(__name__)
app.config['SECRET_KEY'] = 'plc-mentor-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 업로드 폴더 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'gxw', 'gx2', 'gx3'}

def allowed_file(filename):
    """허용된 파일 확장자 검증"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """GXW 파일 업로드 및 분석"""
    if 'file' not in request.files:
        return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # GXW 파일 파싱
            parser = GXWParser()
            project_data = parser.parse(filepath)

            # 교육적 설명 생성
            educator = PLCEducator()
            explanations = educator.explain_project(project_data)

            # 래더 로직 시각화
            visualizer = LadderVisualizer()
            ladder_ascii = visualizer.visualize_ladder(project_data, 'ascii')
            ladder_html = visualizer.visualize_ladder(project_data, 'html')
            complexity_analysis = visualizer.analyze_ladder_complexity(project_data)

            # CODESYS 변환
            converter = CodesysConverter()
            codesys_code = converter.convert(project_data)

            return jsonify({
                'success': True,
                'filename': filename,
                'project_data': project_data,
                'explanations': explanations,
                'ladder_visualization': {
                    'ascii': ladder_ascii,
                    'html': ladder_html,
                    'complexity': complexity_analysis
                },
                'codesys_code': codesys_code
            })
            
        except Exception as e:
            return jsonify({'error': f'파일 분석 중 오류: {str(e)}'}), 500
    
    return jsonify({'error': '지원되지 않는 파일 형식입니다'}), 400

@app.route('/analyze')
def analyze_page():
    """분석 결과 페이지"""
    return render_template('analyze.html')

@app.route('/learn')
def learn_page():
    """학습 페이지"""
    educator = PLCEducator()
    tutorials = educator.get_tutorials()
    return render_template('learn.html', tutorials=tutorials)

@app.route('/convert')
def convert_page():
    """변환 페이지"""
    return render_template('convert.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    """GXW 파일을 CODESYS로 변환"""
    if 'file' not in request.files:
        return jsonify({'error': '파일이 선택되지 않았습니다'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '파일이 선택되지 않았습니다'}), 400

    # 변환 옵션 받기
    options = {}
    if 'options' in request.form:
        try:
            options = json.loads(request.form['options'])
        except:
            options = {}

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # GXW 파일 파싱
            parser = GXWParser()
            project_data = parser.parse(filepath)

            # CODESYS 변환 (옵션 적용)
            converter = CodesysConverter()
            conversion_result = converter.convert_with_options(project_data, options)

            # 래더 시각화 (변환 결과 확인용)
            visualizer = LadderVisualizer()
            complexity = visualizer.analyze_ladder_complexity(project_data)

            return jsonify({
                'success': True,
                'stCode': conversion_result.get('structured_text', ''),
                'ldCode': conversion_result.get('ladder_diagram', ''),
                'documentation': conversion_result.get('documentation', ''),
                'stats': {
                    'totalInstructions': complexity.get('total_elements', 0),
                    'networks': complexity.get('total_networks', 0),
                    'devices': len(complexity.get('device_types', {})),
                    'warnings': len([r for r in complexity.get('recommendations', []) if '주의' in r])
                }
            })

        except Exception as e:
            return jsonify({'error': f'변환 중 오류: {str(e)}'}), 500

    return jsonify({'error': '지원되지 않는 파일 형식입니다'}), 400

@app.route('/api/examples')
def get_examples():
    """예제 프로젝트 목록 반환"""
    examples_dir = 'examples'
    examples = []
    
    if os.path.exists(examples_dir):
        for filename in os.listdir(examples_dir):
            if filename.endswith('.json'):  # 예제는 JSON 형태로 저장
                examples.append({
                    'name': filename.replace('.json', ''),
                    'file': filename
                })
    
    return jsonify(examples)

@app.route('/api/example/<example_name>')
def get_example(example_name):
    """특정 예제 프로젝트 반환"""
    try:
        example_path = os.path.join('examples', f'{example_name}.json')
        with open(example_path, 'r', encoding='utf-8') as f:
            example_data = json.load(f)
        return jsonify(example_data)
    except FileNotFoundError:
        return jsonify({'error': '예제를 찾을 수 없습니다'}), 404
    except Exception as e:
        return jsonify({'error': f'예제 로드 오류: {str(e)}'}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """정적 파일 서빙"""
    return send_from_directory('static', filename)

@app.route('/favicon.ico')
def favicon():
    """파비콘 제공"""
    return '', 204  # No Content

if __name__ == '__main__':
    # 개발 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)