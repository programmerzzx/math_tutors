# -*- coding: utf-8 -*-
"""
初中数学证明分析器
针对初中几何和代数证明题进行分析
"""

import json
import os
import re
from typing import Dict, List, Tuple


class JuniorAnalyzer:
    """初中数学证明分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.knowledge_base = self._load_knowledge_base()
        self.problem_library = self._load_problem_library()
        
        # 证明方法映射
        self.proof_methods = {
            '全等三角形证明': self._analyze_congruence,
            '平行线证明': self._analyze_parallel,
            '垂直证明': self._analyze_perpendicular,
            '角度证明': self._analyze_angle,
            '线段相等证明': self._analyze_segment_equal,
            '代数证明': self._analyze_algebraic
        }
        
        # 中考评分标准
        self.grading_criteria = {
            'key_step': 4,      # 关键步骤
            'reasoning': 2,     # 推理完整
            'conclusion': 2,    # 结论明确
            'writing': 2        # 书写规范
        }
    
    def analyze(self, content: str) -> Dict:
        """
        分析初中证明题
        
        Args:
            content: 题目内容
            
        Returns:
            分析结果字典
        """
        # 识别证明类型
        proof_type = self._identify_proof_type(content)
        
        # 调用相应的分析方法
        if proof_type in self.proof_methods:
            analysis = self.proof_methods[proof_type](content)
        else:
            analysis = self._general_analysis(content)
        
        # 获取相关知识
        knowledge = self._get_knowledge(proof_type)
        
        # 获取推荐练习
        recommendations = self._get_recommendations(proof_type)
        
        return {
            'proof_type': proof_type,
            'analysis': analysis,
            'knowledge': knowledge,
            'recommendations': recommendations,
            'grading_criteria': self.grading_criteria
        }
    
    def _identify_proof_type(self, content: str) -> str:
        """识别证明类型"""
        content_lower = content.lower()
        
        # 全等三角形
        if any(kw in content for kw in ['全等', '△', '对应', 'SSS', 'SAS', 'ASA', 'AAS', 'HL']):
            return '全等三角形证明'
        
        # 平行线
        if any(kw in content for kw in ['平行', '平行线', '同位角', '内错角', '同旁内角']):
            return '平行线证明'
        
        # 垂直
        if any(kw in content for kw in ['垂直', '直角', '垂线', '垂足']):
            return '垂直证明'
        
        # 角度
        if any(kw in content for kw in ['角', '角度', '相等', '余角', '补角']):
            return '角度证明'
        
        # 线段
        if any(kw in content for kw in ['线段', '中点', '线段相等', '延长']):
            return '线段相等证明'
        
        # 默认代数
        return '代数证明'
    
    def _analyze_congruence(self, content: str) -> Dict:
        """分析全等三角形证明"""
        analysis = {
            'theorem_used': [],
            'missing_parts': [],
            'steps': [],
            'hints': []
        }
        
        # 检查使用的判定定理
        if 'SSS' in content or '三边' in content:
            analysis['theorem_used'].append('边边边(SSS)')
        if 'SAS' in content or '两边夹角' in content:
            analysis['theorem_used'].append('边角边(SAS)')
        if 'ASA' in content or '两角夹边' in content:
            analysis['theorem_used'].append('角边角(ASA)')
        if 'AAS' in content or '两角一边' in content:
            analysis['theorem_used'].append('角角边(AAS)')
        if 'HL' in content or '直角' in content:
            analysis['theorem_used'].append('斜边直角边(HL)')
        
        # 常见遗漏点
        if '对应' not in content:
            analysis['missing_parts'].append('未说明对应顶点或对应边')
        if '公共边' not in content and '公共' not in content:
            analysis['hints'].append('注意寻找图形中的公共边或公共角')
        
        # 分析证明步骤
        analysis['steps'] = [
            '1. 找出两个需要证明全等的三角形',
            '2. 分析已知条件，找出相等的边和角',
            '3. 根据条件选择合适的判定定理',
            '4. 规范书写证明过程'
        ]
        
        return analysis
    
    def _analyze_parallel(self, content: str) -> Dict:
        """分析平行线证明"""
        analysis = {
            'theorem_used': [],
            'missing_parts': [],
            'steps': []
        }
        
        # 平行线判定定理
        if '同位角' in content and ('相等' in content or '相等' in content):
            analysis['theorem_used'].append('同位角相等，两直线平行')
        if '内错角' in content and '相等' in content:
            analysis['theorem_used'].append('内错角相等，两直线平行')
        if '同旁内角' in content and ('互补' in content or '180' in content):
            analysis['theorem_used'].append('同旁内角互补，两直线平行')
        
        analysis['steps'] = [
            '1. 找出需要证明平行的两条直线',
            '2. 找出这两条直线被哪条直线所截',
            '3. 计算或证明相应的同位角、内错角或同旁内角',
            '4. 根据平行线判定定理得出结论'
        ]
        
        return analysis
    
    def _analyze_perpendicular(self, content: str) -> Dict:
        """分析垂直证明"""
        analysis = {
            'theorem_used': [],
            'steps': []
        }
        
        # 垂直判定方法
        if '90°' in content or '直角' in content:
            analysis['theorem_used'].append('直角等于90°')
        if '邻补角' in content and '相等' in content:
            analysis['theorem_used'].append('邻补角相等，则各为90°')
        if '等腰' in content and '三线合一' in content:
            analysis['theorem_used'].append('等腰三角形三线合一')
        
        analysis['steps'] = [
            '1. 构造或找出90°的角',
            '2. 利用垂直定义或相关定理证明',
            '3. 注意格式：∵... ∴... ∴... ⊥ ...'
        ]
        
        return analysis
    
    def _analyze_angle(self, content: str) -> Dict:
        """分析角度证明"""
        analysis = {
            'theorem_used': [],
            'missing_parts': [],
            'steps': []
        }
        
        if '对顶角' in content:
            analysis['theorem_used'].append('对顶角相等')
        if '余角' in content:
            analysis['theorem_used'].append('同角的余角相等')
        if '补角' in content:
            analysis['theorem_used'].append('同角的补角相等')
        if '三角形内角和' in content or '内角和' in content:
            analysis['theorem_used'].append('三角形内角和为180°')
        
        analysis['steps'] = [
            '1. 分析图中各角之间的关系',
            '2. 利用角度计算或已知相等关系',
            '3. 注意格式规范书写'
        ]
        
        return analysis
    
    def _analyze_segment_equal(self, content: str) -> Dict:
        """分析线段相等证明"""
        analysis = {
            'methods': [],
            'steps': []
        }
        
        analysis['methods'] = [
            '全等三角形对应边相等',
            '等腰三角形两腰相等',
            '线段垂直平分线性质',
            '角平分线性质',
            '圆中半径相等'
        ]
        
        analysis['steps'] = [
            '1. 判断需要证明相等的线段所在三角形',
            '2. 尝试证明三角形全等',
            '3. 或利用其他线段相等定理'
        ]
        
        return analysis
    
    def _analyze_algebraic(self, content: str) -> Dict:
        """分析代数证明"""
        analysis = {
            'techniques': [],
            'steps': []
        }
        
        if '因式分解' in content:
            analysis['techniques'].append('因式分解')
        if '配方法' in content:
            analysis['techniques'].append('配方法')
        if '换元' in content:
            analysis['techniques'].append('换元法')
        if '分类讨论' in content:
            analysis['techniques'].append('分类讨论')
        
        analysis['steps'] = [
            '1. 理解题意，明确要证明的结论',
            '2. 分析已知条件与结论的关系',
            '3. 选择合适的证明方法',
            '4. 规范书写证明过程'
        ]
        
        return analysis
    
    def _general_analysis(self, content: str) -> Dict:
        """通用分析"""
        return {
            'type': '综合证明',
            'difficulty': '中等',
            'suggestion': '请根据题目具体内容进行分析'
        }
    
    def _get_knowledge(self, proof_type: str) -> Dict:
        """获取相关知识"""
        knowledge_map = {
            '全等三角形证明': '初中/平面几何.md',
            '平行线证明': '初中/平面几何.md',
            '垂直证明': '初中/平面几何.md',
            '角度证明': '初中/平面几何.md',
            '线段相等证明': '初中/平面几何.md',
            '代数证明': '初中/代数证明.md'
        }
        
        return {
            'file': knowledge_map.get(proof_type, '初中/平面几何.md'),
            'tips': self._get_tips(proof_type)
        }
    
    def _get_tips(self, proof_type: str) -> List[str]:
        """获取解题提示"""
        tips_map = {
            '全等三角形证明': [
                '注意寻找公共边和公共角',
                '对应顶点的顺序要一致',
                '严格按SSS、SAS、ASA、AAS、HL的顺序写条件'
            ],
            '平行线证明': [
                '找准截线和被截线',
                '注意内错角和同位角的识别',
                '同旁内角需要相加等于180°'
            ],
            '垂直证明': [
                '利用直角三角形的性质',
                '注意三线合一的应用',
                '利用补角或余角的关系'
            ],
            '角度证明': [
                '灵活运用内角和定理',
                '注意外角定理的应用',
                '利用平行线的角性质'
            ],
            '线段相等证明': [
                '优先考虑全等三角形',
                '注意等腰三角形的性质',
                '利用中点相关性质'
            ],
            '代数证明': [
                '注意因式分解的技巧',
                '配方法要完整',
                '分类讨论要不重不漏'
            ]
        }
        
        return tips_map.get(proof_type, ['仔细审题，规范书写'])
    
    def _get_recommendations(self, proof_type: str) -> List[Dict]:
        """获取推荐练习"""
        # 从题库中获取相关题目
        problems = self.problem_library.get(proof_type, [])
        return problems[:3] if problems else []
    
    def _load_knowledge_base(self) -> Dict:
        """加载知识库"""
        knowledge = {}
        kb_path = 'knowledge_base/初中'
        
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
        kb_path = 'knowledge_base/初中/题库'
        
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
        """
        检查证明是否正确
        
        Args:
            proof: 学生提交的证明
            standard_answer: 标准答案
            
        Returns:
            检查结果
        """
        # 提取关键步骤
        key_steps = self._extract_key_steps(proof)
        standard_steps = self._extract_key_steps(standard_answer)
        
        # 计算得分
        total_score = 10
        score = 0
        missing_steps = []
        
        for step in standard_steps:
            if step in key_steps:
                score += total_score / len(standard_steps)
            else:
                missing_steps.append(step)
        
        # 检查格式
        format_score = 0
        if '∵' in proof and '∴' in proof:
            format_score = 2
        if '证明' in proof:
            format_score += 1
        
        return {
            'total_score': round(score + format_score, 1),
            'key_steps_found': len(key_steps),
            'missing_steps': missing_steps,
            'format_correct': format_score > 0
        }
    
    def _extract_key_steps(self, text: str) -> List[str]:
        """提取关键步骤"""
        # 提取包含关键定理的语句
        patterns = [
            r'[△]\w+\s*≅\s*[△]\w+',  # 全等
            r'∥',  # 平行
            r'⊥',  # 垂直
            r'∠\w+\s*=\s*∠\w+',  # 角相等
            r'=\s*\w+\w+',  # 边相等
        ]
        
        steps = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            steps.extend(matches)
        
        return steps
