# generate_sensitive_data.py
import base64
import json
import os
import random
import string
from abc import ABC, abstractmethod
from typing import List

import pandas as pd
from loguru import logger

from config import GENERATE_DATA_PATH


class PasswordStyle(ABC):
    """弱密码风格抽象基类"""

    @abstractmethod
    def generate(self) -> List[str]:
        pass


class CommonWeakPassword(PasswordStyle):
    """通用弱密码，支持指定生成数量"""

    def __init__(self, count: int = 50):
        self.count = count
        self.patterns = [
            '123456', '123456789', '12345', '1234567', '1234567890',
            '111111', '000000', '123321', '123123', '666666', '888888',
            'abc123', 'password', 'admin', 'root', 'user123', 'login',
            'passw0rd', 'p@ssw0rd', 'qwerty', '1q2w3e', '123qwe',
            'test123', 'demo123', 'welcome123', '13800138000', '13912345678'
        ]

    def generate(self) -> List[str]:
        # 重复填充以达到 count
        passwords = []
        while len(passwords) < self.count:
            passwords.extend(self.patterns)
        passwords = passwords[:self.count]  # 截取指定数量
        return passwords


class HuaweiStylePassword(PasswordStyle):
    """华为相关弱密码，支持指定生成数量"""

    def __init__(self, count: int = 100):
        self.count = count
        self.bases = ['huawei', 'hw', 'HW', 'Hw']
        self.suffixes = ['123', '1234', '123456', '132', '456', '520', '1314', '666', '888', '2025', '2024', '2023',
                         '147', '369', '258', '963', '741', '123', '456']
        self.specials = ['@123', '@369', '#123', '!123', '.123', '_123', '@132', '.456']

    def generate(self) -> List[str]:
        passwords = set()
        transformations = [str.lower, str.upper, str.capitalize, lambda x: x]

        for base in self.bases:
            for t in transformations:
                b = t(base.replace(' ', ''))
                for suf in self.suffixes:
                    passwords.add(b + suf)
                    passwords.add(suf + b)

        for base in ['huawei', 'hw']:
            for t in transformations:
                b = t(base)
                for sp in self.specials:
                    passwords.add(b + sp)
                    passwords.add(sp + b)

        # 符号替换
        for b in ['huawei', 'Hw', 'hw']:
            if 'huawei' in b.lower():
                passwords.add(b.replace('u', '@', 1))
                passwords.add(b.replace('a', '@', 1))
                passwords.add(b.replace('i', '1'))
                passwords.add(b.replace('e', '3'))
                passwords.add(b.replace('a', '4'))

        common_combinations = [
            'huawei123', 'huawei123456', 'huawei132', 'hw123', 'hw132',
            'Hw@123', 'hw#123', 'hu@wei123', '123huawei', '456huawei'
        ]
        passwords.update(common_combinations)

        # 转为列表并重复填充至 count
        passwords = list(passwords)
        while len(passwords) < self.count:
            passwords.extend(passwords)
        passwords = passwords[:self.count]

        logger.debug(f"✅ 生成华为风格弱密码 {len(passwords)} 条")
        return passwords


class DjangoTokenStylePassword(PasswordStyle):
    """
    模拟 Django 重置密码 Token 风格
    格式：{user_id}!{random_string}
    例如：123!a1b2c3d4e5f6g7h8i9j0k1l2
    """

    def __init__(self, count: int = 150, user_id_range: tuple = (1, 10000)):
        self.count = count
        self.user_id_min, self.user_id_max = user_id_range
        self.chars = 'abcdefghijklmnopqrstuvwxyz0123456789'

    def _random_string(self, length: int) -> str:
        return ''.join(random.choices(self.chars, k=length))

    def generate(self) -> List[str]:
        logger.info("🔄 开始生成 Django Token 风格弱密码...")
        tokens = set()

        while len(tokens) < self.count:
            user_id = random.randint(self.user_id_min, self.user_id_max)
            length = random.randint(12, 20)  # Django token 长度
            random_part = self._random_string(length)
            token = f"{user_id}!{random_part}"
            tokens.add(token)

        logger.success(f"✅ Django Token 风格生成完成，共 {len(tokens)} 条")
        return list(tokens)


