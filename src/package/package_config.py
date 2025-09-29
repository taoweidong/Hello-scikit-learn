#!/usr/bin/env python3
"""
打包配置模块
定义项目打包的各种配置参数
"""

import os
from pathlib import Path
from typing import List, Dict, Any


class PackageConfig:
    """打包配置类"""
    
    # 项目基本信息
    PROJECT_NAME = "hello-scikit-learn"
    PROJECT_VERSION = "0.1.0"
    
    # 主要脚本文件
    MAIN_SCRIPTS = [
        "generate_data.py",
        "train_model.py", 
        "predict.py"
    ]
    
    # 构建目录配置
    BUILD_DIR = "build"
    DIST_DIR = "dist"
    TEMP_DIR = "temp"
    
    # PyInstaller基础配置
    PYINSTALLER_BASE_OPTIONS = [
        "--onefile",      # 单文件模式
        "--clean",        # 清理临时文件
        "--noconfirm",    # 不询问确认
    ]
    
    # 隐藏导入模块列表
    HIDDEN_IMPORTS = [
        "sklearn.utils._cython_blas",
        "sklearn.neighbors.typedefs", 
        "sklearn.neighbors.quad_tree",
        "sklearn.tree._utils",
        "pandas._libs.tslibs.timedeltas",
        "jieba",
        "loguru",
        "openpyxl",
        "numpy",
        "scipy",
        "joblib"
    ]
    
    # 需要包含的数据文件和目录
    INCLUDE_DATA = [
        ("src", "src"),
        ("config.py", "."),
    ]
    
    # 需要复制到分发包的额外文件
    DISTRIBUTION_FILES = [
        "config.py",
        "README.md", 
        "requirements.txt"
    ]
    
    # 需要创建的目录
    REQUIRED_DIRS = [
        "data",
        "models", 
        "logs"
    ]
    
    @classmethod
    def get_platform_config(cls, platform: str) -> Dict[str, Any]:
        """获取平台特定配置"""
        platform_configs = {
            "windows": {
                "console": True,
                "executable_suffix": ".exe",
                "additional_options": ["--console"]
            },
            "linux": {
                "console": True,
                "executable_suffix": "",
                "additional_options": []
            },
            "macos": {
                "console": True,
                "executable_suffix": "",
                "additional_options": []
            }
        }
        
        return platform_configs.get(platform, platform_configs["linux"])
    
    @classmethod
    def get_build_command(cls, script_name: str, platform: str, arch: str) -> List[str]:
        """生成PyInstaller构建命令"""
        script_path = Path(script_name)
        exe_name = script_path.stem
        platform_config = cls.get_platform_config(platform)
        
        # 基础命令
        cmd = ["pyinstaller"] + cls.PYINSTALLER_BASE_OPTIONS
        
        # 输出配置
        cmd.extend([
            f"--distpath={cls.DIST_DIR}/{platform}-{arch}",
            f"--workpath={cls.BUILD_DIR}/{exe_name}",
            f"--specpath={cls.BUILD_DIR}",  # 指定spec文件存放目录
            f"--name={exe_name}",
        ])
        
        # 平台特定选项
        cmd.extend(platform_config["additional_options"])
        
        # 隐藏导入
        for imp in cls.HIDDEN_IMPORTS:
            cmd.extend(["--hidden-import", imp])
        
        # 包含数据文件
        for src, dst in cls.INCLUDE_DATA:
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dst}"])
        
        # 脚本文件
        cmd.append(script_name)
        
        return cmd
    
    @classmethod
    def validate_environment(cls) -> bool:
        """验证构建环境"""
        # 检查必要的脚本文件是否存在
        for script in cls.MAIN_SCRIPTS:
            if not os.path.exists(script):
                print(f"警告: 脚本文件 {script} 不存在")
                return False
        
        # 检查源代码目录
        if not os.path.exists("src"):
            print("错误: src 目录不存在")
            return False
        
        return True