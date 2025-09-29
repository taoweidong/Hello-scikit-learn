#!/usr/bin/env python3
"""
打包模块初始化文件
导出公共接口类
"""

from .package_config import PackageConfig
from .builder import BaseBuilder, BuildResult
from .platform_builders import (
    WindowsBuilder,
    LinuxBuilder, 
    MacOSBuilder,
    BuilderFactory,
    CrossPlatformBuilder
)
from .package_manager import PackageManager, PackageMetadata

# 版本信息
__version__ = "0.1.0"
__author__ = "Hello-scikit-learn Team"

# 公共接口导出
__all__ = [
    # 配置类
    "PackageConfig",
    
    # 构建器类
    "BaseBuilder",
    "WindowsBuilder", 
    "LinuxBuilder",
    "MacOSBuilder",
    "BuilderFactory",
    "CrossPlatformBuilder",
    
    # 结果和数据类
    "BuildResult",
    "PackageMetadata",
    
    # 管理器类
    "PackageManager",
    
    # 便捷函数
    "build_current_platform",
    "build_cross_platform",
    "create_release_package",
    "clean_spec_files",
]


def build_current_platform(config=None):
    """
    便捷函数：构建当前平台的包
    
    Args:
        config: 可选的PackageConfig实例
        
    Returns:
        构建摘要字典
    """
    manager = PackageManager(config)
    return manager.build_current_platform()


def build_cross_platform(platforms=None, config=None):
    """
    便捷函数：跨平台构建
    
    Args:
        platforms: 要构建的平台列表，None表示构建所有平台
        config: 可选的PackageConfig实例
        
    Returns:
        跨平台构建摘要字典
    """
    manager = PackageManager(config)
    return manager.build_cross_platform(platforms)


def create_release_package(platform, arch, format="zip", config=None):
    """
    便捷函数：创建发布包
    
    Args:
        platform: 目标平台
        arch: 目标架构
        format: 包格式 ("zip" 或 "tar.gz")
        config: 可选的PackageConfig实例
        
    Returns:
        发布包路径
    """
    manager = PackageManager(config)
    return manager.create_release_package(platform, arch, format)


def clean_spec_files(keep_latest_only=True, config=None):
    """
    便捷函数：清理build目录中的spec文件
    
    Args:
        keep_latest_only: 是否只保留最新的spec文件
        config: 可选的PackageConfig实例
    """
    manager = PackageManager(config)
    manager.clean_spec_files(keep_latest_only)


# 模块级别的便捷接口
def get_default_config():
    """获取默认配置"""
    return PackageConfig()


def get_supported_platforms():
    """获取支持的平台列表"""
    return BuilderFactory.get_supported_platforms()


def create_builder(platform=None, config=None):
    """创建构建器实例"""
    return BuilderFactory.create_builder(platform, config)


# 打印模块信息
def print_module_info():
    """打印模块信息"""
    print(f"Hello-scikit-learn 打包模块 v{__version__}")
    print(f"作者: {__author__}")
    print(f"支持平台: {', '.join(get_supported_platforms())}")
    print("\n主要功能:")
    print("- 跨平台PyInstaller打包")
    print("- 平台特定优化")
    print("- 包版本管理")
    print("- 发布包创建")
    print("- 一键式构建")


if __name__ == "__main__":
    print_module_info()