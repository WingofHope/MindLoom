# src/services/logger/create_logger.py

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from config import config  # 这里导入 config 对象

# 从配置文件中加载日志配置
LOG_PATH = config.get('log_config.path', 'log/')
LOG_LEVEL = config.get('log_config.level', 'debug').upper()
LOG_MODE = config.get('log_config.mode', 'develop')

# 映射日志级别
LOG_LEVEL_MAP = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

class CreateLogger:
    def __init__(self, name='base', log_file=None):
        log_dir = LOG_PATH
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
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

    def get_logger(self):
        return self.logger

# 创建不同模块的日志记录器
def get_logger(module_name):
    log_file = os.path.join(LOG_PATH, f'{module_name}.log')
    logger = CreateLogger(name=module_name, log_file=log_file)
    return logger.get_logger()

# 创建mindloom的基础log
base_log = get_logger('mindloom')
