
import sys
import os
import json

# 获取当前项目根目录
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 添加源代码目录到 Python 解释器路径中
# sys.path.insert(0, os.path.dirname(__file__))
# 获取默认配置文件路径
config_path = os.path.join(root_path,'config/default_config.json')
# 从文件中加载 JSON 数据
config_json = {}
with open(config_path, 'r') as config_file:
    config_json = json.load(config_file)
# 获取 LOG 相关配置
LOG_PATH = 'log/'
LOG_MODE = 'debug'
if 'log_config' in config_json:
    if 'path' in config_json['log_config']:
        LOG_PATH = config_json['log_config']['path']
    if 'mode' in config_json['log_config']:
        LOG_MODE = config_json['log_config']['mode']