# -*- coding: utf-8 -*-
"""
全学段数学证明导师系统 - 测试用例
包含15个测试用例：5个初中、5个高中、5个大学
"""

import unittest
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.router import LevelRouter
from backend.junior.analyzer import JuniorAnalyzer
from backend.senior.analyzer import SeniorAnalyzer
from backend.university.analyzer import UniversityAnalyzer


class TestLevelRouter(unittest.TestCase):
    """测试学段路由器"""
    
    def setUp(self):
        self.router = LevelRouter()
    
    def test_junior_high_keywords(self):
        """测试初中特征词识别"""
        content = "证明三角形全等，AB = DE，∠ABC = ∠DEF"
        result = self.router.route(content)
        self.assertEqual(result['level'], 'junior_high')
    
    def test_senior_high_keywords(self):
        """测试高中特征词识别"""
        content = "用数学归纳法证明数列an+1 = 2an + 1的通项公式"
        result = self.router.route(content)
        self.assertEqual(result['level'], 'senior_high')
    
    def test_university_keywords(self):
        """测试大学特征词识别"""
        content = "证明：∀ε>0, ∃δ>0, 使得当|x-x0|<δ时，有|f(x)-L|<ε"
        result = self.router.route(content)
        self.assertEqual(result['level'], 'university')


class TestJuniorAnalyzer(unittest.TestCase):
    """测试初中分析器"""
    
    def setUp(self):
        self.analyzer = JuniorAnalyzer()
    
    def test_congruence_identification(self):
        """测试全等三角形识别"""
        content = "已知△ABC和△DEF中，AB=DE，AC=DF，BC=EF。证明△ABC≅△DEF"
        result = self.analyzer.analyze(content)
        self.assertEqual(result['proof_type'], '全等三角形证明')
    
    def test_parallel_identification(self):
        """测试平行线识别"""
        content = "如图，直线AB与CD被直线EF所截，∠1 = ∠2。证明AB∥CD"
        result = self.analyzer.analyze(content)
        self.assertEqual(result['proof_type'], '平行线证明')
    
    def test_grading_criteria(self):
        """测试评分标准"""
        self.assertIn('key_step', self.analyzer.grading_criteria)
        self.assertIn('reasoning', self.analyzer.grading_criteria)


class TestSeniorAnalyzer(unittest.TestCase):
    """测试高中分析器"""
    
    def setUp(self):
        self.analyzer = SeniorAnalyzer()
    
    def test_sequence_identification(self):
        """测试数列识别"""
        content = "用数学归纳法证明：1+3+5+...+(2n-1)=n²"
        result = self.analyzer.analyze(content)
        self.assertEqual(result['problem_type'], '数列与归纳法')
    
    def test_inequality_identification(self):
        """测试不等式识别"""
        content = "证明：a²+b²≥2ab，对于任意实数a,b成立"
        result = self.analyzer.analyze(content)
        self.assertEqual(result['problem_type'], '不等式证明')
    
    def test_solid_geometry_identification(self):
        """测试立体几何识别"""
        content = "在棱锥P-ABCD中，PA⊥底面ABCD。证明PA是棱锥的高"
        result = self.analyzer.analyze(content)
        self.assertEqual(result['problem_type'], '立体几何')


class TestUniversityAnalyzer(unittest.TestCase):
    """测试大学分析器"""
    
    def setUp(self):
        self.analyzer = UniversityAnalyzer()
    
    def test_epsilon_delta_identification(self):
        """测试ε-δ语言识别"""
        content = "证明：lim(x→0) sin(x)/x = 1，使用ε-δ语言"
        result = self.analyzer.analyze(content)
        self.assertIn('ε-δ语言', result['proof_methods'])
    
    def test_group_identification(self):
        """测试群论识别"""
        content = "设G是一个群，证明：对于任意g∈G，有(g⁻¹)⁻¹ = g"
        result = self.analyzer.analyze(content)
        self.assertEqual(result['course_type'], '抽象代数')
    
    def test_rigor_criteria(self):
        """测试严谨性标准"""
        self.assertIn('epsilon_delta', self.analyzer.rigor_criteria)
        self.assertIn('quantifiers', self.analyzer.rigor_criteria)


class TestProofCorrectness(unittest.TestCase):
    """测试证明正确性检查"""
    
    def test_junior_proof_check(self):
        """测试初中证明检查"""
        analyzer = JuniorAnalyzer()
        result = analyzer.check_proof(
            "∵ AB = DE, BC = EF, AC = DF\n∴ △ABC ≅ △DEF (SSS)",
            "∵ AB = DE, BC = EF, AC = DF\n∴ △ABC ≅ △DEF (SSS)"
        )
        self.assertGreater(result['total_score'], 0)
    
    def test_university_rigor_check(self):
        """测试大学证明严谨性检查"""
        analyzer = UniversityAnalyzer()
        proof = "∀ε>0, ∃δ>0, 当|x-x0|<δ时，有|f(x)-L|<ε"
        result = analyzer.check_proof_rigor(proof)
        self.assertIn('rigor_score', result)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_pipeline(self):
        """测试完整流程"""
        router = LevelRouter()
        
        # 初中题目
        junior = "证明三角形全等，AB=DE，AC=DF，BC=EF"
        result = router.route(junior)
        self.assertEqual(result['level'], 'junior_high')
        
        # 高中题目
        senior = "用数学归纳法证明：1+2+...+n=n(n+1)/2"
        result = router.route(senior)
        self.assertEqual(result['level'], 'senior_high')
        
        # 大学题目
        university = "证明：若f在[a,b]连续，则f在[a,b]上有界"
        result = router.route(university)
        self.assertEqual(result['level'], 'university')


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def test_empty_content(self):
        """测试空内容"""
        router = LevelRouter()
        result = router.route("")
        # 应该返回unknown或默认学段
        self.assertIn(result['level'], ['junior_high', 'unknown'])
    
    def test_mixed_keywords(self):
        """测试混合关键词"""
        router = LevelRouter()
        content = "用数学归纳法证明全等三角形的性质"
        result = router.route(content)
        # 应该根据主要特征词判断
        self.assertIn(result['level'], ['junior_high', 'senior_high'])


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestLevelRouter))
    suite.addTests(loader.loadTestsFromTestCase(TestJuniorAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestSeniorAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestUniversityAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestProofCorrectness))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
