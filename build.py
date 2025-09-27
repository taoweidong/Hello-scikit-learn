#!/usr/bin/env python3
"""
跨平台打包脚本
支持Windows和Linux平台的PyInstaller打包
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# 项目配置
PROJECT_NAME = "hello-scikit-learn"
MAIN_SCRIPTS = [
    "generate_data.py",
    "train_model.py", 
    "predict.py"
]

# 输出目录
DIST_DIR = "dist"
BUILD_DIR = "build"


def get_platform_info():
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


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = [BUILD_DIR, DIST_DIR]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)
            
    # 重新创建目录
    os.makedirs(DIST_DIR, exist_ok=True)


def install_dependencies():
    """安装依赖"""
    print("安装构建依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def build_executable(script_name, platform_name, arch):
    """构建单个可执行文件"""
    script_path = Path(script_name)
    exe_name = script_path.stem
    
    print(f"\n开始构建 {exe_name}...")
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 单文件模式
        "--clean",    # 清理临时文件
        "--noconfirm",  # 不询问确认
        f"--distpath={DIST_DIR}/{platform_name}-{arch}",
        f"--workpath={BUILD_DIR}/{exe_name}",
        f"--name={exe_name}",
        script_name
    ]
    
    # 平台特定配置
    if platform_name == "windows":
        cmd.append("--console")  # Windows控制台应用
    
    # 添加隐藏导入（解决一些模块找不到的问题）
    hidden_imports = [
        "sklearn.utils._cython_blas",
        "sklearn.neighbors.typedefs", 
        "sklearn.neighbors.quad_tree",
        "sklearn.tree._utils",
        "pandas._libs.tslibs.timedeltas",
        "jieba",
        "loguru",
        "openpyxl",
        "numpy",
        "scipy"
    ]
    
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    # 包含数据文件和模块
    cmd.extend([
        "--add-data", f"src{os.pathsep}src",
        "--add-data", f"config.py{os.pathsep}.",
    ])
    
    try:
        subprocess.check_call(cmd)
        print(f"✅ {exe_name} 构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {exe_name} 构建失败: {e}")
        return False


def create_distribution_package(platform_name, arch):
    """创建分发包"""
    dist_platform_dir = Path(DIST_DIR) / f"{platform_name}-{arch}"
    
    if not dist_platform_dir.exists():
        print(f"警告: 分发目录 {dist_platform_dir} 不存在")
        return
    
    # 复制配置和说明文件
    files_to_copy = [
        "config.py",
        "README.md", 
        "requirements.txt"
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, dist_platform_dir)
    
    # 创建示例数据目录
    example_data_dir = dist_platform_dir / "data"
    example_data_dir.mkdir(exist_ok=True)
    
    # 创建模型目录
    models_dir = dist_platform_dir / "models"
    models_dir.mkdir(exist_ok=True)
    
    # 创建日志目录
    logs_dir = dist_platform_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    print(f"✅ 分发包创建完成: {dist_platform_dir}")


def main():
    """主函数"""
    print(f"🔧 开始构建 {PROJECT_NAME}")
    
    # 获取平台信息
    platform_name, arch = get_platform_info()
    print(f"检测到平台: {platform_name}-{arch}")
    
    # 清理构建目录
    clean_build_dirs()
    
    # 安装依赖
    install_dependencies()
    
    # 构建所有脚本
    success_count = 0
    for script in MAIN_SCRIPTS:
        if os.path.exists(script):
            if build_executable(script, platform_name, arch):
                success_count += 1
        else:
            print(f"警告: 脚本文件 {script} 不存在，跳过")
    
    # 创建分发包
    if success_count > 0:
        create_distribution_package(platform_name, arch)
        print(f"\n🎉 构建完成! 成功构建 {success_count}/{len(MAIN_SCRIPTS)} 个执行文件")
        print(f"输出目录: {DIST_DIR}/{platform_name}-{arch}")
    else:
        print(f"\n❌ 构建失败! 没有成功构建任何执行文件")
        sys.exit(1)


if __name__ == "__main__":
    main()