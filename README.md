非常好！我们将采用 **面向对象编程（OOP）** 的方式重构代码，并使用强大的 `loguru` 库进行日志记录，提升项目的可维护性、可扩展性和专业性。

---

## ✅ 项目结构（更新）

```bash
/ml-sensitive-detection/
│
├── models/                     # 模型存储目录
├── data/
│   └── sensitive_data.xlsx     # 训练数据
├── src/
│   ├── __init__.py
│   ├── trainer.py              # 模型训练类
│   ├── predictor.py            # 模型预测类
│   └── generate_sensitive_data/ # 数据生成模块
├── specs/                      # PyInstaller配置文件
├── dist/                       # 打包输出目录
├── train_model.py              # 巡检入口：训练 + 评估
├── predict.py                  # 预测入口
├── generate_data.py            # 数据生成入口
├── build.py                    # 跨平台打包脚本
├── build.bat                   # Windows打包脚本
├── build.sh                    # Linux/macOS打包脚本
├── config.py                   # 配置文件
└── requirements.txt
```

---

## 📦 第一步：安装依赖

```bash
pip install pandas scikit-learn openpyxl joblib loguru pyinstaller
```

### `requirements.txt`

```txt
pandas>=1.3.0
scikit-learn>=1.0.0
openpyxl>=3.0.0
joblib>=1.2.0
loguru>=0.7.0
pyinstaller>=6.0.0
```

---

## 🛠️ 配置文件 `config.py`

```python
# config.py
import os
from datetime import datetime

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据路径
DATA_PATH = os.path.join(ROOT_DIR, 'data', 'sensitive_data.xlsx')

# 模型保存目录
MODEL_DIR = os.path.join(ROOT_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

# 最新模型路径
LATEST_MODEL_PATH = os.path.join(MODEL_DIR, 'sensitive_classifier_latest.pkl')

# 带时间戳的模型路径格式
def get_timestamped_model_path():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(MODEL_DIR, f'sensitive_classifier_{timestamp}.pkl')
```

---

## 🧱 核心模块 1：`src/trainer.py`（模型训练器）

```python
# src/trainer.py
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from loguru import logger
import pandas as pd
import joblib
from config import DATA_PATH, LATEST_MODEL_PATH, get_timestamped_model_path


class ModelTrainer:
    """
    敏感信息分类模型训练器
    负责加载数据、训练、评估和保存模型
    """

    def __init__(self):
        self.pipeline = None
        self.X_test = None
        self.y_test = None
        logger.info("ModelTrainer 初始化完成")

    def load_data(self):
        """加载并清洗训练数据"""
        try:
            logger.info(f"正在加载数据: {DATA_PATH}")
            df = pd.read_excel(DATA_PATH)
            logger.success(f"✅ 数据加载成功，共 {len(df)} 条记录")

            # 清洗
            df.dropna(subset=['text', 'is_sensitive'], inplace=True)
            logger.debug(f"数据清洗完成，剩余 {len(df)} 条有效数据")

            return df['text'].astype(str), df['is_sensitive']
        except Exception as e:
            logger.error(f"❌ 数据加载失败: {e}")
            raise

    def build_pipeline(self):
        """构建机器学习 Pipeline"""
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
            ('classifier', MultinomialNB())
        ])
        logger.info("Pipeline 构建完成: TF-IDF + 朴素贝叶斯")

    def train(self):
        """训练模型"""
        X, y = self.load_data()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.build_pipeline()
        logger.info("开始模型训练...")
        self.pipeline.fit(X_train, y_train)

        # 保留测试集用于评估
        self.X_test = X_test
        self.y_test = y_test

        logger.success("🎉 模型训练完成！")

    def evaluate(self):
        """评估模型性能"""
        if not self.pipeline or self.X_test is None:
            logger.warning("⚠️ 模型未训练或测试集为空，跳过评估")
            return None

        y_pred = self.pipeline.predict(self.X_test)
        acc = accuracy_score(self.y_test, y_pred)

        logger.info(f"📊 模型评估结果:")
        logger.info(f"   准确率: {acc:.4f}")
        logger.info("\n" + classification_report(self.y_test, y_pred, target_names=['非敏感', '敏感']))

        return acc

    def save_model(self):
        """保存模型到文件系统"""
        try:
            # 保存带时间戳的版本
            timestamped_path = get_timestamped_model_path()
            joblib.dump(self.pipeline, timestamped_path)
            logger.info(f"📁 模型已保存（历史版本）: {timestamped_path}")

            # 保存为最新版
            joblib.dump(self.pipeline, LATEST_MODEL_PATH)
            logger.success(f"✅ 模型已更新至最新版: {LATEST_MODEL_PATH}")

        except Exception as e:
            logger.error(f"❌ 模型保存失败: {e}")
            raise
```

