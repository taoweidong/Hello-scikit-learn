# Hello Scikit-learn 项目

一个基于机器学习的敏感信息检测项目，采用面向对象编程（OOP）设计，集成了现代化的打包和部署解决方案。

## 🌟 项目特色

- 🔍 **智能检测**: 使用朴素贝叶斯算法检测敏感信息
- 🏗️ **模块化设计**: 面向对象架构，易于维护和扩展
- 📦 **一键打包**: 支持跨平台（Windows/Linux/macOS）可执行文件打包
- 📊 **完整日志**: 使用loguru提供详细的日志记录
- 🔄 **数据生成**: 内置多种敏感数据生成器
- 🎯 **生产就绪**: 支持训练、预测、部署的完整流程

---

## 📁 项目结构

```
hello-scikit-learn/
│
├── src/                         # 核心源代码目录
│   ├── __init__.py
│   ├── trainer.py                # 模型训练器
│   ├── predictor.py              # 模型预测器
│   ├── generate_sensitive_data/   # 数据生成模块
│   │   ├── __init__.py
│   │   ├── sensitive_data_generator.py
│   │   ├── password_style.py
│   │   ├── normal_text_generator.py
│   │   └── normal_code_generator.py
│   └── package/                  # 打包系统模块
│       ├── __init__.py
│       ├── package_config.py
│       ├── builder.py
│       ├── platform_builders.py
│       └── package_manager.py
│
├── models/                      # 模型存储目录
├── data/                        # 训练数据目录
├── logs/                        # 日志文件目录
├── build/                       # 构建中间文件（包含spec文件）
├── dist/                        # 打包输出目录
├── packages/                    # 发布包目录
│
├── generate_data.py             # 数据生成入口
├── train_model.py               # 模型训练入口
├── predict.py                   # 模型预测入口
│
├── build.py                     # 一键式打包入口
├── build.bat                    # Windows打包脚本
├── build.sh                     # Linux/macOS打包脚本
│
├── config.py                    # 项目配置文件
├── requirements.txt             # Python依赖列表
├── pyproject.toml               # 项目元数据
└── README.md                    # 项目说明文档
```

---

## 🚀 快速开始

### 1. 环境准备

**系统要求:**
- Python 3.10+
- 内存: 4GB+
- 硬盘空间: 2GB+

**安装依赖:**
```bash
pip install -r requirements.txt
```

### 2. 数据准备

生成训练数据：
```bash
python generate_data.py
```

### 3. 模型训练

训练敏感信息检测模型：
```bash
python train_model.py
```

### 4. 预测测试

执行预测测试：
```bash
python predict.py
```

---

## 🛠️ 技术架构

### 核心组件

| 组件 | 文件 | 说明 |
|------|------|------|
| **数据生成器** | `src/generate_sensitive_data/` | 生成多种类型的敏感/非敏感数据 |
| **模型训练器** | `src/trainer.py` | 负责数据加载、模型训练和评估 |
| **模型预测器** | `src/predictor.py` | 负责加载模型并执行预测 |
| **打包系统** | `src/package/` | 跨平台打包和部署管理 |

### 机器学习流程

1. **数据生成**: 使用内置生成器创建训练数据
2. **特征提取**: TF-IDF向量化（ngram_range=(1,2)）
3. **模型训练**: 朴素贝叶斯分类器
4. **模型评估**: 准确率、精准率、召回率等指标
5. **模型保存**: 支持版本管理和历史备份

---

## 📦 一键式打包系统

项目集成了先进的跨平台打包系统，支持将Python项目打包为可独立运行的可执行文件。

### 打包命令

#### Windows 用户：
```cmd
# 一键打包当前平台
build.bat

# 跨平台打包
build.bat cross

# 清理spec文件
build.bat cleanspec

# 显示帮助
build.bat help
```

#### Linux/macOS 用户：
```bash
# 设置执行权限（仅首次）
chmod +x build.sh

# 一键打包当前平台
./build.sh

# 跨平台打包
./build.sh cross

# 清理spec文件
./build.sh cleanspec

# 显示帮助
./build.sh help
```

#### Python 命令行：
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

### 打包输出结构

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

