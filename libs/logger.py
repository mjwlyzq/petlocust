import logging
import os

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class Logger(object):
    logger = logging.getLogger("Logger")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    formatter = logging.Formatter(  # 指定logger输出格式
        '时间:%(asctime)s '  # 时间，默认精确到毫秒
        '文件名:%(filename)s '  # 日志文件名
        '模块名:%(module)s '  # 日志模块名
        '方法:%(funcName)s '  # 日志函数名
        '代码行:%(lineno)d '  # 日志模块代码行
        '级别:%(levelname) s '  # log级别
        '路径:%(pathname)s '  # 完整路径
        '消息：%(message)s'  # 打印的消息
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    # filename = PATH('./../log')
    # if not os.path.exists(filename):
    #     os.makedirs(filename)
    # # file_handler = logging.FileHandler(filename=f'{filename}/all.log', encoding='utf-8')
    # file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    # logger.addHandler(file_handler)

    error_count = 0

    @property
    def info(self):
        return self.logger.info

    @property
    def warning(self):
        return self.logger.warning

    @property
    def error(self):
        return self.logger.error

    @property
    def debug(self):
        return self.logger.debug

    @classmethod
    def set_debug_level(cls):
        cls.logger.setLevel(logging.DEBUG)

    @classmethod
    def set_info_level(cls):
        cls.logger.setLevel(logging.INFO)


log = Logger()
