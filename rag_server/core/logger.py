import logging
from logging.handlers import RotatingFileHandler  # 日志轮转

def get_logger(name: str):
    logger = logging.getLogger(name)  # 获取日志对象
    logger.setLevel(logging.INFO)  # 设置日志级别  INFO，WARNING，ERROR

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")  # 日志格式
    # asctime:日志时间
    # name:日志名称,
    # levelname:日志级别,
    # message:日志信息

    # 文件日志
    file_handler = RotatingFileHandler("app.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")  # 日志的轮转，最大10M，最多5个
    file_handler.setFormatter(formatter)  # 设置日志格式

    # 控制台日志
    stream_handler = logging.StreamHandler()  # 控制台
    stream_handler.setFormatter(formatter)  # 设置日志格式

    logger.addHandler(file_handler)  # 添加文件日志
    logger.addHandler(stream_handler)  # 添加控制台日志
    return logger

logger = get_logger("ai_assistant")