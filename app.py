# -*- coding: utf-8 -*-
"""
全学段数学证明导师系统 - 简化版后端
使用 DeepSeek API 进行 AI 对话和图片识别
支持 Railway 免费部署
"""

import os
import re
import base64
import json
from datetime import datetime
from io import BytesIO
from PIL import Image

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取前端目录路径
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')

# 初始化 DeepSeek 客户端
client = None
if DEEPSEEK_API_KEY:
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def init_deepseek_client():
    """初始化 DeepSeek 客户端"""
    global client
    if not client and DEEPSEEK_API_KEY:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return client is not None


# 学段配置
LEVEL_CONFIG = {
    'junior': {
        'name': '初中',
        'name_en': 'Junior High',
        'description': '初中数学证明',
        'keywords': [
            '全等', '三角形', '平行', '垂直', '角平分线', '中点',
            '等腰', '直角', '勾股', '圆', '弧', '弦', '圆周角',
            '平行四边形', '矩形', '菱形', '正方形', '梯形',
            '多边形', '内角', '外角', '对顶角', '同位角', '内错角',
            '因式分解', '方程', '一元', '二元', '方程组'
        ],
        'system_prompt': '''你是一位资深的初中数学教师，专注于帮助学生理解和掌握初中数学证明题。
你擅长：
- 三角形全等证明（SSS、SAS、ASA、AAS、HL）
- 平行四边形及特殊四边形的性质与判定
- 圆的性质、弧、弦、圆周角定理
- 勾股定理及其应用
- 角平分线、线段垂直平分线的性质
- 代数证明（因式分解、方程证明）

请用清晰、耐心、鼓励的方式引导学生思考，不要直接给出完整答案，而是通过提问和提示帮助学生自己发现证明思路。
回答要简洁明了，使用中文，适当使用数学符号。'''
    },
    'senior': {
        'name': '高中',
        'name_en': 'Senior High',
        'description': '高中数学证明',
        'keywords': [
            '导数', '微分', '积分', '极限', '连续', '可导',
            '向量', '数量积', '向量积', '空间向量',
            '椭圆', '双曲线', '抛物线', '圆锥曲线', '焦点', '准线',
            '数学归纳法', '归纳', '递推', '数列',
            '立体几何', '空间', '面角', '二面角', '体积',
            '正弦', '余弦', '正切', '恒等式', '和差化积',
            '不等式', '均值不等式', '概率', '排列', '组合'
        ],
        'system_prompt': '''你是一位专业的高中数学教师，专注于高中数学证明题的辅导。
你擅长：
- 导数与微分证明题
- 数学归纳法的应用
- 空间向量与立体几何证明
- 圆锥曲线（椭圆、双曲线、抛物线）的证明
- 三角函数恒等式证明
- 不等式证明（均值不等式、柯西不等式等）
- 数列与递推关系证明

请提供严谨、逻辑清晰的证明指导，帮助学生理解证明的核心思路和方法。
使用规范的数学语言，适当配合图形描述（文字描述）。
回答要专业但易于理解。'''
    },
    'university': {
        'name': '大学',
        'name_en': 'University',
        'description': '大学数学证明',
        'keywords': [
            'ε-δ', '极限', '连续', '可导', '可积', '一致收敛',
            'Borel', 'Lebesgue', 'Riemann', 'Cauchy',
            '群', '环', '域', '同态', '同构', '子群', '陪集',
            '理想', '向量空间', '线性变换', '特征值', 'Jordan',
            '拓扑', '开集', '闭集', '紧致', '连通', '同伦',
            '复变', '解析', '奇点', '留数', '级数',
            '泛函', 'Hilbert', 'Banach', '算子', '谱',
            '测度', '可测', '几乎处处'
        ],
        'system_prompt': '''你是一位资深的大学数学教授，专注于大学数学专业的证明题辅导。
你擅长：
- 数学分析：ε-δ语言、极限、连续、一致收敛
- 实变函数与测度论：Lebesgue积分、测度、可测函数
- 线性代数：线性空间、特征值与特征向量、Jordan标准形
- 抽象代数：群、环、域、同态、同构
- 拓扑学：开集、闭集、紧致性、连通性、同伦
- 复变函数：解析函数、留数定理、级数展开
- 泛函分析：Banach空间、Hilbert空间、算子理论

请提供严格、深入的数学证明指导，帮助学生理解证明的本质。
使用严格的数学符号和语言，适当解释关键概念和技巧。
对于复杂的证明，给出清晰的步骤分解。'''
    }
}


def detect_level(text: str) -> str:
    """根据文本内容自动检测学段"""
    if not text:
        return 'junior'
    
    text_lower = text.lower()
    scores = {}
    
    for level, config in LEVEL_CONFIG.items():
        score = 0
        for keyword in config['keywords']:
            if keyword.lower() in text_lower:
                score += 1
        scores[level] = score
    
    if max(scores.values()) == 0:
        return 'junior'
    
    return max(scores, key=scores.get)


