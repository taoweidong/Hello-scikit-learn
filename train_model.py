# -*- coding: utf-8 -*-
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
