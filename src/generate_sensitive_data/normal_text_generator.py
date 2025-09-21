"""Normal text generator for sensitive data generation"""
import random
from typing import List

from loguru import logger


class NormalTextGenerator:
    """生成非敏感中文语句，支持指定生成数量，接口风格与 HuaweiStylePassword 保持一致"""

    def __init__(self, count: int = 1000):
        self.count = count
        self.subjects = ['今天', '明天', '昨天', '我', '你', '他', '我们', '大家']
        self.verbs = ['很', '非常', '特别', '真的', '相当', '有点', '']
        self.adjectives = ['好', '开心', '不错', '棒', '顺利', '愉快']
        self.activities = ['开会', '学习', '工作', '休息', '吃饭', '锻炼']
        self.times = ['早上', '中午', '下午', '晚上', '周末', '假期']
        self.locations = ['办公室', '家里', '学校', '公园', '健身房']

    def generate(self) -> List[str]:
        logger.info(f"🔄 开始生成正常文本（非敏感信息），目标 {self.count} 条...")
        texts = []

        patterns = [
            lambda: f"{random.choice(self.subjects)}{random.choice(self.verbs)}{random.choice(self.adjectives)}",
            lambda: f"{random.choice(self.times)}去{random.choice(self.locations)}{random.choice(self.activities)}",
            lambda: f"{random.choice(self.subjects)}要{random.choice(self.activities)}了",
            lambda: f"希望{random.choice(self.subjects)}{random.choice(self.activities)}顺利",
            lambda: f"今天{random.choice(self.activities)}很开心"
        ]

        for _ in range(self.count):
            text = random.choice(patterns)()
            texts.append(text)

        logger.success(f"✅ 正常文本生成完成，共 {len(texts)} 条")
        return texts