# 打包模块使用说明

## 概述

项目已重新整理打包功能，所有打包相关代码现在统一存放在 `src/package` 目录下，并提供一键式打包入口。

## 目录结构

```
src/package/
├── __init__.py              # 模块导出接口
├── package_config.py        # 打包配置
├── builder.py              # 核心构建器
├── platform_builders.py    # 平台特定构建器
└── package_manager.py      # 包管理器
```

## 使用方法

### 一键式构建

#### Windows用户：
```bash
# 构建当前平台
build.bat

# 跨平台构建
build.bat cross

# 清理spec文件
build.bat cleanspec

# 显示帮助
build.bat help
```

#### Linux/macOS用户：
```bash
# 构建当前平台
./build.sh

# 跨平台构建
./build.sh cross

# 清理spec文件
./build.sh cleanspec

# 显示帮助
./build.sh help
```

### Python命令行

```bash
# 构建当前平台
python build.py

# 跨平台构建
python build.py cross

# 显示模块信息
python build.py info

# 清理旧包
python build.py clean

# 清理spec文件
python build.py cleanspec

# 列出已构建包
python build.py list

# 显示帮助
python build.py help
```

### 程序化使用

```python
from src.package import PackageManager, PackageConfig

# 创建包管理器
manager = PackageManager()

# 构建当前平台
summary = manager.build_current_platform()

# 跨平台构建
summary = manager.build_cross_platform()

# 创建发布包
package_path = manager.create_release_package("windows", "x86_64", "zip")
```

## 主要功能

### 1. 跨平台支持
- **Windows**: 生成 `.exe` 可执行文件
- **Linux**: 生成可执行二进制文件
- **macOS**: 生成可执行二进制文件

### 2. 智能配置
- 自动检测平台和架构
- 预配置隐藏导入模块
- 包含必要的数据文件

### 3. 包管理
- 版本管理
- 自动清理旧包
- 发布包创建（ZIP/TAR格式）

### 4. 日志记录
- 详细的构建日志
- 按日期轮转
- 错误诊断信息

### 5. 文件管理
- **Spec文件管理**: 所有PyInstaller生成的.spec文件自动存放到`build/`目录
- **清理功能**: 支持清理旧的spec文件和构建产物
- **版本管理**: 自动管理不同版本的构建产物

## 输出结构

构建完成后，文件将输出到：
```
build/                          # 构建中间文件
├── generate_data.spec          # PyInstaller配置文件
├── train_model.spec
├── predict.spec
└── 子目录/                     # 构建中间文件

dist/
├── windows-x86_64/             # Windows平台构建结果
│   ├── generate_data.exe
│   ├── train_model.exe
│   ├── predict.exe
│   ├── config.py
│   ├── README.md
│   ├── requirements.txt
│   ├── data/                   # 数据目录
│   ├── models/                 # 模型目录
│   └── logs/                   # 日志目录
└── linux-x86_64/               # Linux平台构建结果
    └── ...
```

## 配置定制

如需自定义配置，可修改 `src/package/package_config.py`：

```python
class PackageConfig:
    # 项目信息
    PROJECT_NAME = "hello-scikit-learn"
    PROJECT_VERSION = "0.1.0"
    
    # 主要脚本
    MAIN_SCRIPTS = [
        "generate_data.py",
        "train_model.py", 
        "predict.py"
    ]
    
    # 其他配置...
```

## 故障排除

### 1. 导入错误
如果遇到模块导入错误，检查：
- Python路径是否正确
- 所有依赖是否已安装
- 隐藏导入配置是否完整

### 2. 构建失败
查看日志文件：
```
logs/build_windows_x86_64_YYYY-MM-DD.log
logs/package_manager_YYYY-MM-DD.log
```

### 3. 依赖问题
确保安装了所有必要依赖：
```bash
pip install -r requirements.txt
```

## 扩展功能

### 添加新脚本
在 `PackageConfig.MAIN_SCRIPTS` 中添加新的脚本文件名。

### 平台特定优化
继承 `BaseBuilder` 类创建自定义构建器：

```python
from src.package.builder import BaseBuilder

class CustomBuilder(BaseBuilder):
    def build_single_executable(self, script_name):
        # 自定义构建逻辑
        return super().build_single_executable(script_name)
```

### 新的包格式
在 `PackageManager` 中添加新的包格式支持。

## 注意事项

1. **内存要求**: PyInstaller打包需要足够的内存空间
2. **防病毒软件**: 可能会误报打包后的可执行文件
3. **文件大小**: 单文件模式会产生较大的可执行文件
4. **权限**: Linux/macOS需要设置执行权限

## 版本历史

- **v0.1.0**: 初始版本，支持基础打包功能
  - 跨平台构建
  - 包管理
  - 一键式操作
  - 日志记录