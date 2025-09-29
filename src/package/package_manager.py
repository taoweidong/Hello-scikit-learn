#!/usr/bin/env python3
"""
包管理器模块
提供高级的打包管理功能，包括版本管理、发布等
"""

import os
import json
import shutil
import zipfile
import tarfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from loguru import logger

from .builder import BuildResult
from .platform_builders import BuilderFactory, CrossPlatformBuilder
from .package_config import PackageConfig


class PackageMetadata:
    """包元数据类"""
    
    def __init__(self, name: str, version: str, platform: str, arch: str):
        self.name = name
        self.version = version
        self.platform = platform
        self.arch = arch
        self.build_time = datetime.now().isoformat()
        self.build_info: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "platform": self.platform,
            "arch": self.arch,
            "build_time": self.build_time,
            "build_info": self.build_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageMetadata':
        """从字典创建"""
        metadata = cls(
            data["name"],
            data["version"], 
            data["platform"],
            data["arch"]
        )
        metadata.build_time = data.get("build_time", metadata.build_time)
        metadata.build_info = data.get("build_info", {})
        return metadata


class PackageManager:
    """包管理器主类"""
    
    def __init__(self, config: Optional[PackageConfig] = None):
        self.config = config or PackageConfig()
        self.packages_dir = Path("packages")
        self.packages_dir.mkdir(exist_ok=True)
        
        # 初始化日志
        logger.add(
            f"logs/package_manager_{{time:YYYY-MM-DD}}.log",
            rotation="1 day",
            level="INFO"
        )
        
        logger.info("包管理器初始化完成")
    
    def build_current_platform(self) -> Dict[str, Any]:
        """构建当前平台的包"""
        logger.info("开始构建当前平台包...")
        
        builder = BuilderFactory.create_builder(config=self.config)
        results = builder.build_all_executables()
        
        # 创建分发包
        builder.create_distribution_package()
        
        # 获取构建摘要
        summary = builder.get_build_summary(results)
        
        # 保存元数据
        metadata = PackageMetadata(
            self.config.PROJECT_NAME,
            self.config.PROJECT_VERSION,
            summary["platform"].split("-")[0],
            summary["platform"].split("-")[1]
        )
        metadata.build_info = summary
        
        self._save_metadata(metadata)
        
        logger.success(f"当前平台构建完成: {summary['platform']}")
        return summary
    
    def build_cross_platform(self, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """跨平台构建"""
        logger.info("开始跨平台构建...")
        
        cross_builder = CrossPlatformBuilder(self.config)
        
        if platforms:
            # 构建指定平台
            all_results = {}
            for platform in platforms:
                all_results[platform] = cross_builder.build_for_platform(platform)
        else:
            # 构建所有平台
            all_results = cross_builder.build_for_all_platforms()
        
        # 获取跨平台摘要
        summary = cross_builder.get_cross_platform_summary(all_results)
        
        # 保存所有平台的元数据
        for platform, results in all_results.items():
            if any(r.success for r in results):
                platform_parts = platform.split("-") if "-" in platform else [platform, "unknown"]
                metadata = PackageMetadata(
                    self.config.PROJECT_NAME,
                    self.config.PROJECT_VERSION,
                    platform_parts[0],
                    platform_parts[1] if len(platform_parts) > 1 else "unknown"
                )
                metadata.build_info = {
                    "results": [{"script": r.script_name, "success": r.success} for r in results]
                }
                self._save_metadata(metadata)
        
        logger.success("跨平台构建完成")
        return summary
    
    def create_release_package(self, platform: str, arch: str, format: str = "zip") -> Optional[str]:
        """创建发布包"""
        logger.info(f"创建 {platform}-{arch} 发布包...")
        
        dist_dir = Path(self.config.DIST_DIR) / f"{platform}-{arch}"
        if not dist_dir.exists():
            logger.error(f"分发目录不存在: {dist_dir}")
            return None
        
        # 创建发布包
        release_name = f"{self.config.PROJECT_NAME}-{self.config.PROJECT_VERSION}-{platform}-{arch}"
        release_dir = self.packages_dir / release_name
        
        if format.lower() == "zip":
            package_path = f"{release_dir}.zip"
            self._create_zip_package(dist_dir, package_path)
        elif format.lower() in ["tar", "tar.gz", "tgz"]:
            package_path = f"{release_dir}.tar.gz"
            self._create_tar_package(dist_dir, package_path)
        else:
            logger.error(f"不支持的包格式: {format}")
            return None
        
        logger.success(f"发布包创建完成: {package_path}")
        return package_path
    
    def _create_zip_package(self, source_dir: Path, package_path: str) -> None:
        """创建ZIP包"""
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
    
    def _create_tar_package(self, source_dir: Path, package_path: str) -> None:
        """创建TAR包"""
        with tarfile.open(package_path, 'w:gz') as tarf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    tarf.add(file_path, arcname)
    
    def _save_metadata(self, metadata: PackageMetadata) -> None:
        """保存包元数据"""
        metadata_file = self.packages_dir / f"{metadata.name}-{metadata.version}-{metadata.platform}-{metadata.arch}.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.debug(f"元数据保存: {metadata_file}")
    
    def list_packages(self) -> List[PackageMetadata]:
        """列出所有已构建的包"""
        packages = []
        
        for metadata_file in self.packages_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    packages.append(PackageMetadata.from_dict(data))
            except Exception as e:
                logger.warning(f"读取元数据文件失败 {metadata_file}: {e}")
        
        return packages
    
    def clean_packages(self, keep_latest: int = 5) -> None:
        """清理旧的包文件"""
        logger.info(f"清理包文件，保留最新 {keep_latest} 个...")
        
        packages = self.list_packages()
        
        # 按平台分组
        platform_packages: Dict[str, List[PackageMetadata]] = {}
        for pkg in packages:
            platform_key = f"{pkg.platform}-{pkg.arch}"
            if platform_key not in platform_packages:
                platform_packages[platform_key] = []
            platform_packages[platform_key].append(pkg)
        
        # 每个平台保留最新的几个版本
        for platform_key, pkg_list in platform_packages.items():
            # 按构建时间排序
            pkg_list.sort(key=lambda x: x.build_time, reverse=True)
            
            # 删除旧版本
            for old_pkg in pkg_list[keep_latest:]:
                self._remove_package(old_pkg)
                logger.info(f"删除旧包: {old_pkg.name}-{old_pkg.version}-{old_pkg.platform}-{old_pkg.arch}")
    
    def clean_spec_files(self, keep_latest_only: bool = True) -> None:
        """清理所有位置的spec文件（包括build目录和根目录）"""
        logger.info("清理所有位置的spec文件...")
        
        spec_files_found = False
        
        # 1. 清理build目录中的spec文件
        build_path = Path(self.config.BUILD_DIR)
        if build_path.exists():
            build_spec_files = list(build_path.glob("*.spec"))
            if build_spec_files:
                spec_files_found = True
                logger.info(f"在build目录中找到 {len(build_spec_files)} 个spec文件")
                
                if keep_latest_only:
                    # 按修改时间排序，保留最新的每个脚本的spec文件
                    script_specs: Dict[str, List[Path]] = {}
                    
                    for spec_file in build_spec_files:
                        script_name = spec_file.stem
                        if script_name not in script_specs:
                            script_specs[script_name] = []
                        script_specs[script_name].append(spec_file)
                    
                    # 每个脚本保留最新的spec文件
                    for script_name, files in script_specs.items():
                        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                        # 删除除了最新的之外的所有spec文件
                        for old_spec in files[1:]:
                            old_spec.unlink()
                            logger.info(f"删除旧spec文件: {old_spec}")
                else:
                    # 删除所有spec文件
                    for spec_file in build_spec_files:
                        spec_file.unlink()
                        logger.info(f"删除spec文件: {spec_file}")
        
        # 2. 清理根目录中的spec文件（这些可能是旧的或误放的）
        root_path = Path(".")
        root_spec_files = list(root_path.glob("*.spec"))
        if root_spec_files:
            spec_files_found = True
            logger.warning(f"在根目录中找到 {len(root_spec_files)} 个误放的spec文件，将被清理")
            
            for spec_file in root_spec_files:
                spec_file.unlink()
                logger.info(f"删除根目录spec文件: {spec_file}")
        
        # 3. 清理其他可能的spec文件位置
        for subdir in ["dist", "temp", "packages"]:
            subdir_path = Path(subdir)
            if subdir_path.exists():
                subdir_spec_files = list(subdir_path.rglob("*.spec"))
                if subdir_spec_files:
                    spec_files_found = True
                    logger.warning(f"在{subdir}目录中找到 {len(subdir_spec_files)} 个spec文件，将被清理")
                    
                    for spec_file in subdir_spec_files:
                        spec_file.unlink()
                        logger.info(f"删除{subdir}目录spec文件: {spec_file}")
        
        if not spec_files_found:
            logger.info("未找到任何spec文件")
        
        logger.success("spec文件清理完成")
    
    def _remove_package(self, metadata: PackageMetadata) -> None:
        """删除指定包的所有文件"""
        base_name = f"{metadata.name}-{metadata.version}-{metadata.platform}-{metadata.arch}"
        
        # 删除元数据文件
        metadata_file = self.packages_dir / f"{base_name}.json"
        if metadata_file.exists():
            metadata_file.unlink()
        
        # 删除包文件
        for ext in [".zip", ".tar.gz", ".tgz"]:
            package_file = self.packages_dir / f"{base_name}{ext}"
            if package_file.exists():
                package_file.unlink()
    
    def get_package_info(self, platform: str, arch: str) -> Optional[PackageMetadata]:
        """获取指定平台的包信息"""
        packages = self.list_packages()
        
        for pkg in packages:
            if pkg.platform == platform and pkg.arch == arch:
                return pkg
        
        return None
    
    def create_release_summary(self) -> Dict[str, Any]:
        """创建发布摘要"""
        packages = self.list_packages()
        
        summary = {
            "project_name": self.config.PROJECT_NAME,
            "project_version": self.config.PROJECT_VERSION,
            "total_packages": len(packages),
            "platforms": {},
            "latest_build": None
        }
        
        latest_time = None
        
        for pkg in packages:
            platform_key = f"{pkg.platform}-{pkg.arch}"
            
            if platform_key not in summary["platforms"]:
                summary["platforms"][platform_key] = []
            
            summary["platforms"][platform_key].append({
                "version": pkg.version,
                "build_time": pkg.build_time,
                "build_info": pkg.build_info
            })
            
            # 找到最新构建
            if latest_time is None or pkg.build_time > latest_time:
                latest_time = pkg.build_time
                summary["latest_build"] = {
                    "platform": platform_key,
                    "version": pkg.version,
                    "build_time": pkg.build_time
                }
        
        return summary