packages/                       # 发布包目录
└── hello-scikit-learn-0.1.0-windows-x86_64.zip
```

### 打包特性

- ✅ **单文件模式**: 每个脚本打包为一个独立的可执行文件
- ✅ **无依赖运行**: 打包后的文件可在没有Python环境的机器上运行
- ✅ **智能配置**: 自动包含所有必要的模块和数据文件
- ✅ **跨平台支持**: 支持Windows、Linux、macOS三大平台
- ✅ **版本管理**: 自动管理不同版本的构建产物
- ✅ **清理功能**: 支持清理旧的spec文件和构建产物

### 使用打包后的程序

1. **运行数据生成：**
   ```bash
   # Windows
   generate_data.exe
   
   # Linux/macOS
   ./generate_data
   ```

2. **运行模型训练：**
   ```bash
   # Windows
   train_model.exe
   
   # Linux/macOS
   ./train_model
   ```

3. **运行预测：**
   ```bash
   # Windows
   predict.exe
   
   # Linux/macOS
   ./predict
   ```

---

## 📊 日志系统

项目使用`loguru`库提供完整的日志记录功能：

- **分级记录**: INFO、WARNING、ERROR、SUCCESS等级别
- **文件轮转**: 每日自动创建新的日志文件
- **控制台输出**: 实时显示关键信息
- **结构化格式**: 时间戳、级别、模块名等

### 日志文件位置

```
logs/
├── train_log_2025-09-29.log      # 训练日志
├── predict_log_2025-09-29.log    # 预测日志
├── build_windows_x86_64_2025-09-29.log  # 构建日志
└── package_manager_2025-09-29.log        # 包管理日志
```

## 🔧 配置管理

项目使用集中式配置管理，主要配置位于`config.py`：

```python
# 数据路径配置
GENERATE_DATA_PATH = "data/sensitive_data.xlsx"
TRAIN_DATA_PATH = "data/train_data.xlsx"

# 模型配置
MODEL_SAVE_PATH = "models/"
LATEST_MODEL_PATH = "models/latest_model.pkl"

# 日志配置
LOG_LEVEL = "INFO"
LOG_ROTATION = "1 day"
```

## 🔄 数据生成

项目内置多种数据生成器：

| 生成器 | 类型 | 说明 |
|---------|------|------|
| `CommonWeakPassword` | 弱密码 | 常见的弱密码数据 |
| `HuaweiStylePassword` | 华为风格 | 模拟华为设备密码 |
| `TokenStylePassword` | Token风格 | API Token、访问密钥等 |
| `DjangoTokenStylePassword` | Django Token | Django框架的Token格式 |
| `NormalTextGenerator` | 正常文本 | 非敏感的日常文本 |
| `NormalCodeGenerator` | 代码段 | 正常的代码片段 |

## 🎯 性能指标

基于默认训练数据的性能表现：

- **准确率**: ~95%
- **精准率**: ~93%
- **召回率**: ~94%
- **F1分数**: ~93.5%

*注：实际性能取决于训练数据的质量和数量*:## 🔭 故障排除

### 常见问题

1. **模块导入错误**
   - 检查Python路径是否正确
   - 确保所有依赖已正确安装
   - 检查隐藏导入配置是否完整

2. **构建失败**
   - 查看日志文件获取详细错误信息
   - 检查是PyInstaller是否正确安装
   - 确保有足够的内存和磁盘空间

3. **数据加载问题**
   - 检查数据文件路径是否存在
   - 验证数据格式是否正确
   - 检查文件权限

### 日志文件位置

```
logs/
├── build_windows_x86_64_YYYY-MM-DD.log      # 构建日志
├── package_manager_YYYY-MM-DD.log           # 包管理日志
├── train_log_YYYY-MM-DD.log                 # 训练日志
└── predict_log_YYYY-MM-DD.log               # 预测日志
```

## 📚 扩展功能

### 添加新脚本

在 `src/package/package_config.py` 中添加新的脚本文件名：

```python
MAIN_SCRIPTS = [
    "generate_data.py",
    "train_model.py", 
    "predict.py",
    "your_new_script.py"  # 添加新脚本
]
```

### 自定义构建器

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

## 📝 许可证

本项目采用 MIT 许可证，详情参见 LICENSE 文件。

## 👥 贡献

欢迎提交 Issues 和 Pull Requests！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🚀 更新日志

### v0.1.0 (2025-09-29)
- ✅ 初始版本发布
- ✅ 实现敏感信息检测基础功能
- ✅ 集成跨平台打包系统
- ✅ 添加完整的日志系统
- ✅ 内置多种数据生成器
- ✅ 支持一键式构建和部署
- ✅ Spec文件统一管理
- ✅ 包版本管理和清理功能

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！ ⭐**

</div>

