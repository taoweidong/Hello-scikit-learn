#!/usr/bin/env python3
"""
核心构建器模块
提供通用的构建功能和接口
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from loguru import logger

from .package_config import PackageConfig


class BuildResult:
    """构建结果类"""
    
    def __init__(self, script_name: str, success: bool, error_message: Optional[str] = None):
        self.script_name = script_name
        self.success = success
        self.error_message = error_message
        self.executable_path: Optional[str] = None
    
    def __repr__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.script_name}: {'成功' if self.success else self.error_message}"


class BaseBuilder:
    """基础构建器"""
    
    def __init__(self, config: Optional[PackageConfig] = None):
        self.config = config or PackageConfig()
        self.platform_name, self.arch = self._get_platform_info()
        
        # 配置日志
        logger.add(
            f"logs/build_{self.platform_name}_{self.arch}_{{time:YYYY-MM-DD}}.log",
            rotation="1 day",
            level="INFO"
        )
    
    def _get_platform_info(self) -> Tuple[str, str]:
        """获取平台信息"""
        system = platform.system().lower()
        arch = platform.machine().lower()
        
        if system == "windows":
            return "windows", arch
        elif system == "linux":
            return "linux", arch
        elif system == "darwin":
            return "macos", arch
        else:
            return system, arch
    
    def clean_build_dirs(self) -> None:
        """清理构建目录"""
        dirs_to_clean = [
            self.config.DIST_DIR,
            self.config.TEMP_DIR
        ]
        
        # 清理dist和temp目录，但保留build目录结构
        for dir_name in dirs_to_clean:
            if os.path.exists(dir_name):
                logger.info(f"清理目录: {dir_name}")
                shutil.rmtree(dir_name)
        
        # 清理build目录中的子目录，但保留目录结构用于存放spec文件
        if os.path.exists(self.config.BUILD_DIR):
            for item in os.listdir(self.config.BUILD_DIR):
                item_path = os.path.join(self.config.BUILD_DIR, item)
                if os.path.isdir(item_path):
                    logger.info(f"清理构建子目录: {item_path}")
                    shutil.rmtree(item_path)
                elif item.endswith('.spec'):
                    # 保留spec文件，不删除
                    logger.debug(f"保留spec文件: {item_path}")
        
        # 重新创建必要目录
        os.makedirs(self.config.DIST_DIR, exist_ok=True)
        os.makedirs(self.config.BUILD_DIR, exist_ok=True)
        logger.info("构建目录清理完成")
    
    def install_dependencies(self) -> bool:
        """安装构建依赖"""
        try:
            logger.info("安装构建依赖...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            logger.success("依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"依赖安装失败: {e}")
            return False
    
    def validate_environment(self) -> bool:
        """验证构建环境"""
        logger.info("验证构建环境...")
        
        # 检查配置
        if not self.config.validate_environment():
            logger.error("环境验证失败")
            return False
        
        # 检查PyInstaller
        try:
            subprocess.check_call(
                ["pyinstaller", "--version"], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("PyInstaller 未安装或不可用")
            return False
        
        logger.success("环境验证通过")
        return True
    
    def build_single_executable(self, script_name: str) -> BuildResult:
        """构建单个可执行文件"""
        script_path = Path(script_name)
        exe_name = script_path.stem
        
        logger.info(f"开始构建 {exe_name}...")
        
        # 生成构建命令
        cmd = self.config.get_build_command(script_name, self.platform_name, self.arch)
        
        try:
            # 执行构建
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            # 检查输出文件是否存在
            platform_config = self.config.get_platform_config(self.platform_name)
            executable_name = exe_name + platform_config["executable_suffix"]
            executable_path = Path(self.config.DIST_DIR) / f"{self.platform_name}-{self.arch}" / executable_name
            
            if executable_path.exists():
                build_result = BuildResult(script_name, True)
                build_result.executable_path = str(executable_path)
                logger.success(f"✅ {exe_name} 构建成功: {executable_path}")
                return build_result
            else:
                return BuildResult(script_name, False, f"输出文件未找到: {executable_path}")
        
        except subprocess.CalledProcessError as e:
            error_msg = f"构建失败: {e.stderr if e.stderr else str(e)}"
            logger.error(f"❌ {exe_name} {error_msg}")
            return BuildResult(script_name, False, error_msg)
    
    def build_all_executables(self) -> List[BuildResult]:
        """构建所有可执行文件"""
        logger.info(f"🔧 开始构建 {self.config.PROJECT_NAME}")
        logger.info(f"检测到平台: {self.platform_name}-{self.arch}")
        
        results = []
        
        # 清理构建目录
        self.clean_build_dirs()
        
        # 验证环境
        if not self.validate_environment():
            return [BuildResult("环境验证", False, "环境验证失败")]
        
        # 安装依赖
        if not self.install_dependencies():
            return [BuildResult("依赖安装", False, "依赖安装失败")]
        
        # 构建所有脚本
        for script in self.config.MAIN_SCRIPTS:
            if os.path.exists(script):
                result = self.build_single_executable(script)
                results.append(result)
            else:
                logger.warning(f"脚本文件 {script} 不存在，跳过")
                results.append(BuildResult(script, False, "文件不存在"))
        
        return results
    
    def create_distribution_package(self) -> bool:
        """创建分发包"""
        dist_platform_dir = Path(self.config.DIST_DIR) / f"{self.platform_name}-{self.arch}"
        
        if not dist_platform_dir.exists():
            logger.warning(f"分发目录 {dist_platform_dir} 不存在")
            return False
        
        logger.info("创建分发包...")
        
        # 复制配置和说明文件
        for file_name in self.config.DISTRIBUTION_FILES:
            if os.path.exists(file_name):
                shutil.copy2(file_name, dist_platform_dir)
                logger.debug(f"复制文件: {file_name}")
        
        # 创建必要目录
        for dir_name in self.config.REQUIRED_DIRS:
            target_dir = dist_platform_dir / dir_name
            target_dir.mkdir(exist_ok=True)
            logger.debug(f"创建目录: {target_dir}")
        
        logger.success(f"✅ 分发包创建完成: {dist_platform_dir}")
        return True
    
    def get_build_summary(self, results: List[BuildResult]) -> Dict[str, Any]:
        """获取构建摘要"""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        return {
            "platform": f"{self.platform_name}-{self.arch}",
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "successful_builds": [r.script_name for r in successful],
            "failed_builds": [(r.script_name, r.error_message) for r in failed],
            "output_directory": f"{self.config.DIST_DIR}/{self.platform_name}-{self.arch}"
        }