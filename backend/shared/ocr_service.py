# -*- coding: utf-8 -*-
"""
OCR服务模块
提供数学公式识别功能
"""

import base64
import io
from typing import Optional


class OCRService:
    """OCR服务类"""
    
    def __init__(self):
        """初始化OCR服务"""
        # 预留PaddleOCR接口
        self.use_paddle = False  # 默认关闭，需要时可开启
        self._init_paddle_ocr()
    
    def _init_paddle_ocr(self):
        """初始化PaddleOCR"""
        try:
            # 尝试导入PaddleOCR
            from paddleocr import PaddleOCR
            
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='ch',
                use_gpu=False,
                show_log=False
            )
            self.use_paddle = True
            print("PaddleOCR 初始化成功")
        except ImportError:
            print("PaddleOCR 未安装，将使用模拟OCR服务")
            self.use_paddle = False
        except Exception as e:
            print(f"PaddleOCR 初始化失败: {e}")
            self.use_paddle = False
    
    def recognize(self, image_data: str) -> str:
        """
        识别图片中的数学公式
        
        Args:
            image_data: base64编码的图片数据或图片路径
            
        Returns:
            识别的文本内容（LaTeX格式）
        """
        if self.use_paddle:
            return self._paddle_ocr_recognize(image_data)
        else:
            return self._mock_ocr_recognize(image_data)
    
    def _paddle_ocr_recognize(self, image_data: str) -> str:
        """使用PaddleOCR进行识别"""
        try:
            # 解码base64图片
            if isinstance(image_data, str):
                if image_data.startswith('data:image'):
                    # 去除data URI前缀
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            # 转为numpy数组
            import numpy as np
            image = np.frombuffer(image_bytes, dtype=np.uint8)
            image = image.reshape((1, -1, 3)) if len(image) > 0 else np.zeros((100, 100, 3), dtype=np.uint8)
            
            # 识别
            result = self.ocr.ocr(image, cls=True)
            
            if result and result[0]:
                texts = []
                for line in result[0]:
                    texts.append(line[1][0])
                return '\n'.join(texts)
            else:
                return "未能识别到文本"
                
        except Exception as e:
            return f"OCR识别错误: {str(e)}"
    
    def _mock_ocr_recognize(self, image_data: str) -> str:
        """模拟OCR识别（用于测试或未安装PaddleOCR时）"""
        # 这里返回一个示例文本
        return """
请上传图片以进行OCR识别。

当前服务未配置OCR引擎，请：
1. 安装 PaddlePaddle: pip install paddlepaddle
2. 安装 PaddleOCR: pip install paddleocr
3. 重启服务

或者您可以直接输入数学题目文本内容。
"""
    
    def recognize_latex(self, image_data: str) -> str:
        """
        识别图片中的数学公式并转换为LaTeX
        
        Args:
            image_data: base64编码的图片数据
            
        Returns:
            LaTeX格式的文本
        """
        # 基础识别
        text = self.recognize(image_data)
        
        # 转换为LaTeX格式
        latex = self._text_to_latex(text)
        
        return latex
    
    def _text_to_latex(self, text: str) -> str:
        """将普通文本转换为LaTeX格式"""
        # 简单的文本到LaTeX转换
        latex = text
        
        # 替换常见数学符号
        replacements = {
            '△': r'\triangle',
            '≅': r'\cong',
            '∥': r'\parallel',
            '⊥': r'\perp',
            '∠': r'\angle',
            '∈': r'\in',
            '∉': r'\notin',
            '⊂': r'\subset',
            '⊃': r'\supset',
            '∪': r'\cup',
            '∩': r'\cap',
            '∞': r'\infty',
            '≤': r'\leq',
            '≥': r'\geq',
            '≠': r'\neq',
            '±': r'\pm',
            '×': r'\times',
            '÷': r'\div',
            '·': r'\cdot',
            '∀': r'\forall',
            '∃': r'\exists',
            '∵': r'\because',
            '∴': r'\therefore',
        }
        
        for char, latex_char in replacements.items():
            latex = latex.replace(char, latex_char)
        
        # 处理分数
        import re
        # 处理如 a/b 的分数
        latex = re.sub(r'(\w+)/(\w+)', r'\\frac{\1}{\2}', latex)
        
        # 处理上标
        latex = re.sub(r'\^(\d+)', r'^{\1}', latex)
        
        # 处理下标
        latex = re.sub(r'_(\d+)', r'_{\1}', latex)
        
        return latex
    
    def batch_recognize(self, image_list: list) -> list:
        """
        批量识别图片
        
        Args:
            image_list: 图片数据列表
            
        Returns:
            识别结果列表
        """
        results = []
        for image_data in image_list:
            result = self.recognize(image_data)
            results.append(result)
        return results
