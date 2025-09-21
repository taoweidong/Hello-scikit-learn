# config.py
import os
from datetime import datetime

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据路径
DATA_PATH = os.path.join(ROOT_DIR, 'data', 'sensitive_data.xlsx')

GENERATE_DATA_PATH = os.path.join(ROOT_DIR, 'data', 'sensitive_data.xlsx')

# 模型保存目录
MODEL_DIR = os.path.join(ROOT_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

# 最新模型路径
LATEST_MODEL_PATH = os.path.join(MODEL_DIR, 'sensitive_classifier_latest.pkl')


# 带时间戳的模型路径格式
def get_timestamped_model_path():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(MODEL_DIR, f'sensitive_classifier_{timestamp}.pkl')
