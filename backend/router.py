# -*- coding: utf-8 -*-
"""
学段路由器模块
负责根据题目内容自动识别和路由到相应学段
"""

import re
from typing import Dict, Tuple, Optional


class LevelRouter:
    """学段路由器"""
    
    def __init__(self):
        """初始化路由器"""
        # 定义各学段的特征关键词
        self.junior_keywords = {
            'geometric': [
                '全等', '三角形', '平行', '垂直', '角平分线', '中点',
                '等腰', '直角', '勾股', '圆', '弧', '弦', '圆周角',
                '平行四边形', '矩形', '菱形', '正方形', '梯形',
                '多边形', '内角', '外角', '对顶角', '同位角', '内错角'
            ],
            'algebra': [
                '因式分解', '方程', '一元', '二元', '方程组', '解',
                '系数', '常数', '整式', '分式', '根号', '平方'
            ]
        }
        
        self.senior_keywords = {
            'calculus': ['导数', '微分', '积分', '极限', '连续', '可导'],
            'vector': ['向量', '数量积', '向量积', '坐标', '空间向量'],
            'conic': ['椭圆', '双曲线', '抛物线', '圆锥曲线', '焦点', '准线'],
            'induction': ['数学归纳法', '归纳', '递推', '数列'],
            'geometry': ['立体几何', '空间', '面角', '二面角', '体积', '表面积'],
            'trigonometry': ['正弦', '余弦', '正切', '恒等式', '和差化积', '积化和差'],
            'inequality': ['不等式', '均值不等式', '柯西', '排序', 'Jensen'],
            'probability': ['概率', '排列', '组合', '二项式', '期望', '方差']
        }
        
        self.university_keywords = {
            'analysis': ['ε-δ', '极限', '连续', '可导', '可积', '一致收敛', 
                        'Borel', 'Lebesgue', 'Riemann', 'Cauchy'],
            'algebra': ['群', '环', '域', '同态', '同构', '子群', '陪集',
                       '理想', '向量空间', '线性变换', '特征值', 'Jordan'],
            'topology': ['拓扑', '开集', '闭集', '紧致', '连通', '同伦',
                       '同胚', '流形', '度量', '范数'],
            'complex': ['复变', '解析', '奇点', '留数', '级数', 'Laurent',
                       'Cauchy', 'Morera', 'Rouché'],
            'functional': ['泛函', 'Hilbert', 'Banach', '算子', '谱',
                          '共轭', '对偶', '紧致算子'],
            'measure': ['测度', 'Lebesgue', 'Borel', '可测', '积分',
                       '几乎处处', '几乎必然', 'L^p']
        }
    
    def route(self, content: str) -> Dict:
        """
        根据内容路由到相应学段
        
        Args:
            content: 题目内容
            
        Returns:
            Dict: 包含level、domain、confidence等信息的字典
        """
        # 提取文本内容
        text = self._extract_text(content)
        
        # 分析各学段匹配度
        junior_score = self._calculate_score(text, self.junior_keywords)
        senior_score = self._calculate_score(text, self.senior_keywords)
        university_score = self._calculate_score(text, self.university_keywords)
        
        # 确定最佳学段
        scores = {
            'junior_high': junior_score,
            'senior_high': senior_score,
            'university': university_score
        }
        
        best_level = max(scores, key=scores.get)
        max_score = scores[best_level]
        
        # 计算置信度
        if max_score == 0:
            confidence = 0.0
        else:
            total = sum(scores.values())
            confidence = max_score / total if total > 0 else 0
        
        # 获取领域分类
        domain = self._classify_domain(text, best_level)
        
        return {
            'level': best_level,
            'level_name': self._get_level_name(best_level),
            'domain': domain,
            'confidence': round(confidence, 2),
            'scores': {k: round(v, 2) for k, v in scores.items()}
        }
    
    def _extract_text(self, content: str) -> str:
        """提取文本内容"""
        # 移除LaTeX公式标记
        text = re.sub(r'\$+[^\$]+\$+', '', content)
        # 移除图片标记
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        return text
    
    def _calculate_score(self, text: str, keywords_dict: Dict) -> float:
        """计算匹配分数"""
        score = 0.0
        for category, keywords in keywords_dict.items():
            for keyword in keywords:
                if keyword in text:
                    # 核心关键词权重更高
                    if category in ['geometric', 'calculus', 'analysis']:
                        score += 2.0
                    else:
                        score += 1.0
        return score
    
    def _classify_domain(self, text: str, level: str) -> str:
        """分类到具体领域"""
        if level == 'junior_high':
            if any(k in text for k in self.junior_keywords['geometric']):
                return '平面几何'
            return '代数'
        
        elif level == 'senior_high':
            # 检查各领域关键词
            if any(k in text for k in self.senior_keywords['geometry']):
                return '立体几何'
            elif any(k in text for k in self.senior_keywords['conic']):
                return '解析几何'
            elif any(k in text for k in self.senior_keywords['calculus']):
                return '函数与导数'
            elif any(k in text for k in self.senior_keywords['induction']):
                return '数列与归纳法'
            elif any(k in text for k in self.senior_keywords['trigonometry']):
                return '三角函数'
            elif any(k in text for k in self.senior_keywords['vector']):
                return '向量与复数'
            elif any(k in text for k in self.senior_keywords['probability']):
                return '概率统计'
            elif any(k in text for k in self.senior_keywords['inequality']):
                return '不等式证明'
            return '代数与恒等式'
        
        elif level == 'university':
            if any(k in text for k in self.university_keywords['analysis']):
                return '数学分析'
            elif any(k in text for k in self.university_keywords['algebra']):
                return '高等代数'
            elif any(k in text for k in self.university_keywords['topology']):
                return '拓扑学'
            elif any(k in text for k in self.university_keywords['complex']):
                return '复变函数'
            elif any(k in text for k in self.university_keywords['functional']):
                return '泛函分析'
            elif any(k in text for k in self.university_keywords['measure']):
                return '实变函数'
            return '其他'
        
        return '未知'
    
    def _get_level_name(self, level: str) -> str:
        """获取学段中文名称"""
        names = {
            'junior_high': '初中数学',
            'senior_high': '高中数学',
            'university': '大学数学'
        }
        return names.get(level, '未知')
    
    def get_domain_knowledge(self, level: str, domain: str) -> Dict:
        """获取领域知识"""
        knowledge_files = {
            'junior_high': {
                '平面几何': '平面几何.md',
                '代数': '代数证明.md'
            },
            'senior_high': {
                '立体几何': '立体几何.md',
                '解析几何': '解析几何.md',
                '函数与导数': '函数性质.md',
                '数列与归纳法': '数列与归纳法.md',
                '三角函数': '三角函数.md',
                '向量与复数': '向量与复数.md',
                '概率统计': '概率统计.md',
                '不等式证明': '不等式证明.md',
                '代数与恒等式': '代数与恒等式.md'
            },
            'university': {
                '数学分析': '数学分析.md',
                '高等代数': '高等代数.md',
                '拓扑学': '拓扑学.md',
                '复变函数': '复变函数.md',
                '泛函分析': '泛函分析.md',
                '实变函数': '实变函数.md'
            }
        }
        
        file_name = knowledge_files.get(level, {}).get(domain)
        if file_name:
            level_dir = {'junior_high': '初中', 'senior_high': '高中', 'university': '大学'}[level]
            return {'path': f'knowledge_base/{level_dir}/{file_name}'}
        
        return {}
