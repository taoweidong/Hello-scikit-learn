"""Normal code generator for sensitive data generation"""
import random
from typing import List

from loguru import logger


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