def validate_base64_image(base64_str: str) -> bool:
    """验证 base64 图片格式"""
    if not base64_str:
        return False
    
    # 去除 data URI 前缀
    if 'base64,' in base64_str:
        base64_str = base64_str.split('base64,')[1]
    
    try:
        # 尝试解码
        img_data = base64.b64decode(base64_str[:100] + '==')
        
        # 检查图片头
        img_heads = [
            b'\xff\xd8\xff',  # JPEG
            b'\x89PNG',       # PNG
            b'GIF8',          # GIF
            b'RIFF',          # WEBP
        ]
        
        for head in img_heads:
            if img_data.startswith(head):
                return True
        
        return False
    except Exception:
        return False


def extract_base64_data(base64_str: str) -> str:
    """提取纯 base64 数据"""
    if 'base64,' in base64_str:
        return base64_str.split('base64,')[1]
    return base64_str


def process_image_for_api(base64_str: str) -> Image.Image:
    """处理 base64 图片用于 API"""
    clean_base64 = extract_base64_data(base64_str)
    img_bytes = base64.b64decode(clean_base64)
    return Image.open(BytesIO(img_bytes))


def chat_with_deepseek(messages: list, level: str = 'junior') -> str:
    """调用 DeepSeek API 进行对话"""
    if not client:
        if not init_deepseek_client():
            return "错误：DeepSeek API 未配置或初始化失败"
    
    try:
        config = LEVEL_CONFIG.get(level, LEVEL_CONFIG['junior'])
        
        # 构建完整的消息列表
        full_messages = [
            {"role": "system", "content": config['system_prompt']}
        ] + messages
        
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=full_messages,
            temperature=0.7,
            max_tokens=2000,
            stream=False
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"API 调用错误: {str(e)}"


def analyze_image_with_deepseek(base64_str: str, level: str = 'junior') -> dict:
    """使用 DeepSeek 视觉能力分析图片"""
    if not client:
        if not init_deepseek_client():
            return {
                "success": False,
                "error": "DeepSeek API 未配置"
            }
    
    try:
        config = LEVEL_CONFIG.get(level, LEVEL_CONFIG['junior'])
        
        # 构建视觉分析提示
        analysis_prompt = f'''请仔细分析这张数学证明题的图片。
学段：{config['name']}（{config['description']}）

请提供：
1. 题目内容（完整识别图片中的数学证明题）
2. 简要分析这道题的特点
3. 给出解题思路提示

如果图片不清晰或不是数学题，请说明。'''
        
        clean_base64 = extract_base64_data(base64_str)
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{clean_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": analysis_prompt
                        }
                    ]
                }
            ],
            max_tokens=1500
        )
        
        result = response.choices[0].message.content
        
        return {
            "success": True,
            "analysis": result,
            "level": config['name'],
            "detected_level": level
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"图片分析错误: {str(e)}"
        }


