# src/config.py

import sys
import os
import json

# 获取当前项目根目录
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.dirname(__file__))
# 获取默认配置文件路径
config_path = os.path.join(root_path,'config/default_config.json')
# 从文件中加载 JSON 数据
class Config:
    def __init__(self, config_path=config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as config_file:
            return json.load(config_file)

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
        except KeyError:
            return default
        return value

    def set(self, key, value):
        keys = key.split('.')
        d = self.config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value
        self.save_config()

    def save_config(self):
        with open(self.config_path, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

# Initialize the configuration
config = Config()

# 获取 LOG 相关配置
LOG_PATH = config.get('log_config.path', 'log/')
LOG_MODE = config.get('log_config.mode', 'debug')

# 获取MongoDB 相关配置
MONGO_CONFIG = {'host':'localhost', 'port':27017, 'username':None, 'password':None, 'db_name':'test'}
# if 'mongodb_config' in config_json:
#     MONGO_CONFIG = config_json['mongodb_config']

# Example usage
# if __name__ == "__main__":
#     print(config.get("随便来个database url"))