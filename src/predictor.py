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

        # 确保模型已加载
        if self.pipeline is None:
            logger.error("❌ 模型未加载")
            raise RuntimeError("模型未加载，请先加载模型。")

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