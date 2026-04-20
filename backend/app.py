# -*- coding: utf-8 -*-
"""
全学段数学证明导师系统 - 主应用
集成初中、高中、大学三个学段的智能数学证明辅导
"""

import os
import json
import re
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# 导入各学段模块
from junior.analyzer import JuniorAnalyzer
from senior.analyzer import SeniorAnalyzer
from university.analyzer import UniversityAnalyzer
from shared.ocr_service import OCRService
from shared.report_generator import ReportGenerator
from shared.user_manager import UserManager
from router import LevelRouter

app = Flask(__name__)
CORS(app)

# 初始化各模块
ocr_service = OCRService()
level_router = LevelRouter()
junior_analyzer = JuniorAnalyzer()
senior_analyzer = SeniorAnalyzer()
university_analyzer = UniversityAnalyzer()
report_generator = ReportGenerator()
user_manager = UserManager()

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_keywords(content):
    """从文本内容中提取关键词"""
    # 移除常见标点和空白
    content = re.sub(r'[\s，。、；：！？""''（）\[\]（）]+', ' ', content)
    
    # 数学证明特征词定义
    patterns = {
        'junior_high': [
            '全等', '三角形', '平行', '垂直', '角平分线', '中点', 
            '等腰', '直角', '勾股', '圆', '弧', '弦', '圆周角',
            '证明', '因为', '所以', '等于', '平行四边形', '矩形',
            '菱形', '正方形', '梯形', '多边形', '内角', '外角'
        ],
        'senior_high': [
            '导数', '微分', '积分', '向量', '圆锥曲线', '椭圆',
            '双曲线', '抛物线', '数学归纳法', '数列', '极限',
            '函数', '不等式', '立体几何', '空间向量', '面角',
            '二面角', '概率', '排列', '组合', '二项式', '复数',
            '矩阵', '行列式', '正弦', '余弦', '正切', '恒等式'
        ],
        'university': [
            'ε-δ', '极限', '连续', '可导', '可积', '一致收敛',
            '群', '环', '域', '同态', '同构', '子群', '陪集',
            '拓扑', '开集', '闭集', '紧致', '连通', '测度',
            'Lebesgue', 'Borel', 'Hilbert', 'Banach', '泛函',
            '复变', '解析', '奇点', '留数', '级数', '微分方程',
            '特征值', '特征向量', '线性变换', 'Jordan标准形'
        ]
    }
    
    # 统计各学段关键词出现次数
    scores = {'junior_high': 0, 'senior_high': 0, 'university': 0}
    
    for level, keywords in patterns.items():
        for keyword in keywords:
            if keyword in content:
                scores[level] += 1
    
    return scores


def is_junior_high(keywords):
    """判断是否为初中特征"""
    return keywords['junior_high'] > keywords['senior_high'] and \
           keywords['junior_high'] > keywords['university']


def is_senior_high(keywords):
    """判断是否为高中特征"""
    return keywords['senior_high'] > keywords['junior_high'] and \
           keywords['senior_high'] > keywords['university']


def is_university(keywords):
    """判断是否为大学特征"""
    return keywords['university'] > keywords['junior_high'] and \
           keywords['university'] > keywords['senior_high']


@app.route('/')
def index():
    """主页"""
    return jsonify({
        'name': '全学段数学证明导师系统',
        'version': '1.0.0',
        'levels': ['junior_high', 'senior_high', 'university'],
        'description': '集成初中、高中、大学三个学段的智能数学证明辅导系统'
    })


