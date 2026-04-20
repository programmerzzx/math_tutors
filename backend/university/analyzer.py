# -*- coding: utf-8 -*-
"""
大学数学证明分析器
针对大学数学各类证明题进行分析，包括严格的数学证明方法
"""

import json
import os
import re
from typing import Dict, List, Tuple, Set


class UniversityAnalyzer:
    """大学数学证明分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self.knowledge_base = self._load_knowledge_base()
        self.problem_library = self._load_problem_library()
        
        # 课程分类
        self.course_types = {
            '数学分析': self._analyze_analysis,
            '高等代数': self._analyze_linear_algebra,
            '解析几何': self._analyze_analytic_geometry,
            '概率论': self._analyze_probability,
            '常微分方程': self._analyze_ode,
            '抽象代数': self._analyze_abstract_algebra,
            '实变函数': self._analyze_real_analysis,
            '复变函数': self._analyze_complex_analysis,
            '泛函分析': self._analyze_functional_analysis,
            '拓扑学': self._analyze_topology,
            '微分几何': self._analyze_differential_geometry,
            '数论': self._analyze_number_theory,
            '组合数学': self._analyze_combinatorics,
            '数理逻辑': self._analyze_math_logic
        }
        
        # 证明严谨性标准
        self.rigor_criteria = {
            'epsilon_delta': 'ε-δ语言使用正确',
            'quantifiers': '量词使用正确（∀, ∃）',
            'definitions': '定义引用准确',
            'theorems': '定理应用正确',
            'logic': '逻辑推导严谨',
            'notation': '符号使用规范'
        }
        
        # 常见错误类型
        self.common_errors = {
            'epsilon_delta': [
                'δ的选择过于复杂或不合理',
                'ε和δ的关系处理错误',
                '从右向左推导时逻辑混乱'
            ],
            'induction': [
                '归纳假设使用不当',
                '从k到k+1的过渡不严格',
                '未验证基础情形'
            ],
            'algebra': [
                '同态/同构概念混淆',
                '群/环/域性质使用错误',
                '正合列推导不严谨'
            ],
            'analysis': [
                '极限交换不说明条件',
                '积分交换不验证条件',
                '连续性/一致连续性混淆'
            ]
        }
    
    def analyze(self, content: str) -> Dict:
        """
        分析大学证明题
        
        Args:
            content: 题目内容
            
        Returns:
            分析结果字典
        """
        # 识别课程类型
        course_type = self._identify_course_type(content)
        
        # 调用相应分析方法
        if course_type in self.course_types:
            analysis = self.course_types[course_type](content)
        else:
            analysis = self._general_analysis(content)
        
        # 分析使用的证明方法
        proof_methods = self._identify_proof_methods(content)
        
        # 获取相关知识
        knowledge = self._get_knowledge(course_type)
        
        # 获取推荐练习
        recommendations = self._get_recommendations(course_type)
        
        return {
            'course_type': course_type,
            'proof_methods': proof_methods,
            'analysis': analysis,
            'knowledge': knowledge,
            'recommendations': recommendations,
            'rigor_criteria': self.rigor_criteria
        }
    
    def _identify_course_type(self, content: str) -> str:
        """识别课程类型"""
        # 数学分析
        if any(kw in content for kw in ['ε-δ', '极限', '连续', '可导', '可积', 
                                          '一致收敛', 'Riemann', 'Lebesgue', 
                                          '微分中值定理', 'Taylor展开', '积分']):
            return '数学分析'
        
        # 抽象代数
        if any(kw in content for kw in ['群', '环', '域', '同态', '同构', '子群',
                                         '陪集', '商群', '理想', 'Abel群', '循环群',
                                         '正规子群', '单群', 'Sylow定理']):
            return '抽象代数'
        
        # 拓扑学
        if any(kw in content for kw in ['拓扑', '开集', '闭集', '紧致', '连通',
                                         '同伦', '同胚', '流形', '邻域', '内部',
                                         '闭包', '边界', '分离性']):
            return '拓扑学'
        
        # 复变函数
        if any(kw in content for kw in ['复变', '解析', '全纯', '奇点', '留数',
                                         'Laurent级数', 'Cauchy积分公式', '幅角原理']):
            return '复变函数'
        
        # 泛函分析
        if any(kw in content for kw in ['Hilbert空间', 'Banach空间', '算子', '谱',
                                         '有界线性算子', '对偶空间', '共轭算子']):
            return '泛函分析'
        
        # 实变函数
        if any(kw in content for kw in ['Lebesgue积分', '测度', '可测函数', '几乎处处',
                                         'L^p空间', 'Borel集', 'Carathéodory']):
            return '实变函数'
        
        # 高等代数
        if any(kw in content for kw in ['矩阵', '行列式', '特征值', '特征向量', 
                                         '线性空间', '线性变换', 'Jordan标准形',
                                         '相似矩阵', '合同矩阵', '正定矩阵']):
            return '高等代数'
        
        # 常微分方程
        if any(kw in content for kw in ['微分方程', 'ODE', 'PDE', '常微分', '解的存在性',
                                         '解的的唯一性', '稳定性', '相平面', '奇点']):
            return '常微分方程'
        
        # 概率论
        if any(kw in content for kw in ['概率', '随机变量', '期望', '方差', '分布函数',
                                         '大数定律', '中心极限定理', '条件期望']):
            return '概率论'
        
        # 数论
        if any(kw in content for kw in ['数论', '质数', '素数', '同余', '欧拉函数',
                                        '费马小定理', '原根', '二次剩余', '数论函数']):
            return '数论'
        
        # 微分几何
        if any(kw in content for kw in ['微分几何', '曲线', '曲面', '曲率', '挠率',
                                         '第一基本形式', '第二基本形式', 'Gauss曲率']):
            return '微分几何'
        
        # 组合数学
        if any(kw in content for kw in ['组合', '排列', '组合数', '生成函数', '容斥原理',
                                         '递推关系', 'Catalan数', 'Ramsey理论']):
            return '组合数学'
        
        # 数理逻辑
        if any(kw in content for kw in ['数理逻辑', '命题', '谓词', '公理系统', '一致性',
                                         '完全性', '哥德尔', '形式系统', '模型论']):
            return '数理逻辑'
        
        # 解析几何
        if any(kw in content for kw in ['解析几何', '向量', '平面', '直线', '二次曲线',
                                         '坐标变换', '仿射变换', '射影几何']):
            return '解析几何'
        
        return '数学分析'  # 默认
    
    def _identify_proof_methods(self, content: str) -> List[str]:
        """识别证明方法"""
        methods = []
        
        if 'ε-δ' in content or 'epsilon' in content.lower():
            methods.append('ε-δ语言')
        if '归纳' in content or 'induction' in content.lower():
            methods.append('数学归纳法')
        if '反证' in content or '假设' in content and '矛盾' in content:
            methods.append('反证法')
        if '构造' in content:
            methods.append('构造性证明')
        if '存在' in content or '∃' in content:
            methods.append('存在性证明')
        if '∀' in content or '任意' in content:
            methods.append('全称量词证明')
        if '同构' in content or '映射' in content:
            methods.append('同构映射法')
        if '不动点' in content:
            methods.append('不动点定理')
        if '迭代' in content or '收敛' in content:
            methods.append('迭代法')
        
        return methods if methods else ['直接证明']
    
    def _analyze_analysis(self, content: str) -> Dict:
        """分析数学分析"""
        analysis = {
            'topic': '',
            'epsilon_delta_required': False,
            'key_steps': [],
            'common_pitfalls': []
        }
        
        if '极限' in content:
            analysis['topic'] = '极限'
            analysis['epsilon_delta_required'] = True
            analysis['key_steps'] = [
                '1. 明确要证明的目标：∀ε>0, ∃N(δ), 使得...',
                '2. 从目标不等式出发，分析需要什么条件',
                '3. 反向构造证明：先取δ = f(ε)',
                '4. 正向书写：从∀ε>0，取δ=...，则当...时，有...'
            ]
            analysis['common_pitfalls'] = [
                'δ的选取要明确依赖于ε',
                '绝对值不等式放缩要恰当',
                '下标对应关系要清晰'
            ]
        elif '连续' in content:
            analysis['topic'] = '连续性'
            if '一致连续' in content:
                analysis['epsilon_delta_required'] = True
                analysis['key_steps'] = [
                    '1. 区分点连续与一致连续',
                    '2. 否定形式：∃ε₀>0, ∀δ>0, ∃x₁,x₂∈(a,b), 使得|x₁-x₂|<δ但|f(x₁)-f(x₂)|≥ε₀'
                ]
        elif '可导' in content or '导数' in content:
            analysis['topic'] = '导数与微分'
            analysis['key_steps'] = [
                '1. 用定义：f\'(x₀)=lim_{h→0}[f(x₀+h)-f(x₀)]/h',
                '2. 利用导数运算法则',
                '3. 复合函数求导法则'
            ]
        elif '积分' in content:
            analysis['topic'] = '积分'
            analysis['key_steps'] = [
                '1. 明确是Riemann积分还是Lebesgue积分',
                '2. 检查可积条件',
                '3. 利用积分性质（线性性、单调性）',
                '4. 积分中值定理的应用'
            ]
        
        return analysis
    
    def _analyze_abstract_algebra(self, content: str) -> Dict:
        """分析抽象代数"""
        analysis = {
            'structure': '',
            'key_steps': [],
            'properties_to_check': []
        }
        
        if '群' in content:
            analysis['structure'] = '群'
            analysis['properties_to_check'] = [
                '闭合性：∀a,b∈G, a∘b∈G',
                '结合律：∀a,b,c∈G, (a∘b)∘c=a∘(b∘c)',
                '单位元：∃e∈G, 使得e∘a=a∘e=a',
                '逆元：∀a∈G, ∃a⁻¹∈G, 使得a∘a⁻¹=a⁻¹∘a=e'
            ]
            analysis['key_steps'] = [
                '1. 首先验证代数结构',
                '2. 判断是哪种特殊群（循环群、Abel群等）',
                '3. 利用同态基本定理或第一同构定理',
                '4. 必要时构造具体的群或商群'
            ]
        elif '环' in content:
            analysis['structure'] = '环'
            analysis['properties_to_check'] = [
                '加法群：交换群',
                '乘法半群：结合律',
                '分配律：a(b+c)=ab+ac, (a+b)c=ac+bc'
            ]
        elif '域' in content:
            analysis['structure'] = '域'
            analysis['properties_to_check'] = [
                '非零元素构成Abel群',
                '零元对乘法的吸收性',
                '域是整环'
            ]
        
        return analysis
    
    def _analyze_topology(self, content: str) -> Dict:
        """分析拓扑学"""
        analysis = {
            'property': '',
            'key_steps': []
        }
        
        if '紧致' in content or '紧' in content:
            analysis['property'] = '紧致性'
            analysis['key_steps'] = [
                '1. Heine-Borel：Rⁿ中集合紧⇔有界闭',
                '2. 紧致的等价刻画：任意开覆盖有有限子覆盖',
                '3. 紧空间的连续像是紧的',
                '4. 紧空间中的连续函数有最大最小值'
            ]
        elif '连通' in content:
            analysis['property'] = '连通性'
            analysis['key_steps'] = [
                '1. 连通：不能表示为两个非空不相交开集之并',
                '2. 道路连通⇒连通',
                '3. R中区间连通',
                '4. 连续映射保持连通性'
            ]
        elif '同伦' in content or '同伦等价' in content:
            analysis['property'] = '同伦'
        
        return analysis
    
    def _analyze_complex_analysis(self, content: str) -> Dict:
        """分析复变函数"""
        analysis = {
            'topic': '',
            'key_steps': []
        }
        
        if '解析' in content or '全纯' in content:
            analysis['topic'] = '解析函数'
            analysis['key_steps'] = [
                '1. Cauchy-Riemann方程：u_x=v_y, u_y=-v_x',
                '2. 解析函数的实部和虚部是调和函数',
                '3. 解析函数的导数公式'
            ]
        elif '积分' in content:
            analysis['topic'] = '复积分'
            analysis['key_steps'] = [
                '1. Cauchy定理：解析函数在单连通域中的积分只依赖端点',
                '2. Cauchy积分公式',
                '3. 留数定理计算复积分'
            ]
        elif '级数' in content:
            analysis['topic'] = '级数'
            analysis['key_steps'] = [
                '1. 幂级数的收敛半径',
                '2. Laurent级数展开',
                '3. 孤立奇点的分类'
            ]
        
        return analysis
    
    def _analyze_functional_analysis(self, content: str) -> Dict:
        """分析泛函分析"""
        analysis = {
            'space_type': '',
            'key_steps': []
        }
        
        if 'Hilbert' in content:
            analysis['space_type'] = 'Hilbert空间'
            analysis['key_steps'] = [
                '1. 完备的内积空间',
                '2. 正交分解',
                '3. 正交投影',
                '4. Riesz表示定理'
            ]
        elif 'Banach' in content:
            analysis['space_type'] = 'Banach空间'
            analysis['key_steps'] = [
                '1. 完备的赋范空间',
                '2. 有界线性算子',
                '3. 一致有界原理/Banach-Steinhaus定理'
            ]
        
        return analysis
    
    def _analyze_real_analysis(self, content: str) -> Dict:
        """分析实变函数"""
        analysis = {
            'topic': '',
            'key_steps': []
        }
        
        if '测度' in content:
            analysis['topic'] = '测度论'
            analysis['key_steps'] = [
                '1. 外测度→可测集→测度',
                '2. Carathéodory条件',
                '3. 可测函数的定义',
                '4. Egorov定理、Dini定理'
            ]
        elif '积分' in content and 'Lebesgue' in content:
            analysis['topic'] = 'Lebesgue积分'
            analysis['key_steps'] = [
                '1. 简单函数逼近',
                '2. 非负函数的积分',
                '3. 一般函数的积分分解',
                '4. Levi渐升列定理、Fatou引理、Lebesgue控制收敛定理'
            ]
        
        return analysis
    
    def _analyze_linear_algebra(self, content: str) -> Dict:
        """分析高等代数"""
        analysis = {
            'topic': '',
            'key_steps': []
        }
        
        if '特征值' in content or '特征向量' in content:
            analysis['topic'] = '特征值与特征向量'
            analysis['key_steps'] = [
                '1. 特征多项式det(A-λI)=0',
                '2. 求特征值λ',
                '3. 解齐次线性方程组(A-λI)x=0',
                '4. 求特征向量'
            ]
        elif '线性空间' in content:
            analysis['topic'] = '线性空间'
            analysis['key_steps'] = [
                '1. 验证八条公理',
                '2. 求基与维数',
                '3. 求坐标',
                '4. 基变换与坐标变换'
            ]
        elif '相似' in content:
            analysis['topic'] = '矩阵相似'
            analysis['key_steps'] = [
                '1. 相似的定义：P⁻¹AP=B',
                '2. 相似矩阵有相同的特征多项式',
                '3. Jordan标准形'
            ]
        
        return analysis
    
    def _analyze_ode(self, content: str) -> Dict:
        """分析常微分方程"""
        analysis = {
            'type': '',
            'key_steps': []
        }
        
        analysis['key_steps'] = [
            '1. 判断方程类型（一阶/高阶、线性/非线性）',
            '2. 选择适当的解法',
            '3. 验证解的存在唯一性条件',
            '4. 初值问题或边值问题'
        ]
        
        return analysis
    
    def _analyze_probability(self, content: str) -> Dict:
        """分析概率论"""
        analysis = {
            'topic': '',
            'key_steps': []
        }
        
        if '期望' in content:
            analysis['topic'] = '数学期望'
            analysis['key_steps'] = [
                '1. 明确随机变量',
                '2. 求分布或分布函数',
                '3. 计算期望（定义或性质）'
            ]
        elif '大数定律' in content or '中心极限定理' in content:
            analysis['topic'] = '极限定理'
        
        return analysis
    
    def _analyze_analytic_geometry(self, content: str) -> Dict:
        """分析解析几何"""
        return {'topic': '解析几何', 'key_steps': ['向量法', '坐标法']}
    
    def _analyze_number_theory(self, content: str) -> Dict:
        """分析数论"""
        return {'topic': '数论', 'key_steps': ['同余', '素数', '数论函数']}
    
    def _analyze_combinatorics(self, content: str) -> Dict:
        """分析组合数学"""
        return {'topic': '组合数学', 'key_steps': ['计数', '生成函数', '递推关系']}
    
    def _analyze_differential_geometry(self, content: str) -> Dict:
        """分析微分几何"""
        return {'topic': '微分几何', 'key_steps': ['曲率', '第一/第二基本形式']}
    
    def _analyze_math_logic(self, content: str) -> Dict:
        """分析数理逻辑"""
        return {'topic': '数理逻辑', 'key_steps': ['公理系统', '一致性', '完全性']}
    
    def _general_analysis(self, content: str) -> Dict:
        """通用分析"""
        return {
            'type': '综合证明',
            'difficulty': '较难',
            'suggestion': '请根据具体课程内容进行分析'
        }
    
    def _get_knowledge(self, course_type: str) -> Dict:
        """获取相关知识"""
        knowledge_map = {
            '数学分析': '大学/数学分析.md',
            '抽象代数': '大学/抽象代数.md',
            '拓扑学': '大学/拓扑学.md',
            '复变函数': '大学/复变函数.md',
            '泛函分析': '大学/泛函分析.md',
            '实变函数': '大学/实变函数.md',
            '高等代数': '大学/高等代数.md',
            '常微分方程': '大学/常微分方程.md',
            '概率论': '大学/概率论.md',
            '解析几何': '大学/解析几何.md',
            '数论': '大学/数论.md',
            '组合数学': '大学/组合数学.md',
            '微分几何': '大学/微分几何.md',
            '数理逻辑': '大学/数理逻辑.md'
        }
        
        return {
            'file': knowledge_map.get(course_type, '大学/数学分析.md'),
            'tips': self._get_tips(course_type)
        }
    
    def _get_tips(self, course_type: str) -> List[str]:
        """获取解题提示"""
        tips_map = {
            '数学分析': [
                'ε-δ语言是基础，必须熟练掌握',
                '注意一致连续与点连续的区别',
                '注意各种中值定理的条件和结论'
            ],
            '抽象代数': [
                '证明群同构用同态基本定理',
                '证明是域需要验证所有公理',
                '注意正规子群与商群的关系'
            ],
            '拓扑学': [
                '紧致性是核心概念',
                '注意各种分离性公理的区别',
                '同伦是研究空间的强有力工具'
            ],
            '复变函数': [
                '解析函数有无穷阶导数',
                '留数定理计算积分很方便',
                '共形映射保持角度'
            ],
            '泛函分析': [
                '完备性是核心',
                '共鸣定理需要逐点有界',
                '谱理论是算子理论的核心'
            ],
            '实变函数': [
                '几乎处处收敛不等于一致收敛',
                'Lebesgue积分优于Riemann积分之处',
                'L^p空间的完备性'
            ]
        }
        
        return tips_map.get(course_type, ['仔细审题，严谨证明'])
    
    def _get_recommendations(self, course_type: str) -> List[Dict]:
        """获取推荐练习"""
        problems = self.problem_library.get(course_type, [])
        return problems[:3] if problems else []
    
    def check_proof_rigor(self, proof: str) -> Dict:
        """
        检查证明的严谨性
        
        Args:
            proof: 证明过程
            
        Returns:
            严谨性检查结果
        """
        issues = []
        
        # 检查ε-δ语言
        if 'ε' in proof or 'epsilon' in proof.lower():
            if 'δ' not in proof and 'delta' not in proof.lower():
                issues.append('使用了ε但未定义δ')
            if '∀ε>0' not in proof and '∀ε' not in proof:
                issues.append('缺少全称量词∀ε>0')
        
        # 检查量词
        if '∃' in proof and not re.search(r'∃\w+', proof):
            issues.append('存在量词后应跟变量名')
        if '∀' in proof and not re.search(r'∀\w+', proof):
            issues.append('全称量词后应跟变量名')
        
        # 检查定义引用
        if '定义' in proof:
            if not re.search(r'定义\s*\d+', proof):
                issues.append('引用定义时应说明定义编号')
        
        # 检查定理引用
        if any(kw in proof for kw in ['定理', '引理', '推论']):
            if not re.search(r'(定理|引理|推论)\s*\d+', proof):
                issues.append('引用定理时应说明编号或名称')
        
        return {
            'rigor_score': max(0, 100 - len(issues) * 15),
            'issues': issues,
            'is_rigorous': len(issues) == 0
        }
    
    def _load_knowledge_base(self) -> Dict:
        """加载知识库"""
        knowledge = {}
        kb_path = 'knowledge_base/大学'
        
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
        kb_path = 'knowledge_base/大学/题库'
        
        if os.path.exists(kb_path):
            for filename in os.listdir(kb_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(kb_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            course = filename.replace('题库.json', '')
                            problems[course] = json.load(f)
                    except:
                        pass
        
        return problems
