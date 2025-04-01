import sys
import os
import string
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

os.environ["CONFIG_PASSWORD"] = "P6eJ9q5kR3JSAI6yJHgOfEG0qSykpmn3"
from config import config

print(config.get('actions.rabbitmq.password'))

# LOG 配置
LOG_PATH = config.get('log_config.path', 'log/')
LOG_MODE = config.get('log_config.mode', 'debug')

# 模板加载方法
TEMPLATE_LOAD_METHOD = config.get('prompts.default_source', 'file')

# MongoDB 配置
MONGO_CONFIG = config.get('prompts.mongodb_config')

# RabbitMQ 配置
RABBITMQ_CONFIG = config.get('actions.rabbitmq')

def secure_config():
    # 检查是否已有环境变量密码
    pwd = os.environ.get("CONFIG_PASSWORD")
    if not pwd:
        pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        print(f"自动生成的密码: {pwd}")
        os.environ["CONFIG_PASSWORD"] = pwd

    config.set("encryption.encryption_enabled", True)

    if config.save_config():
        print("保存加密后的配置文件成功。")
    else:
        print("保存配置失败，安全存储配置文件操作中止。")

# secure_config()
