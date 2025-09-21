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
        logger.info("\n" + classification_report(self.y_test, y_pred, target_names=['非敏感', '敏感'],
                                                 zero_division=0  # 可选：0, 1, 'warn'（默认行为）
                                                 ))

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
