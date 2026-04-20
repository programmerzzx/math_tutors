# -*- coding: utf-8 -*-
"""
学习报告生成器
生成跨学段学习报告和统计信息
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class ReportGenerator:
    """学习报告生成器"""
    
    def __init__(self):
        """初始化报告生成器"""
        self.user_data_path = 'user_data'
        os.makedirs(self.user_data_path, exist_ok=True)
    
    def generate_report(self, user_id: str = 'default') -> Dict:
        """
        生成学习报告
        
        Args:
            user_id: 用户ID
            
        Returns:
            学习报告字典
        """
        # 加载用户数据
        user_data = self._load_user_data(user_id)
        
        # 生成各部分报告
        report = {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'summary': self._generate_summary(user_data),
            'level_statistics': self._generate_level_statistics(user_data),
            'topic_mastery': self._generate_topic_mastery(user_data),
            'progress_tracking': self._generate_progress_tracking(user_data),
            'learning_path': self._generate_learning_path(user_data),
            'recommendations': self._generate_recommendations(user_data)
        }
        
        return report
    
    def _load_user_data(self, user_id: str) -> Dict:
        """加载用户数据"""
        filepath = os.path.join(self.user_data_path, f'{user_id}.json')
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 返回默认数据
        return {
            'history': [],
            'level_counts': {'junior_high': 0, 'senior_high': 0, 'university': 0},
            'topic_mastery': {},
            'last_active': None
        }
    
    def _generate_summary(self, user_data: Dict) -> Dict:
        """生成摘要"""
        history = user_data.get('history', [])
        
        total_problems = len(history)
        correct_count = sum(1 for h in history if h.get('score', 0) >= 60)
        avg_score = sum(h.get('score', 0) for h in history) / total_problems if total_problems > 0 else 0
        
        return {
            'total_problems': total_problems,
            'correct_problems': correct_count,
            'accuracy_rate': round(correct_count / total_problems * 100, 1) if total_problems > 0 else 0,
            'average_score': round(avg_score, 1),
            'total_study_time': sum(h.get('time_spent', 0) for h in history),
            'current_streak': self._calculate_streak(user_data)
        }
    
    def _generate_level_statistics(self, user_data: Dict) -> Dict:
        """生成学段统计"""
        level_counts = user_data.get('level_counts', {'junior_high': 0, 'senior_high': 0, 'university': 0})
        
        level_names = {
            'junior_high': '初中数学',
            'senior_high': '高中数学',
            'university': '大学数学'
        }
        
        statistics = {}
        for level, count in level_counts.items():
            statistics[level] = {
                'name': level_names.get(level, level),
                'problem_count': count,
                'percentage': 0  # 将在下面计算
            }
        
        total = sum(level_counts.values())
        if total > 0:
            for level in statistics:
                statistics[level]['percentage'] = round(
                    statistics[level]['problem_count'] / total * 100, 1
                )
        
        # 最活跃学段
        most_active = max(level_counts.items(), key=lambda x: x[1]) if any(level_counts.values()) else None
        
        return {
            'distribution': statistics,
            'most_active_level': {
                'level': most_active[0] if most_active else None,
                'name': level_names.get(most_active[0], '无') if most_active else '无',
                'count': most_active[1] if most_active else 0
            }
        }
    
    def _generate_topic_mastery(self, user_data: Dict) -> Dict:
        """生成知识点掌握情况"""
        history = user_data.get('history', [])
        topic_scores = defaultdict(list)
        
        for item in history:
            topic = item.get('topic', '其他')
            score = item.get('score', 0)
            topic_scores[topic].append(score)
        
        mastery = {}
        for topic, scores in topic_scores.items():
            avg_score = sum(scores) / len(scores)
            mastery[topic] = {
                'attempts': len(scores),
                'average_score': round(avg_score, 1),
                'best_score': max(scores),
                'level': self._score_to_level(avg_score)
            }
        
        # 按掌握程度排序
        sorted_mastery = dict(sorted(
            mastery.items(),
            key=lambda x: x[1]['average_score'],
            reverse=True
        ))
        
        return sorted_mastery
    
    def _generate_progress_tracking(self, user_data: Dict) -> Dict:
        """生成进度追踪"""
        history = user_data.get('history', [])
        
        # 按日期统计
        daily_progress = defaultdict(lambda: {'count': 0, 'total_score': 0})
        
        for item in history:
            date = item.get('date', datetime.now().strftime('%Y-%m-%d'))
            daily_progress[date]['count'] += 1
            daily_progress[date]['total_score'] += item.get('score', 0)
        
        # 计算趋势
        recent_days = 7
        today = datetime.now()
        trend = []
        
        for i in range(recent_days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            data = daily_progress.get(date, {'count': 0, 'total_score': 0})
            avg = data['total_score'] / data['count'] if data['count'] > 0 else 0
            trend.append({
                'date': date,
                'count': data['count'],
                'avg_score': round(avg, 1)
            })
        
        return {
            'daily_breakdown': dict(daily_progress),
            'weekly_trend': list(reversed(trend)),
            'improvement_rate': self._calculate_improvement(history)
        }
    
    def _generate_learning_path(self, user_data: Dict) -> Dict:
        """生成学习路径建议"""
        topic_mastery = self._generate_topic_mastery(user_data)
        level_stats = user_data.get('level_counts', {})
        
        path = []
        
        # 分析用户在各学段的进度
        if level_stats.get('junior_high', 0) < 5:
            path.append({
                'level': 'junior_high',
                'suggestion': '建议从初中基础开始巩固',
                'topics': ['平面几何', '代数基础']
            })
        
        if level_stats.get('senior_high', 0) < level_stats.get('junior_high', 0) * 0.5:
            path.append({
                'level': 'senior_high',
                'suggestion': '可以在巩固初中基础后进入高中内容',
                'topics': ['函数与导数', '数列']
            })
        
        # 找出薄弱知识点
        weak_topics = [t for t, m in topic_mastery.items() if m['average_score'] < 70]
        if weak_topics:
            path.append({
                'level': 'weakness_improvement',
                'suggestion': '需要加强的知识点',
                'topics': weak_topics[:3]
            })
        
        return {
            'suggested_path': path,
            'estimated_duration': f'{len(path) * 2}周' if path else '已完成基础学习'
        }
    
    def _generate_recommendations(self, user_data: Dict) -> List[Dict]:
        """生成个性化推荐"""
        recommendations = []
        
        topic_mastery = self._generate_topic_mastery(user_data)
        level_stats = user_data.get('level_counts', {})
        
        # 基于薄弱知识点推荐
        weak_topics = [t for t, m in topic_mastery.items() if m['average_score'] < 60]
        for topic in weak_topics[:2]:
            recommendations.append({
                'type': 'weakness_improvement',
                'topic': topic,
                'priority': 'high',
                'suggestion': f'建议加强{topic}的练习'
            })
        
        # 基于学段分布推荐
        if level_stats.get('junior_high', 0) > level_stats.get('senior_high', 0) * 2:
            recommendations.append({
                'type': 'level_progression',
                'priority': 'medium',
                'suggestion': '初中内容掌握较好，可以开始高中内容的学习'
            })
        
        # 基于准确率推荐
        history = user_data.get('history', [])
        recent = history[-5:] if len(history) >= 5 else history
        recent_accuracy = sum(1 for h in recent if h.get('score', 0) >= 60) / len(recent) if recent else 0
        
        if recent_accuracy > 0.8:
            recommendations.append({
                'type': 'difficulty_increase',
                'priority': 'medium',
                'suggestion': '准确率较高，建议挑战更高难度题目'
            })
        elif recent_accuracy < 0.5:
            recommendations.append({
                'type': 'difficulty_decrease',
                'priority': 'high',
                'suggestion': '准确率较低，建议巩固基础后继续'
            })
        
        return recommendations
    
    def _calculate_streak(self, user_data: Dict) -> int:
        """计算连续学习天数"""
        history = user_data.get('history', [])
        if not history:
            return 0
        
        dates = set(item.get('date', '') for item in history if item.get('date'))
        if not dates:
            return 0
        
        streak = 0
        today = datetime.now().date()
        
        for i in range(365):
            check_date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            if check_date in dates:
                streak += 1
            else:
                break
        
        return streak
    
    def _calculate_improvement(self, history: List) -> float:
        """计算进步率"""
        if len(history) < 4:
            return 0.0
        
        first_half = history[:len(history)//2]
        second_half = history[len(history)//2:]
        
        first_avg = sum(h.get('score', 0) for h in first_half) / len(first_half)
        second_avg = sum(h.get('score', 0) for h in second_half) / len(second_half)
        
        return round(second_avg - first_avg, 1)
    
    def _score_to_level(self, score: float) -> str:
        """将分数转换为掌握等级"""
        if score >= 90:
            return '精通'
        elif score >= 75:
            return '熟练'
        elif score >= 60:
            return '一般'
        else:
            return '薄弱'
    
    def export_report(self, user_id: str, format: str = 'json') -> str:
        """
        导出报告
        
        Args:
            user_id: 用户ID
            format: 导出格式 (json, csv, html)
            
        Returns:
            报告文件路径
        """
        report = self.generate_report(user_id)
        
        if format == 'json':
            filepath = os.path.join(self.user_data_path, f'{user_id}_report.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        
        elif format == 'html':
            filepath = os.path.join(self.user_data_path, f'{user_id}_report.html')
            html_content = self._generate_html_report(report)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return filepath
    
    def _generate_html_report(self, report: Dict) -> str:
        """生成HTML格式的报告"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>学习报告 - {report['user_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 8px; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 24px; color: #2196F3; }}
        .metric-label {{ color: #666; }}
    </style>
</head>
<body>
    <h1>📊 学习报告</h1>
    <p>生成时间: {report['generated_at']}</p>
    
    <div class="section">
        <h2>学习概览</h2>
        <div class="metric">
            <div class="metric-value">{report['summary']['total_problems']}</div>
            <div class="metric-label">总题目数</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report['summary']['accuracy_rate']}%</div>
            <div class="metric-label">正确率</div>
        </div>
        <div class="metric">
            <div class="metric-value">{report['summary']['average_score']}</div>
            <div class="metric-label">平均分</div>
        </div>
    </div>
</body>
</html>
"""
