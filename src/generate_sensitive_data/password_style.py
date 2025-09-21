"""Password style classes for sensitive data generation"""
import base64
import json
import random
import string
from abc import ABC, abstractmethod
from typing import List

from loguru import logger


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
