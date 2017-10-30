"""
Logging utilities/abstractions
"""
import logging
import logging.handlers


def setup_root_logger_handler(level=logging.INFO,
                              msg_format='[%(levelname)s] - %(asctime)s - %(funcName)s() - %(message)s',
                              date_format='%b %d, %Y %H:%M:%S') -> None:
    """
    This method sets formatter for root logger
    :param level:
    :param msg_format:
    :param date_format:
    :return:
    """
    # Initiate stream handler
    formatter = logging.Formatter(fmt=msg_format, datefmt=date_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [stream_handler]