@app.route('/api/identify_level', methods=['POST'])
def identify_level():
    """
    学段识别API
    根据题目内容自动识别学段
    """
    data = request.get_json()
    content = data.get('content', '')
    
    if not content:
        return jsonify({'error': '内容不能为空'}), 400
    
    keywords = extract_keywords(content)
    max_score = max(keywords.values())
    
    if max_score == 0:
        # 无法识别，返回最可能的学段
        return jsonify({
            'level': 'unknown',
            'confidence': 0.0,
            'suggestion': '无法识别学段，请手动选择或提供更详细的题目内容'
        })
    
    # 计算置信度
    total = sum(keywords.values())
    confidence = max_score / total if total > 0 else 0
    
    # 确定学段
    if is_junior_high(keywords):
        level = 'junior_high'
        level_name = '初中数学'
    elif is_senior_high(keywords):
        level = 'senior_high'
        level_name = '高中数学'
    elif is_university(keywords):
        level = 'university'
        level_name = '大学数学'
    else:
        level = 'auto_detect'
        level_name = '待定'
    
    return jsonify({
        'level': level,
        'level_name': level_name,
        'confidence': round(confidence, 2),
        'keywords': keywords,
        'suggestion': f'根据题目内容分析，最可能的学段是：{level_name}'
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    统一分析API
    对上传的证明题进行分析
    """
    # 获取请求数据
    data = request.get_json()
    
    # 图片或文本内容
    image_base64 = data.get('image')
    content = data.get('content', '')
    level = data.get('level', 'auto')  # auto, junior_high, senior_high, university
    
    # OCR识别（如果提供了图片）
    if image_base64:
        try:
            content = ocr_service.recognize(image_base64)
        except Exception as e:
            return jsonify({'error': f'OCR识别失败: {str(e)}'}), 500
    
    if not content:
        return jsonify({'error': '题目内容不能为空'}), 400
    
    # 学段识别
    if level == 'auto':
        keywords = extract_keywords(content)
        if is_junior_high(keywords):
            level = 'junior_high'
        elif is_senior_high(keywords):
            level = 'senior_high'
        elif is_university(keywords):
            level = 'university'
        else:
            level = 'junior_high'  # 默认初中
    
    # 调用相应学段的分析器
    try:
        if level == 'junior_high':
            result = junior_analyzer.analyze(content)
        elif level == 'senior_high':
            result = senior_analyzer.analyze(content)
        elif level == 'university':
            result = university_analyzer.analyze(content)
        else:
            return jsonify({'error': '未知的学段类型'}), 400
        
        return jsonify({
            'level': level,
            'level_name': get_level_name(level),
            'content': content,
            'result': result
        })
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500


@app.route('/api/switch_level', methods=['POST'])
def switch_level():
    """
    学段切换API
    手动切换到指定学段
    """
    data = request.get_json()
    level = data.get('level')
    
    valid_levels = ['junior_high', 'senior_high', 'university']
    if level not in valid_levels:
        return jsonify({
            'error': '无效的学段',
            'valid_levels': valid_levels
        }), 400
    
    return jsonify({
        'success': True,
        'level': level,
        'level_name': get_level_name(level),
        'description': get_level_description(level)
    })


@app.route('/api/report', methods=['GET'])
def get_report():
    """
    获取学习报告API
    """
    user_id = request.args.get('user_id', 'default')
    report = report_generator.generate_report(user_id)
    return jsonify(report)


@app.route('/api/knowledge/<level>/<topic>', methods=['GET'])
def get_knowledge(level, topic):
    """
    获取知识库内容
    """
    knowledge_path = f'knowledge_base/{get_level_dir(level)}/{topic}.md'
    
    if not os.path.exists(knowledge_path):
        return jsonify({'error': '知识库内容不存在'}), 404
    
    try:
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({
            'level': level,
            'topic': topic,
            'content': content
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/problems/<level>/<topic>', methods=['GET'])
def get_problems(level, topic):
    """
    获取题库内容
    """
    problems_path = f'knowledge_base/{get_level_dir(level)}/题库/{topic}题库.json'
    
    if not os.path.exists(problems_path):
        return jsonify({'error': '题库不存在'}), 404
    
    try:
        with open(problems_path, 'r', encoding='utf-8') as f:
            problems = json.load(f)
        return jsonify({
            'level': level,
            'topic': topic,
            'problems': problems
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_level_name(level):
    """获取学段中文名称"""
    names = {
        'junior_high': '初中数学',
        'senior_high': '高中数学',
        'university': '大学数学'
    }
    return names.get(level, '未知')


def get_level_description(level):
    """获取学段描述"""
    descriptions = {
        'junior_high': '初中数学证明模块，主要涵盖平面几何、代数证明等内容',
        'senior_high': '高中数学证明模块，涵盖代数、几何、函数、数列等多个领域',
        'university': '大学数学证明模块，包括数学分析、高等代数、抽象代数等课程'
    }
    return descriptions.get(level, '')


def get_level_dir(level):
    """获取学段目录名"""
    dirs = {
        'junior_high': '初中',
        'senior_high': '高中',
        'university': '大学'
    }
    return dirs.get(level, '')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
