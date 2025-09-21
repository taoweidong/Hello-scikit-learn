"""Main entry point for generating sensitive data"""
from src.generate_sensitive_data.sensitive_data_generator import SensitiveDataGenerator
from src.generate_sensitive_data.password_style import (
    CommonWeakPassword,
    HuaweiStylePassword,
    TokenStylePassword,
    DjangoTokenStylePassword
)
from config import GENERATE_DATA_PATH


def main():
    generator = SensitiveDataGenerator(output_path=GENERATE_DATA_PATH)
    generator.add_password_style(CommonWeakPassword(count=1000))
    generator.add_password_style(HuaweiStylePassword(count=1000))
    generator.add_password_style(TokenStylePassword(count=1000))
    generator.add_password_style(DjangoTokenStylePassword(count=1000))  # 添加 Django Token 风格

    generator.generate_dataset()


if __name__ == "__main__":
    main()