#!/usr/bin/env python3
"""
一键式打包入口脚本
使用新的打包模块进行构建
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.package import PackageManager, PackageConfig
from loguru import logger


def print_banner():
    """打印横幅信息"""
    print("="*60)
    print("🚀 Hello-scikit-learn 一键式打包工具")
    print("="*60)
    print()


def print_results(summary):
    """打印构建结果"""
    print("\n" + "="*60)
    print("📊 构建结果摘要")
    print("="*60)
    
    if "platform" in summary:
        # 单平台构建结果
        print(f"平台: {summary['platform']}")
        print(f"总计: {summary['total']} 个脚本")
        print(f"成功: {summary['successful']} 个")
        print(f"失败: {summary['failed']} 个")
        print(f"成功率: {summary['success_rate']:.1%}")
        
        if summary['successful_builds']:
            print(f"\n✅ 成功构建的脚本:")
            for script in summary['successful_builds']:
                print(f"  - {script}")
        
        if summary['failed_builds']:
            print(f"\n❌ 失败的脚本:")
            for script, error in summary['failed_builds']:
                print(f"  - {script}: {error}")
        
        print(f"\n📁 输出目录: {summary['output_directory']}")
    
    else:
        # 跨平台构建结果
        print(f"总平台数: {summary['total_platforms']}")
        
        for platform, results in summary['platform_results'].items():
            print(f"\n{platform}:")
            print(f"  成功: {results['successful']}/{results['total']}")
            print(f"  成功率: {results['success_rate']:.1%}")
    
    print("\n" + "="*60)


def main():
    """主函数"""
    # 确保在项目根目录
    if not os.path.exists("src"):
        print("❌ 错误: 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 创建logs目录
    os.makedirs("logs", exist_ok=True)
    
    # 配置日志
    logger.add(
        "logs/build_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    try:
        print_banner()
        
        # 检查命令行参数
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "cross":
                # 跨平台构建
                print("🌍 开始跨平台构建...")
                manager = PackageManager()
                summary = manager.build_cross_platform()
                print_results(summary)
                
            elif command == "info":
                # 显示模块信息
                from src.package import print_module_info
                print_module_info()
                return
                
            elif command == "clean":
                # 清理包文件
                print("🧹 清理旧的包文件...")
                manager = PackageManager()
                manager.clean_packages()
                print("✅ 清理完成")
                return
                
            elif command == "cleanspec":
                # 清理spec文件
                print("🧹 清理build目录中的spec文件...")
                manager = PackageManager()
                manager.clean_spec_files()
                print("✅ spec文件清理完成")
                return
                
            elif command == "list":
                # 列出已构建的包
                print("📦 已构建的包:")
                manager = PackageManager()
                packages = manager.list_packages()
                
                if not packages:
                    print("暂无已构建的包")
                else:
                    for pkg in packages:
                        print(f"  {pkg.name}-{pkg.version}-{pkg.platform}-{pkg.arch} ({pkg.build_time})")
                return
                
            elif command in ["help", "-h", "--help"]:
                print("使用方法:")
                print("  python build.py           # 构建当前平台")
                print("  python build.py cross     # 跨平台构建")
                print("  python build.py info      # 显示模块信息")
                print("  python build.py clean     # 清理旧包")
                print("  python build.py cleanspec # 清理spec文件")
                print("  python build.py list      # 列出已构建包")
                print("  python build.py help      # 显示帮助")
                return
            
            else:
                print(f"❌ 未知命令: {command}")
                print("使用 'python build.py help' 查看帮助")
                sys.exit(1)
        
        else:
            # 默认构建当前平台
            print("🔧 开始构建当前平台...")
            manager = PackageManager()
            summary = manager.build_current_platform()
            print_results(summary)
            
            # 如果构建成功，询问是否创建发布包
            if summary['successful'] > 0:
                try:
                    response = input("\n是否创建发布包? (y/N): ").strip().lower()
                    if response in ['y', 'yes']:
                        platform_parts = summary['platform'].split('-')
                        platform = platform_parts[0]
                        arch = platform_parts[1] if len(platform_parts) > 1 else "unknown"
                        
                        package_path = manager.create_release_package(platform, arch)
                        if package_path:
                            print(f"✅ 发布包创建完成: {package_path}")
                        else:
                            print("❌ 发布包创建失败")
                except KeyboardInterrupt:
                    print("\n操作取消")
    
    except KeyboardInterrupt:
        print("\n\n⏹ 构建被用户中断")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"构建失败: {e}")
        print(f"\n❌ 构建失败: {e}")
        print("请查看日志文件获取详细信息")
        sys.exit(1)


if __name__ == "__main__":
    main()