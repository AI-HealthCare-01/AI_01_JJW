import logging

from ai_worker.core.config import config
from ai_worker.core.logger import setup_logger


def get_logger() -> logging.Logger:
    # 앱 전역에서 사용할 로거
    return setup_logger()


default_logger = get_logger()