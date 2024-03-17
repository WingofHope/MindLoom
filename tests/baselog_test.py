# tests/baselog_test.py

import unittest
import sys
import os

# 添加源代码目录到 Python 解释器路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.services.logger.base_logger import BaseLogger

class TestLogger(unittest.TestCase):
    def test_logging(self):
        logger = BaseLogger('test_logger')
        logger.debug('This is a debug message')
        logger.info('This is an info message')
        logger.warning('This is a warning message')
        logger.error('This is an error message')
        logger.critical('This is a critical message')

if __name__ == '__main__':
    unittest.main()
    