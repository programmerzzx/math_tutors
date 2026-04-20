# -*- coding: utf-8 -*-
"""
用户管理模块
管理用户数据和会话
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        """初始化用户管理器"""
        self.user_data_path = 'user_data'
        os.makedirs(self.user_data_path, exist_ok=True)
    
    def create_session(self, user_id: str) -> Dict:
        """
        创建用户会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            会话信息
        """
        session = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
            'current_level': 'junior_high',
            'history': []
        }
        
        self._save_session(user_id, session)
        return session
    
    def get_session(self, user_id: str) -> Optional[Dict]:
        """
        获取用户会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            会话信息
        """
        filepath = os.path.join(self.user_data_path, f'{user_id}_session.json')
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    # 更新最后活跃时间
                    session['last_active'] = datetime.now().isoformat()
                    self._save_session(user_id, session)
                    return session
            except:
                pass
        
        # 创建新会话
        return self.create_session(user_id)
    
    def update_session(self, user_id: str, updates: Dict) -> bool:
        """
        更新用户会话
        
        Args:
            user_id: 用户ID
            updates: 更新内容
            
        Returns:
            是否成功
        """
        session = self.get_session(user_id)
        if session:
            session.update(updates)
            session['last_active'] = datetime.now().isoformat()
            return self._save_session(user_id, session)
        return False
    
    def add_problem_record(self, user_id: str, problem_data: Dict) -> bool:
        """
        添加题目记录
        
        Args:
            user_id: 用户ID
            problem_data: 题目数据
            
        Returns:
            是否成功
        """
        session = self.get_session(user_id)
        if session:
            # 添加记录
            record = {
                'timestamp': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'level': problem_data.get('level'),
                'topic': problem_data.get('topic'),
                'score': problem_data.get('score', 0),
                'time_spent': problem_data.get('time_spent', 0),
                'status': problem_data.get('status', 'completed')
            }
            
            session['history'].append(record)
            
            # 更新学段计数
            level = problem_data.get('level', 'junior_high')
            session['level_counts'][level] = session['level_counts'].get(level, 0) + 1
            
            return self._save_session(user_id, session)
        
        return False
    
    def get_statistics(self, user_id: str) -> Dict:
        """
        获取用户统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计数据
        """
        session = self.get_session(user_id)
        if not session:
            return {}
        
        history = session.get('history', [])
        
        return {
            'total_problems': len(history),
            'level_distribution': session.get('level_counts', {}),
            'recent_problems': history[-10:],
            'avg_score': sum(h.get('score', 0) for h in history) / len(history) if history else 0
        }
    
    def reset_progress(self, user_id: str) -> bool:
        """
        重置用户进度
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否成功
        """
        session = self.get_session(user_id)
        if session:
            session['history'] = []
            session['level_counts'] = {'junior_high': 0, 'senior_high': 0, 'university': 0}
            session['last_active'] = datetime.now().isoformat()
            return self._save_session(user_id, session)
        return False
    
    def _save_session(self, user_id: str, session: Dict) -> bool:
        """保存会话"""
        try:
            filepath = os.path.join(self.user_data_path, f'{user_id}_session.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存会话失败: {e}")
            return False
    
    def generate_user_id(self) -> str:
        """生成用户ID"""
        timestamp = datetime.now().isoformat()
        hash_object = hashlib.md5(timestamp.encode())
        return f"user_{hash_object.hexdigest()[:8]}"
