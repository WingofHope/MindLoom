from loguru import logger
import os

# 1. 添加logger
# 获取当前文件的完整路径
current_file_path = os.path.abspath(__file__)
# build logger
logger_base = os.path.join(os.path.dirname(os.path.dirname(current_file_path)), "logs")
if not os.path.exists(logger_base):
    os.makedirs(logger_base)
log_info_path  = os.path.join(logger_base, "info.log")
log_error_path = os.path.join(logger_base, "error.log")

logger.add(log_info_path, level="INFO", rotation="12:00", retention="7 days")
logger.add(log_error_path, level="ERROR", rotation="12:00", retention="30 days")

def write_log(level, message):
    if level == "info":
        logger.info(message)
    elif level == "error":
        logger.error(message)
    else:
        logger.warning("log level is not correct")