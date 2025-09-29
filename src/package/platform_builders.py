#!/usr/bin/env python3
"""
平台特定构建器模块
为不同平台提供专门的构建实现
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

from .builder import BaseBuilder, BuildResult
from .package_config import PackageConfig


class WindowsBuilder(BaseBuilder):
    """Windows平台构建器"""
    
    def __init__(self, config: Optional[PackageConfig] = None):
        super().__init__(config)
        logger.info("初始化Windows构建器")
    
    def build_single_executable(self, script_name: str) -> BuildResult:
        """Windows特定的构建逻辑"""
        logger.info(f"使用Windows构建器构建 {script_name}")
        
        # 添加Windows特定的构建选项
        result = super().build_single_executable(script_name)
        
        if result.success and result.executable_path:
            # Windows后处理：可以添加签名、图标等
            self._post_process_windows_executable(result.executable_path)
        
        return result
    
    def _post_process_windows_executable(self, executable_path: str) -> None:
        """Windows可执行文件后处理"""
        logger.debug(f"Windows后处理: {executable_path}")
        # 这里可以添加：
        # - 数字签名
        # - 图标设置
        # - 版本信息
        # - 病毒扫描等
    
    def create_windows_installer(self) -> bool:
        """创建Windows安装包（可选功能）"""
        # 可以集成NSIS或其他安装包制作工具
        logger.info("Windows安装包功能尚未实现")
        return False


class LinuxBuilder(BaseBuilder):
    """Linux平台构建器"""
    
    def __init__(self, config: Optional[PackageConfig] = None):
        super().__init__(config)
        logger.info("初始化Linux构建器")
    
    def build_single_executable(self, script_name: str) -> BuildResult:
        """Linux特定的构建逻辑"""
        logger.info(f"使用Linux构建器构建 {script_name}")
        
        result = super().build_single_executable(script_name)
        
        if result.success and result.executable_path:
            # Linux后处理：设置执行权限
            self._post_process_linux_executable(result.executable_path)
        
        return result
    
    def _post_process_linux_executable(self, executable_path: str) -> None:
        """Linux可执行文件后处理"""
        logger.debug(f"Linux后处理: {executable_path}")
        
        # 设置执行权限
        try:
            os.chmod(executable_path, 0o755)
            logger.debug(f"设置执行权限: {executable_path}")
        except Exception as e:
            logger.warning(f"设置执行权限失败: {e}")
    
    def create_deb_package(self) -> bool:
        """创建Debian包（可选功能）"""
        logger.info("Debian包功能尚未实现")
        return False
    
    def create_rpm_package(self) -> bool:
        """创建RPM包（可选功能）"""
        logger.info("RPM包功能尚未实现")
        return False


class MacOSBuilder(BaseBuilder):
    """macOS平台构建器"""
    
    def __init__(self, config: Optional[PackageConfig] = None):
        super().__init__(config)
        logger.info("初始化macOS构建器")
    
    def build_single_executable(self, script_name: str) -> BuildResult:
        """macOS特定的构建逻辑"""
        logger.info(f"使用macOS构建器构建 {script_name}")
        
        result = super().build_single_executable(script_name)
        
        if result.success and result.executable_path:
            # macOS后处理
            self._post_process_macos_executable(result.executable_path)
        
        return result
    
    def _post_process_macos_executable(self, executable_path: str) -> None:
        """macOS可执行文件后处理"""
        logger.debug(f"macOS后处理: {executable_path}")
        
        # 设置执行权限
        try:
            os.chmod(executable_path, 0o755)
            logger.debug(f"设置执行权限: {executable_path}")
        except Exception as e:
            logger.warning(f"设置执行权限失败: {e}")
    
    def create_app_bundle(self) -> bool:
        """创建macOS应用包（可选功能）"""
        logger.info("macOS应用包功能尚未实现")
        return False
    
    def create_dmg_installer(self) -> bool:
        """创建DMG安装包（可选功能）"""
        logger.info("DMG安装包功能尚未实现")
        return False


class BuilderFactory:
    """构建器工厂类"""
    
    @staticmethod
    def create_builder(platform: Optional[str] = None, config: Optional[PackageConfig] = None) -> BaseBuilder:
        """根据平台创建对应的构建器"""
        
        if platform is None:
            import platform as plt
            platform = plt.system().lower()
        
        platform = platform.lower()
        
        if platform == "windows":
            return WindowsBuilder(config)
        elif platform == "linux":
            return LinuxBuilder(config)
        elif platform == "darwin":
            return MacOSBuilder(config)
        else:
            logger.warning(f"未知平台 {platform}，使用默认构建器")
            return BaseBuilder(config)
    
    @staticmethod
    def get_supported_platforms() -> List[str]:
        """获取支持的平台列表"""
        return ["windows", "linux", "darwin"]


class CrossPlatformBuilder:
    """跨平台构建器（用于CI/CD环境）"""
    
    def __init__(self, config: Optional[PackageConfig] = None):
        self.config = config or PackageConfig()
        self.builders: Dict[str, BaseBuilder] = {}
        
        # 初始化所有平台的构建器
        for platform in BuilderFactory.get_supported_platforms():
            try:
                self.builders[platform] = BuilderFactory.create_builder(platform, config)
            except Exception as e:
                logger.warning(f"无法初始化 {platform} 构建器: {e}")
    
    def build_for_platform(self, platform: str) -> List[BuildResult]:
        """为指定平台构建"""
        if platform not in self.builders:
            logger.error(f"平台 {platform} 不支持")
            return [BuildResult("平台检查", False, f"不支持的平台: {platform}")]
        
        builder = self.builders[platform]
        return builder.build_all_executables()
    
    def build_for_all_platforms(self) -> Dict[str, List[BuildResult]]:
        """为所有支持的平台构建"""
        results = {}
        
        for platform in self.builders.keys():
            logger.info(f"开始为 {platform} 平台构建...")
            results[platform] = self.build_for_platform(platform)
        
        return results
    
    def get_cross_platform_summary(self, all_results: Dict[str, List[BuildResult]]) -> Dict[str, Any]:
        """获取跨平台构建摘要"""
        summary = {
            "platforms": list(all_results.keys()),
            "total_platforms": len(all_results),
            "platform_results": {}
        }
        
        for platform, results in all_results.items():
            successful = [r for r in results if r.success]
            failed = [r for r in results if not r.success]
            
            summary["platform_results"][platform] = {
                "total": len(results),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": len(successful) / len(results) if results else 0
            }
        
        return summary