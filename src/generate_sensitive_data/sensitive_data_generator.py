"""Main sensitive data generator"""
import os
import random
from typing import List

import pandas as pd
from loguru import logger

from config import GENERATE_DATA_PATH
from .password_style import PasswordStyle
from .normal_text_generator import NormalTextGenerator
from .normal_code_generator import NormalCodeGenerator


class SensitiveDataGenerator:
    """敏感数据生成器主类"""

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.password_styles: List[PasswordStyle] = []
        self.normal_text_generator = NormalTextGenerator(count=1000)  # 统一在 __init__ 中传 count
        self.normal_code_generator = NormalCodeGenerator(count=5000)  # ✅ 添加代码生成器
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def add_password_style(self, style: PasswordStyle):
        self.password_styles.append(style)
        return self

    def generate_weak_passwords(self, target_count: int = 1000) -> List[str]:
        logger.info("🔄 开始生成弱密码（敏感信息）...")
        all_passwords = set()

        for style in self.password_styles:
            try:
                passwords = style.generate()
                all_passwords.update(passwords)
                logger.debug(f"   → 添加 {len(passwords)} 条 {style.__class__.__name__}")
            except Exception as e:
                logger.exception(f"❌ 生成 {style.__class__.__name__} 失败: {e}")

        # 补足数量
        bases = ['pass', 'pwd', '123', 'qwe', 'test', 'user', 'login']
        suffixes = [str(i) for i in range(1, 100)] + ['123', '1234', '520', '1314', '666', '888']

        while len(all_passwords) < target_count:
            base = random.choice(bases)
            suffix = random.choice(suffixes)
            case_func = random.choice([str.lower, str.upper, str.capitalize])
            pwd = case_func(base + suffix)
            all_passwords.add(pwd)

        while len(all_passwords) < target_count:
            num = ''.join([str(random.randint(0, 9)) for _ in range(random.randint(4, 8))])
            all_passwords.add(num)

        logger.success(f"✅ 弱密码生成完成，共 {len(all_passwords)} 条")
        return list(all_passwords)

    def generate_dataset(self):
        logger.info(f"🚀 开始生成敏感数据集: {self.output_path}")

        try:
            weak_passwords = self.generate_weak_passwords(target_count=1000)
            normal_texts = self.normal_text_generator.generate()
            normal_codes = self.normal_code_generator.generate()  # ✅ 获取代码片段

            data = []
            for text in weak_passwords:
                data.append({'text': text, 'is_sensitive': 1})
            for text in normal_texts:
                data.append({'text': text, 'is_sensitive': 0})
            for code in normal_codes:
                data.append({'text': code, 'is_sensitive': 0})  # ✅ 非敏感

            df = pd.DataFrame(data)
            df = df.sample(frac=1, random_state=42).reset_index(drop=True)

            df.to_excel(self.output_path, index=False)
            logger.success(f"🎉 敏感数据集生成成功！")
            logger.info(f"📊 总样本数: {len(df)}")
            logger.info(f"🔴 弱密码 (1): {len(weak_passwords)} 条")
            logger.info(f"🟢 正常文本 (0): {len(normal_texts)} 条")
            logger.info(f"🟢 正常代码 (0): {len(normal_codes)} 条")
            logger.info(f"📁 文件保存路径: {self.output_path}")

        except Exception as e:
            logger.exception(f"❌ 生成数据失败: {e}")
            raise