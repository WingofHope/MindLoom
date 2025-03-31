# src/services/logger/create_logger.py

import os
import logging
import yaml
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# 获取当前项目根目录
root_path = Path(__file__).resolve().parent.parent.parent

# 配置文件路径
config_path = root_path / 'config' / 'config.yaml'
default_config_path = root_path / 'config' / 'default_config.yaml'
config_path = config_path if config_path.exists() else default_config_path

# 读取 log_config 配置
try:
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config_data = yaml.safe_load(config_file) or {}
        log_config = config_data.get('log_config', {})
except (FileNotFoundError, yaml.YAMLError):
    log_config = {}

# 提供默认值
LOG_PATH = log_config.get('path', 'log/')
LOG_LEVEL = log_config.get('level', 'debug').upper()
LOG_MODE = log_config.get('mode', 'develop')

# 映射日志级别
LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class CreateLogger:
    def __init__(self, name: str = 'base', log_file: str = None):
        log_dir = LOG_PATH
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = log_file or os.path.join(log_dir, f'{name}.log')
        self.logger = logging.getLogger(name)
        self.logger.setLevel(LOG_LEVEL_MAP.get(LOG_LEVEL, logging.DEBUG))
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 仅在开发模式下使用控制台输出
        if LOG_MODE == 'develop':
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 设定日志文件轮转
        backup_count = 0 if LOG_MODE == 'develop' else 180
        file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=backup_count)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger

# 创建不同模块的日志记录器
def get_logger(module_name: str) -> logging.Logger:
    log_file = os.path.join(LOG_PATH, f'{module_name}.log')
    logger = CreateLogger(name=module_name, log_file=log_file)
    return logger.get_logger()

# 创建 mindloom 的基础 log
base_log = get_logger('mindloom')
