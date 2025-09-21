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