@app.route('/', methods=['GET'])
def index():
    """首页 - 返回HTML"""
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """提供静态文件"""
    return send_from_directory(FRONTEND_DIR, filename)


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    api_status = "configured" if client else "not_configured"
    
    return jsonify({
        "status": "healthy",
        "api_status": api_status,
        "timestamp": datetime.now().isoformat(),
        "service": "全学段数学证明导师系统",
        "version": "2.0.0"
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_proof():
    """
    分析证明题 API
    
    请求参数：
    - image: base64 编码的图片（可选）
    - level: 学段 (junior/senior/university)
    - text: 题目文本（可选）
    
    返回：
    - analysis: 题目分析
    - errors: 错误诊断
    - suggestions: 改进建议
    - steps: 解题步骤
    """
    try:
        data = request.get_json()
        
        image = data.get('image', '')
        level = data.get('level', 'auto')
        text = data.get('text', '')
        
        # 自动检测学段
        if level == 'auto':
            level = detect_level(text) if text else 'junior'
        
        # 验证学段
        if level not in LEVEL_CONFIG:
            level = 'junior'
        
        result = {
            "success": True,
            "level": level,
            "level_name": LEVEL_CONFIG[level]['name'],
            "timestamp": datetime.now().isoformat()
        }
        
        # 处理图片
        if image:
            if not validate_base64_image(image):
                return jsonify({
                    "success": False,
                    "error": "无效的图片格式"
                }), 400
            
            # 使用 DeepSeek 视觉能力分析图片
            image_result = analyze_image_with_deepseek(image, level)
            
            if image_result['success']:
                result['image_analysis'] = image_result['analysis']
                result['detected_level'] = image_result.get('detected_level', level)
            else:
                result['image_error'] = image_result.get('error', '图片分析失败')
        
        # 处理文本
        if text:
            # 构建分析提示
            analysis_messages = [
                {"role": "user", "content": f"""请分析这道数学证明题：

{text}

请提供：
1. 题目分析：这道题考察的知识点和解题方向
2. 常见错误：学生在这类题目中容易犯的错误
3. 解题思路：给出简要的解题思路提示
4. 关键步骤：指出证明的关键步骤

请用清晰、条理的方式回答。"""}
            ]
            
            analysis = chat_with_deepseek(analysis_messages, level)
            result['text_analysis'] = analysis
        
        # 如果没有提供任何内容
        if not image and not text:
            return jsonify({
                "success": False,
                "error": "请提供图片或题目文本"
            }), 400
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"分析失败: {str(e)}"
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    对话辅导 API
    
    请求参数：
    - message: 用户消息
    - history: 对话历史（可选）
    - level: 学段 (junior/senior/university)
    
    返回：
    - response: AI 回复
    - history: 更新后的对话历史
    """
    try:
        data = request.get_json()
        
        message = data.get('message', '')
        history = data.get('history', [])
        level = data.get('level', 'junior')
        
        if not message:
            return jsonify({
                "success": False,
                "error": "消息不能为空"
            }), 400
        
        # 验证学段
        if level not in LEVEL_CONFIG:
            level = 'junior'
        
        # 构建消息历史
        messages = []
        
        # 添加历史对话
        for item in history[-10:]:  # 只保留最近10条
            if isinstance(item, dict):
                messages.append({
                    "role": item.get("role", "user"),
                    "content": item.get("content", "")
                })
        
        # 添加当前消息
        messages.append({
            "role": "user",
            "content": message
        })
        
        # 调用 DeepSeek API
        response = chat_with_deepseek(messages, level)
        
        # 更新历史
        new_history = history[-9:] + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
        
        return jsonify({
            "success": True,
            "response": response,
            "history": new_history,
            "level": level,
            "level_name": LEVEL_CONFIG[level]['name']
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"对话失败: {str(e)}"
        }), 500


@app.route('/api/levels', methods=['GET'])
def get_levels():
    """获取支持的学段列表"""
    levels = []
    for key, config in LEVEL_CONFIG.items():
        levels.append({
            "id": key,
            "name": config['name'],
            "name_en": config['name_en'],
            "description": config['description']
        })
    
    return jsonify({
        "success": True,
        "levels": levels
    })


@app.route('/api/hint', methods=['POST'])
def get_hint():
    """
    获取解题提示 API
    
    请求参数：
    - text: 题目文本
    - level: 学段
    - step: 需要第几步提示
    """
    try:
        data = request.get_json()
        
        text = data.get('text', '')
        level = data.get('level', 'junior')
        step = data.get('step', 1)
        
        if not text:
            return jsonify({
                "success": False,
                "error": "题目文本不能为空"
            }), 400
        
        if level not in LEVEL_CONFIG:
            level = 'junior'
        
        # 根据步骤数提供不同程度的提示
        hint_prompts = {
            1: "给出这道题的第一步提示，帮助学生开始思考。",
            2: "给出这道题的关键提示，帮助学生找到解题方向。",
            3: "给出这道题的详细提示，基本指出解题思路。",
            4: "给出完整的解题思路和方法。",
            5: "给出完整的解题步骤。"
        }
        
        hint_level = min(step, 5)
        hint_request = hint_prompts.get(hint_level, hint_prompts[1])
        
        messages = [
            {"role": "user", "content": f"""题目：
{text}

请{hint_request}

注意：不要直接给出完整答案，通过提示引导学生自己思考。"""}
        ]
        
        response = chat_with_deepseek(messages, level)
        
        return jsonify({
            "success": True,
            "hint": response,
            "step": hint_level,
            "max_steps": 5
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取提示失败: {str(e)}"
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate_proof():
    """
    验证证明步骤 API
    
    请求参数：
    - problem: 原题目
    - proof: 学生的证明步骤
    - level: 学段
    """
    try:
        data = request.get_json()
        
        problem = data.get('problem', '')
        proof = data.get('proof', '')
        level = data.get('level', 'junior')
        
        if not problem or not proof:
            return jsonify({
                "success": False,
                "error": "题目和证明步骤都不能为空"
            }), 400
        
        if level not in LEVEL_CONFIG:
            level = 'junior'
        
        messages = [
            {"role": "user", "content": f"""请验证以下数学证明是否正确：

原题目：
{problem}

学生证明：
{problem}

请检查：
1. 证明的逻辑是否正确
2. 每一步是否有依据（公理、定理、已知条件）
3. 证明是否完整
4. 是否有逻辑错误或跳步

如果有问题，请指出具体错误并给出修改建议。
如果证明正确，请给予肯定并指出可改进的地方。"""}
        ]
        
        response = chat_with_deepseek(messages, level)
        
        return jsonify({
            "success": True,
            "validation": response
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"验证失败: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "API 端点不存在"
    }), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "error": "服务器内部错误"
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"启动全学段数学证明导师系统...")
    print(f"API 配置状态: {'已配置' if client else '未配置'}")
    print(f"监听端口: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