---

## 🔮 核心模块 2：`src/predictor.py`（模型预测器）

```python
# src/predictor.py
from loguru import logger
import joblib
import os
from config import LATEST_MODEL_PATH


class ModelPredictor:
    """
    敏感信息分类模型预测器
    负责加载模型并执行预测
    """

    def __init__(self, model_path=None):
        self.model_path = model_path or LATEST_MODEL_PATH
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        """加载训练好的模型"""
        if not os.path.exists(self.model_path):
            logger.error(f"❌ 模型文件不存在: {self.model_path}")
            raise FileNotFoundError(f"模型未找到，请先运行训练脚本。")

        try:
            self.pipeline = joblib.load(self.model_path)
            logger.success(f"✅ 模型加载成功: {self.model_path}")
        except Exception as e:
            logger.error(f"❌ 模型加载失败: {e}")
            raise

    def predict(self, texts):
        """
        预测文本是否为敏感信息
        :param texts: str 或 list[str]
        :return: list[dict] 包含文本、标签、置信度等信息
        """
        if isinstance(texts, str):
            texts = [texts]

        try:
            predictions = self.pipeline.predict(texts)
            probabilities = self.pipeline.predict_proba(texts)

            results = []
            for text, pred, prob in zip(texts, predictions, probabilities):
                label = "敏感" if pred == 1 else "非敏感"
                confidence = max(prob)
                result = {
                    'text': text,
                    'label': label,
                    'confidence': round(confidence, 4),
                    'is_sensitive': int(pred)
                }
                results.append(result)
                logger.info(f"📝 '{text}' -> {label} (置信度: {confidence:.4f})")

            return results

        except Exception as e:
            logger.error(f"❌ 预测过程中发生错误: {e}")
            raise
```

---

## ▶️ 入口脚本 1：`train_model.py`（巡检任务）

```python
# train_model.py
from src.trainer import ModelTrainer
from loguru import logger


def main():
    logger.add("logs/train_log_{time:YYYY-MM-DD}.log", rotation="1 day", level="INFO")
    logger.info("🔧 开始执行模型巡检任务...")

    trainer = ModelTrainer()
    try:
        trainer.train()
        accuracy = trainer.evaluate()
        trainer.save_model()
        logger.success("✅ 模型巡检任务完成！")
        return accuracy
    except Exception as e:
        logger.critical(f"💥 模型巡检任务失败: {e}")
        raise


if __name__ == "__main__":
    main()
```

---

## ▶️ 入口脚本 2：`predict.py`（预测任务）

```python
# predict.py
from src.predictor import ModelPredictor
from loguru import logger


def main():
    # 日志输出到文件 + 控制台
    logger.add("logs/predict_log_{time:YYYY-MM-DD}.log", rotation="1 day", level="INFO")

    try:
        predictor = ModelPredictor()
        test_texts = [
            "密码是123456",
            "今天天气真好",
            "身份证号：11010119900307XXXX",
            "请查收邮件"
        ]
        logger.info("🔍 开始批量预测...")
        results = predictor.predict(test_texts)
        logger.success("✅ 预测完成！")
        return results
    except Exception as e:
        logger.critical(f"💥 预测任务失败: {e}")
        raise


if __name__ == "__main__":
    main()
```

---

## 📝 运行示例

### 1. 首次训练（会自动创建 logs/ 目录）

