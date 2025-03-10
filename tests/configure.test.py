import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from config import config

# LOG 配置
LOG_PATH = config.get('log_config.path', 'log/')
LOG_MODE = config.get('log_config.mode', 'debug')

# 模板加载方法
TEMPLATE_LOAD_METHOD = config.get('prompts.default_source', 'file')

# MongoDB 配置
MONGO_CONFIG = config.get('prompts.mongodb_config')

# RabbitMQ 配置
RABBITMQ_CONFIG = config.get('actions.rabbitmq')

config.save_config()