class TokenStylePassword(PasswordStyle):
    """
    生成多种认证方式的 Token 风格弱密码，包括：
    - 传统 Token（UUID、hex）
    - JWT Token（模拟三段式结构）
    - OAuth Bearer Token（随机字符串）
    """

    def __init__(self, count: int = 150):
        self.count = count
        self.chars = string.ascii_letters + string.digits
        self.hex_chars = 'abcdef0123456789'

    def _random_string(self, length: int) -> str:
        return ''.join(random.choices(self.chars, k=length))

    def _random_hex(self, length: int) -> str:
        return ''.join(random.choices(self.hex_chars, k=length))

    def _b64_encode(self, data: dict) -> str:
        """模拟 base64 编码（不带 padding，URL 安全）"""
        json_str = json.dumps(data, separators=(',', ':'))
        b64 = base64.urlsafe_b64encode(json_str.encode()).decode('utf-8')
        return b64.rstrip('=')

    def _generate_traditional_token(self) -> str:
        """传统 Token：如 32位 hex 或 UUID 风格"""
        return random.choice([
            self._random_hex(32),  # 32位十六进制
            self._random_string(32),  # 随机32字符
            f"{self._random_hex(8)}-{self._random_hex(4)}-{self._random_hex(4)}-{self._random_hex(4)}-{self._random_hex(12)}",
            # 模拟 UUID
        ])

    def _generate_jwt_token(self) -> str:
        """生成模拟 JWT Token（结构正确但内容虚假）"""
        header = {"alg": random.choice(["HS256", "HS512", "RS256"]), "typ": "JWT"}
        payload = {
            "sub": self._random_string(random.randint(8, 16)),
            "exp": random.randint(1700000000, 2000000000),
            "iat": random.randint(1600000000, 1700000000),
            "jti": self._random_string(16),
            "scope": random.choice(["read", "write", "admin", "user"]),
        }
        signature = self._random_string(43)  # 模拟签名长度

        enc_header = self._b64_encode(header)
        enc_payload = self._b64_encode(payload)

        return f"{enc_header}.{enc_payload}.{signature}"

    def _generate_oauth_token(self) -> str:
        """生成 OAuth 风格 Bearer Token"""
        return random.choice([
            self._random_string(32),
            self._random_string(40),
            self._random_string(64),
            f"token_{self._random_string(24)}",
            f"access_{self._random_string(32)}",
            f"oauth2:{self._random_string(30)}",
            f"sk-{self._random_string(32)}",  # 模拟 Stripe 风格密钥
        ])

    def generate(self) -> List[str]:
        logger.info("🔄 开始生成多种 Token 风格弱密码（传统/_jwt/OAuth）...")
        tokens = set()

        # 各类型比例（可调整）
        traditional_ratio = 0.3
        jwt_ratio = 0.4
        oauth_ratio = 0.3

        num_traditional = int(self.count * traditional_ratio)
        num_jwt = int(self.count * jwt_ratio)
        num_oauth = self.count - num_traditional - num_jwt  # 补足

        # 生成传统 Token
        for _ in range(num_traditional):
            tokens.add(self._generate_traditional_token())

        # 生成 JWT
        for _ in range(num_jwt):
            tokens.add(self._generate_jwt_token())

        # 生成 OAuth Token
        for _ in range(num_oauth):
            tokens.add(self._generate_oauth_token())

        logger.success(f"✅ 多种 Token 风格生成完成，共 {len(tokens)} 条")
        return list(tokens)


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


class NormalCodeGenerator:
    """
    生成正常的代码片段（非敏感），支持主流编程语言（C/C++/Python/Java）
    每条输出为一行常见代码语句，用于模拟正常开发内容
    """

    def __init__(self, count: int = 1000):
        self.count = count
        self.languages = {
            'python': self._generate_python,
            'java': self._generate_java,
            'c': self._generate_c,
            'cpp': self._generate_cpp,
        }

    def _generate_python(self) -> str:
        return random.choice([
            'def hello_world():',
            'print("Hello, World!")',
            'import os',
            'from datetime import datetime',
            'for i in range(10):',
            'if condition:',
            'return response.json()',
            'try:',
            'except Exception as e:',
            'with open("file.txt", "r") as f:',
            'class User(models.Model):',
            'def __init__(self, name):',
            'self.name = name',
            'data = [x for x in range(100)]',
            'logging.info("Process started")',
        ])

    def _generate_java(self) -> str:
        return random.choice([
            'public class Main {',
            'public static void main(String[] args) {',
            'System.out.println("Hello, World!");',
            'int count = 0;',
            'for (int i = 0; i < 10; i++) {',
            'if (status == true) {',
            'String message = "success";',
            'private String username;',
            'public User getUser() {',
            '} // end of method',
            'try {',
            '} catch (Exception e) {',
            '@Override',
            'import java.util.List;',
            'public class UserService {',
        ])

    def _generate_c(self) -> str:
        return random.choice([
            '#include <stdio.h>',
            'int main() {',
            'printf("Hello, World\\n");',
            'return 0;',
            '}',
            'int sum = 0;',
            'for (int i = 0; i < n; i++) {',
            'if (flag == 1) {',
            'void calculate();',
            'static int counter = 0;',
            'while (running) {',
            '#define MAX_SIZE 1024',
            'char buffer[256];',
            'fclose(fp);',
            'return -1;',
        ])

    def _generate_cpp(self) -> str:
        return random.choice([
            '#include <iostream>',
            'using namespace std;',
            'class Animal {',
            'virtual void speak() = 0;',
            'std::string name;',
            'public:',
            'private:',
            'void Dog::bark() {',
            'std::cout << "Woof!" << std::endl;',
            'std::vector<int> numbers;',
            'auto it = list.begin();',
            'try {',
            '} catch (const std::exception& e) {',
            'unique_ptr<Resource> res;',
            'shared_mutex mutex;',
        ])

    def generate(self) -> List[str]:
        logger.info(f"🔄 开始生成正常代码片段（非敏感），目标 {self.count} 条...")
        code_lines = []

        for _ in range(self.count):
            lang = random.choice(list(self.languages.keys()))
            line = self.languages[lang]()
            code_lines.append(line)

        logger.success(f"✅ 正常代码片段生成完成，共 {len(code_lines)} 条")
        return code_lines


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


def main():
    generator = SensitiveDataGenerator(output_path=GENERATE_DATA_PATH)
    generator.add_password_style(CommonWeakPassword(count=1000))
    generator.add_password_style(HuaweiStylePassword(count=1000))
    generator.add_password_style(TokenStylePassword(count=1000))
    generator.add_password_style(DjangoTokenStylePassword(count=1000))  # 添加 Django Token 风格

    generator.generate_dataset()


if __name__ == "__main__":
    main()