```bash
python train_model.py
```

日志输出（控制台 + `logs/train_log_2025-09-21.log`）：

```
2025-09-21 10:30:00.000 | INFO     | __main__:main:10 - 🔧 开始执行模型巡检任务...
2025-09-21 10:30:00.100 | INFO     | trainer:<init>:18 - ModelTrainer 初始化完成
2025-09-21 10:30:00.200 | INFO     | trainer:load_data:28 - 正在加载数据: data/sensitive_data.xlsx
2025-09-21 10:30:00.300 | SUCCESS  | trainer:load_data:32 - ✅ 数据加载成功，共 100 条记录
...
2025-09-21 10:30:05.000 | SUCCESS  | trainer:save_model:83 - ✅ 模型已更新至最新版: models/sensitive_classifier_latest.pkl
2025-09-21 10:30:05.100 | SUCCESS  | __main__:main:18 - ✅ 模型巡检任务完成！
```

### 2. 执行预测

```bash
python predict.py
```

输出：

```
2025-09-21 10:31:00.000 | INFO     | predictor:_load_model:18 - ✅ 模型加载成功: models/sensitive_classifier_latest.pkl
2025-09-21 10:31:00.100 | INFO     | predictor:predict:33 - 🔍 开始批量预测...
2025-09-21 10:31:00.200 | INFO     | predictor:predict:43 - 📝 '密码是123456' -> 敏感 (置信度: 0.8921)
...
2025-09-21 10:31:00.500 | SUCCESS  | __main__:main:17 - ✅ 预测完成！
```

---

## ✅ 优势总结

| 特性 | 实现说明 |
|------|----------|
| **面向对象** | 使用 `ModelTrainer` 和 `ModelPredictor` 封装职责 |
| **日志记录** | 使用 `loguru` 输出结构化日志，支持文件滚动 |
| **配置分离** | 所有路径集中管理于 `config.py` |
| **异常处理** | 关键步骤均有 try/catch 与日志告警 |
| **生产就绪** | 支持定时训练 + 独立预测，便于部署 |
| **跨平台打包** | 支持 Windows/Linux 可执行文件打包 |

---

## 🚀 跨平台打包功能

项目现在支持使用 PyInstaller 将 Python 脚本打包为可执行文件，支持 Windows 和 Linux 平台。

### 打包命令

#### Windows 用户：
```cmd
# 直接双击运行
build.bat

# 或者命令行运行
python build.py
```

#### Linux/macOS 用户：
```bash
# 设置执行权限（仅首次）
chmod +x build.sh

# 运行打包脚本
./build.sh

# 或者直接运行
python3 build.py
```

### 打包输出

打包完成后，可执行文件将位于 `dist/` 目录下：

```
dist/
└── windows-amd64/          # Windows 64位版本
    ├── generate_data.exe   # 数据生成工具
    ├── train_model.exe     # 模型训练工具
    ├── predict.exe         # 预测工具
    ├── config.py          # 配置文件
    ├── README.md          # 说明文件
    ├── data/              # 数据目录
    ├── models/            # 模型目录
    └── logs/              # 日志目录
```

### 打包特性

- **单文件模式：** 每个脚本打包为一个独立的可执行文件
- **无依赖：** 打包后的文件可在没有 Python 环境的机器上运行
- **自动配置：** 自动包含所有必要的模块和数据文件
- **跨平台：** 同一脚本支持 Windows 和 Linux 打包

### 使用打包后的程序

1. **运行数据生成：**
   ```bash
   # Windows
   generate_data.exe
   
   # Linux
   ./generate_data
   ```

2. **运行模型训练：**
   ```bash
   # Windows
   train_model.exe
   
   # Linux
   ./train_model
   ```

3. **运行预测：**
   ```bash
   # Windows
   predict.exe
   
   # Linux
   ./predict
   ```

### 打包注意事项

- 首次打包可能需要较长时间（约 5-10 分钟）
- 打包后的文件较大（约 100-200MB），这是正常现象
- 如果打包失败，请检查是否正确安装了 PyInstaller：`pip install pyinstaller`

