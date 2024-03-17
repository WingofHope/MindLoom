# src/services/logger/base_logger.py

import os
import logging
from logging.handlers import TimedRotatingFileHandler

from ...config import LOG_PATH,LOG_MODE

# 基础日志类
class BaseLogger:
    def __init__(self, name='mindloom', level=logging.DEBUG):
        # Create log directory if it doesn't exist
        log_dir = LOG_PATH
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_path = os.path.join(log_dir, '{}.log'.format(name))

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Log to console
        if LOG_MODE == 'debug':
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Log to file with automatic rotation
        if LOG_MODE == 'debug':
            backup_count = 0
        else:
            backup_count = 180
        file_handler = TimedRotatingFileHandler(log_path, when='midnight', interval=1, backupCount=backup_count)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)