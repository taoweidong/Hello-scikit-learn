import random
from typing import List
from loguru import logger


class NormalTextGenerator:
    """
    生成非敏感的英文开发相关普通字符串
    用于模拟变量名、函数名、日志、注释等内容
    """

    def __init__(self, count: int = 1000):
        self.count = count
        self.subjects = [
            'user', 'data', 'config', 'file', 'system', 'service',
            'manager', 'handler', 'processor', 'controller',
            'api', 'request', 'response', 'session', 'token'
        ]
        self.verbs = [
            'get', 'set', 'create', 'update', 'delete', 'find',
            'load', 'save', 'process', 'handle', 'validate', 'check'
        ]
        self.adjectives = [
            'valid', 'invalid', 'success', 'failed', 'pending',
            'active', 'inactive', 'initialized', 'complete', 'error'
        ]
        self.suffixes = [
            '_temp', '_backup', '_copy', '_old', '_new', '_v1', '_v2',
            '_test', '_dev', '_prod', '_staging'
        ]
        self.log_actions = [
            'starting...', 'completed.', 'initialized.', 'shutting down...',
            'retrying...', 'connected.', 'disconnected.', 'timeout.',
            'cached result.', 'cleared cache.'
        ]
        self.comments = [
            'TODO: implement error handling',
            'FIXME: this may cause memory leak',
            'HACK: temporary workaround',
            'Optimization: reduce time complexity',
            'Initialize global config',
            'Validate input parameters',
            'Return default value if null',
            'Log execution time',
            'Skip processing if disabled',
            'Ensure thread safety'
        ]

    def _generate_variable_name(self) -> str:
        subject = random.choice(self.subjects)
        adj = random.choice(self.adjectives)
        suffix = random.choice(self.suffixes) if random.random() > 0.7 else ''
        case_style = random.choice(['lower', 'camel', 'snake'])
        base = f"{adj}{subject.capitalize()}" if case_style == 'camel' else f"{adj}_{subject}"
        if case_style == 'snake':
            base = base.lower()
        return base + suffix

    def _generate_function_call(self) -> str:
        verb = random.choice(self.verbs)
        subject = random.choice(self.subjects).capitalize()
        args = random.choice(['()', '(id)', '(data, timeout)', '(config)'])
        return f"{verb}{subject}{args}"

    def _generate_log_message(self) -> str:
        subject = random.choice(self.subjects).capitalize()
        action = random.choice(self.log_actions)
        return f"{subject} {action}"

    def generate(self) -> List[str]:
        logger.info(f"🔄 开始生成英文普通字符串（非敏感，编码相关），目标 {self.count} 条...")
        texts = []

        generators = [
            self._generate_variable_name,
            self._generate_function_call,
            self._generate_log_message,
            lambda: random.choice(self.comments),
            lambda: f"// {random.choice(self.comments)}",
            lambda: f"# {random.choice(self.comments)}",
            lambda: f"LOG: {random.choice(self.adjectives).capitalize()} state detected."
        ]

        for _ in range(self.count):
            text = random.choice(generators)()
            texts.append(text)

        logger.success(f"✅ 英文普通字符串生成完成，共 {len(texts)} 条")
        return texts
