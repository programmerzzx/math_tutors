# -*- coding: utf-8 -*-
"""
高中数学证明分析器
针对高中各类证明题进行分析
"""

import json
import os
import re
from typing import Dict, List, Tuple


class SeniorAnalyzer:
    """高中数学证明分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.knowledge_base = self._load_knowledge_base()
        self.problem_library = self._load_problem_library()
        
        # 题型分类
        self.problem_types = {
            '代数与恒等式': self._analyze_algebra,
            '不等式证明': self._analyze_inequality,
            '平面几何': self._analyze_plane_geometry,
            '立体几何': self._analyze_solid_geometry,
            '解析几何': self._analyze_analytic_geometry,
            '数列与归纳法': self._analyze_sequence,
            '三角函数': self._analyze_trigonometry,
            '函数性质': self._analyze_function,
            '向量与复数': self._analyze_vector_complex,
            '概率统计': self._analyze_probability
        }
        
        # 高考评分标准
        self.grading_criteria = {
            'correctness': 6,     # 正确性
            'completeness': 2,   # 完整性
            'logic': 1.5,         # 逻辑性
            'writing': 0.5       # 书写规范
        }
        
        # 常见失分点
        self.common_mistakes = {
            '数列': ['未验证首项', '归纳假设未使用', '项数错误'],
            '不等式': ['放缩过度', '等号成立条件未说明', '逆向推导'],
            '立体几何': ['未说明线面关系', '法向量计算错误', '遗漏垂直条件'],
            '解析几何': ['未讨论特殊情况', '计算错误', '未验证点在曲线上'],
            '函数': ['定义域遗漏', '端点值未单独考虑', '求导错误']
        }
    
    def analyze(self, content: str) -> Dict:
        """
        分析高中证明题
        
        Args:
            content: 题目内容
            
        Returns:
            分析结果字典
        """
        # 识别题型
        problem_type = self._identify_problem_type(content)
        
        # 调用相应分析方法
        if problem_type in self.problem_types:
            analysis = self.problem_types[problem_type](content)
        else:
            analysis = self._general_analysis(content)
        
        # 获取失分点分析
        mistake_analysis = self._get_mistake_analysis(problem_type)
        
        # 获取相关知识
        knowledge = self._get_knowledge(problem_type)
        
        # 获取推荐练习
        recommendations = self._get_recommendations(problem_type)
        
        return {
            'problem_type': problem_type,
            'analysis': analysis,
            'mistake_analysis': mistake_analysis,
            'knowledge': knowledge,
            'recommendations': recommendations,
            'grading_criteria': self.grading_criteria
        }
    
    def _identify_problem_type(self, content: str) -> str:
        """识别题型"""
        # 数列与数学归纳法
        if any(kw in content for kw in ['数列', '归纳', '数学归纳法', '递推', 'an+1', 'Sn']):
            return '数列与归纳法'
        
        # 不等式
        if any(kw in content for kw in ['不等式', '>', '<', '≥', '≤', '放缩', '均值', '柯西']):
            return '不等式证明'
        
        # 立体几何
        if any(kw in content for kw in ['立体', '空间', '面', '二面角', '线面', '体积', '空间向量']):
            return '立体几何'
        
        # 解析几何
        if any(kw in content for kw in ['椭圆', '双曲线', '抛物线', '圆锥曲线', '焦点', '离心率', '准线']):
            return '解析几何'
        
        # 三角函数
        if any(kw in content for kw in ['正弦', '余弦', '正切', '三角函数', '和差化积', '积化和差', '辅助角']):
            return '三角函数'
        
        # 函数性质
        if any(kw in content for kw in ['函数', '导数', '单调性', '极值', '最值', '凹凸性', 'f(x)']):
            return '函数性质'
        
        # 向量与复数
        if any(kw in content for kw in ['向量', '复数', '模', '共轭', '幅角', '|z|']):
            return '向量与复数'
        
        # 概率统计
        if any(kw in content for kw in ['概率', '期望', '方差', '分布', '二项分布', '正态分布']):
            return '概率统计'
        
        # 平面几何
        if any(kw in content for kw in ['平面几何', '圆', '切线', '割线', '相交弦']):
            return '平面几何'
        
        # 默认代数
        return '代数与恒等式'
    
    def _analyze_sequence(self, content: str) -> Dict:
        """分析数列证明"""
        analysis = {
            'method': '',
            'key_steps': [],
            'common_errors': []
        }
        
        # 判断使用的证明方法
        if '数学归纳法' in content or '归纳' in content:
            analysis['method'] = '数学归纳法'
            analysis['key_steps'] = [
                '1. 验证n=1时命题成立',
                '2. 假设n=k时命题成立',
                '3. 利用假设证明n=k+1时命题成立',
                '4. 综上，命题对所有正整数n成立'
            ]
            analysis['common_errors'] = [
                '归纳假设写错',
                '从n=k到n=k+1的过渡不严谨',
                '未写"综上"'
            ]
        elif '等比' in content or '等差' in content:
            analysis['method'] = '数列通项公式'
            analysis['key_steps'] = [
                '1. 判断是等差还是等比数列',
                '2. 求出首项和公差/公比',
                '3. 写出通项公式',
                '4. 验证'
            ]
        elif 'Sn' in content:
            analysis['method'] = '数列求和'
            analysis['key_steps'] = [
                '1. 分析通项公式特点',
                '2. 选择合适的求和方法（错位相减、裂项、分组等）',
                '3. 规范计算'
            ]
        
        return analysis
    
    def _analyze_inequality(self, content: str) -> Dict:
        """分析不等式证明"""
        analysis = {
            'method': '',
            'techniques': [],
            'key_steps': []
        }
        
        # 判断证明方法
        if '数学归纳法' in content:
            analysis['method'] = '数学归纳法'
        elif '放缩' in content:
            analysis['method'] = '放缩法'
        elif '均值' in content or '基本不等式' in content:
            analysis['method'] = '均值不等式'
        elif '柯西' in content or 'Cauchy' in content:
            analysis['method'] = '柯西不等式'
        elif ' Jensen' in content:
            analysis['method'] = 'Jensen不等式'
        else:
            analysis['method'] = '常规证明'
        
        analysis['techniques'] = [
            '分析法：从结论出发逆向思考',
            '综合法：从条件出发正向推导',
            '放缩法：有意识地将式子放大或缩小',
            '换元法：简化复杂表达式',
            '构造法：构造辅助函数或不等式'
        ]
        
        analysis['key_steps'] = [
            '1. 分析已知条件和结论',
            '2. 选择合适的证明方法',
            '3. 注意等号成立条件',
            '4. 检验边界情况'
        ]
        
        return analysis
    
    def _analyze_solid_geometry(self, content: str) -> Dict:
        """分析立体几何"""
        analysis = {
            'method': '',
            'approaches': [],
            'key_steps': []
        }
        
        if '空间向量' in content or '法向量' in content:
            analysis['method'] = '空间向量法'
            analysis['approaches'] = ['建系', '求法向量', '计算']
            analysis['key_steps'] = [
                '1. 建立适当的空间直角坐标系',
                '2. 写出各点坐标',
                '3. 求平面的法向量',
                '4. 利用向量运算求解'
            ]
        else:
            analysis['method'] = '传统几何法'
            analysis['key_steps'] = [
                '1. 分析线面关系',
                '2. 找出关键平面',
                '3. 利用面面、线面垂直/平行的判定定理',
                '4. 规范书写证明过程'
            ]
        
        return analysis
    
    def _analyze_analytic_geometry(self, content: str) -> Dict:
        """分析解析几何"""
        analysis = {
            'curve_type': '',
            'method': '',
            'key_steps': []
        }
        
        # 判断曲线类型
        if '椭圆' in content:
            analysis['curve_type'] = '椭圆'
        elif '双曲线' in content:
            analysis['curve_type'] = '双曲线'
        elif '抛物线' in content:
            analysis['curve_type'] = '抛物线'
        
        analysis['method'] = '坐标法'
        analysis['key_steps'] = [
            '1. 设点坐标或直线方程',
            '2. 利用曲线方程建立关系',
            '3. 联立方程组',
            '4. 韦达定理及后续处理',
            '5. 注意判别式和参数范围'
        ]
        
        return analysis
    
    def _analyze_trigonometry(self, content: str) -> Dict:
        """分析三角函数证明"""
        analysis = {
            'techniques': [],
            'key_steps': []
        }
        
        analysis['techniques'] = [
            '同角三角函数关系',
            '诱导公式',
            '和差角公式',
            '二倍角公式',
            '辅助角公式 asinθ + bcosθ = √(a²+b²)sin(θ+φ)'
        ]
        
        analysis['key_steps'] = [
            '1. 从角的关系入手，分析各角之间的联系',
            '2. 优先考虑化简，执果索因',
            '3. 注意角的范围对等号成立的影响',
            '4. 常用技巧：1的代换、弦切互化'
        ]
        
        return analysis
    
    def _analyze_function(self, content: str) -> Dict:
        """分析函数性质证明"""
        analysis = {
            'property': '',
            'key_steps': []
        }
        
        if '单调性' in content or '递增' in content or '递减' in content:
            analysis['property'] = '单调性'
            analysis['key_steps'] = [
                '1. 求导数',
                '2. 判断导数符号',
                '3. 得出单调性结论'
            ]
        elif '极值' in content or '最值' in content:
            analysis['property'] = '极值/最值'
            analysis['key_steps'] = [
                '1. 求导',
                '2. 求极值点（导数为零的点）',
                '3. 判断极值类型',
                '4. 求最值（比较端点和极值）'
            ]
        elif '凹凸性' in content:
            analysis['property'] = '凹凸性'
            analysis['key_steps'] = [
                '1. 求二阶导数',
                '2. 判断二阶导数符号',
                '3. 得出凹凸性结论'
            ]
        
        return analysis
    
    def _analyze_vector_complex(self, content: str) -> Dict:
        """分析向量与复数"""
        analysis = {
            'topic': '',
            'key_steps': []
        }
        
        if '向量' in content:
            analysis['topic'] = '向量'
            analysis['key_steps'] = [
                '1. 建立坐标系或选择基底',
                '2. 用坐标或基底表示向量',
                '3. 利用向量运算律',
                '4. 转化为代数问题'
            ]
        elif '复数' in content:
            analysis['topic'] = '复数'
            analysis['key_steps'] = [
                '1. 将复数化为a+bi形式',
                '2. 利用复数运算律',
                '3. 注意模和共轭的性质',
                '4. 必要时使用几何意义'
            ]
        
        return analysis
    
    def _analyze_probability(self, content: str) -> Dict:
        """分析概率统计"""
        analysis = {
            'key_steps': []
        }
        
        analysis['key_steps'] = [
            '1. 明确随机变量及其取值',
            '2. 确定概率分布类型',
            '3. 计算概率',
            '4. 求期望和方差'
        ]
        
        return analysis
    
    def _analyze_plane_geometry(self, content: str) -> Dict:
        """分析平面几何"""
        analysis = {
            'key_steps': []
        }
        
        analysis['key_steps'] = [
            '1. 分析图形结构',
            '2. 找出关键三角形或四边形',
            '3. 利用平面几何定理',
            '4. 计算或证明'
        ]
        
        return analysis
    
    def _analyze_algebra(self, content: str) -> Dict:
        """分析代数证明"""
        analysis = {
            'key_steps': []
        }
        
        analysis['key_steps'] = [
            '1. 分析条件与结论的关系',
            '2. 选择合适的变形技巧',
            '3. 注意运算律和公式的应用',
            '4. 规范书写'
        ]
        
        return analysis
    
    def _general_analysis(self, content: str) -> Dict:
        """通用分析"""
        return {
            'type': '综合证明',
            'difficulty': '中等',
            'suggestion': '请根据题目具体内容进行分析'
        }
    
    def _get_mistake_analysis(self, problem_type: str) -> List[str]:
        """获取常见失分点"""
        return self.common_mistakes.get(problem_type, [
            '审题不仔细',
            '计算错误',
            '步骤不完整',
            '格式不规范'
        ])
    
    def _get_knowledge(self, problem_type: str) -> Dict:
        """获取相关知识"""
        knowledge_map = {
            '数列与归纳法': '高中/数列与归纳法.md',
            '不等式证明': '高中/不等式证明.md',
            '立体几何': '高中/立体几何.md',
            '解析几何': '高中/解析几何.md',
            '三角函数': '高中/三角函数.md',
            '函数性质': '高中/函数性质.md',
            '向量与复数': '高中/向量与复数.md',
            '概率统计': '高中/概率统计.md',
            '平面几何': '高中/平面几何.md',
            '代数与恒等式': '高中/代数与恒等式.md'
        }
        
        return {
            'file': knowledge_map.get(problem_type, '高中/代数与恒等式.md'),
            'tips': self._get_tips(problem_type)
        }
    
    def _get_tips(self, problem_type: str) -> List[str]:
        """获取解题提示"""
        tips_map = {
            '数列与归纳法': [
                '数学归纳法两步缺一不可',
                '归纳假设必须原封不动地使用',
                '有时需要强化命题才能完成证明'
            ],
            '不等式证明': [
                '注意放缩的度，既要能证明又要可实现',
                '多次使用不等式时要注意等号同时成立',
                '逆推法可以帮助找到证明思路'
            ],
            '立体几何': [
                '线面垂直的判定：线垂直于面内两相交直线',
                '面面垂直的判定：一面内一线垂直于另一面',
                '空间向量：建系要使点的坐标尽可能简洁'
            ],
            '解析几何': [
                '设直线方程时考虑斜率不存在的情形',
                '设点还是设线要视具体情况而定',
                '韦达定理是解析几何的核心工具'
            ],
            '三角函数': [
                '注意角的范围，有时需要先求范围再证明',
                '辅助角公式是处理asinθ+bcosθ的利器',
                '1的代换：sin²x+cos²x=1'
            ],
            '函数性质': [
                '求导后注意定义域',
                '极值点不一定是最值点',
                '端点值需要单独考虑'
            ],
            '向量与复数': [
                '向量数量积公式：a·b=|a||b|cosθ',
                '复数模的性质：|z1z2|=|z1||z2|',
                '注意复数运算的几何意义'
            ]
        }
        
        return tips_map.get(problem_type, ['仔细审题，规范解答'])
    
    def _get_recommendations(self, problem_type: str) -> List[Dict]:
        """获取推荐练习"""
        problems = self.problem_library.get(problem_type, [])
        return problems[:3] if problems else []
    
    def _load_knowledge_base(self) -> Dict:
        """加载知识库"""
        knowledge = {}
        kb_path = 'knowledge_base/高中'
        
        if os.path.exists(kb_path):
            for filename in os.listdir(kb_path):
                if filename.endswith('.md'):
                    filepath = os.path.join(kb_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            knowledge[filename[:-3]] = f.read()
                    except:
                        pass
        
        return knowledge
    
    def _load_problem_library(self) -> Dict:
        """加载题库"""
        problems = {}
        kb_path = 'knowledge_base/高中/题库'
        
        if os.path.exists(kb_path):
            for filename in os.listdir(kb_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(kb_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            problem_type = filename.replace('题库.json', '')
                            problems[problem_type] = json.load(f)
                    except:
                        pass
        
        return problems
    
    def check_proof(self, proof: str, standard_answer: str) -> Dict:
        """检查证明是否正确"""
        # 简化检查逻辑
        key_points = self._extract_key_points(proof)
        required_points = self._extract_key_points(standard_answer)
        
        found = sum(1 for p in required_points if p in key_points)
        score = (found / len(required_points)) * 100 if required_points else 0
        
        return {
            'score': round(score, 1),
            'key_points_found': found,
            'total_required': len(required_points)
        }
    
    def _extract_key_points(self, text: str) -> List[str]:
        """提取关键点"""
        # 提取关键数学表达式和定理
        patterns = [
            r'数学归纳法',
            r'等差|等比',
            r'Sn',
            r'an',
            r'f\'\(x\)',
            r'导数',
            r'法向量',
            r'椭圆|双曲线|抛物线',
            r'均值|柯西',
            r'向量',
            r'复数'
        ]
        
        points = []
        for pattern in patterns:
            if re.search(pattern, text):
                points.append(pattern)
        
        return points
