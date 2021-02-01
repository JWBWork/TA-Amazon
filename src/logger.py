"""
Module to define logging behavior with preferred logging library
"""
from src import LOG_DIR
from loguru import logger
import logging
import sys, os

logger.remove()
logger.add(sys.stderr, level="INFO")


class InterceptHandler(logging.Handler):
	def emit(self, record):
		# Get corresponding Loguru level if it exists
		try:
			level = logger.level(record.levelname).name
		except ValueError:
			level = record.levelno

		# Find caller from where originated the logged message
		frame, depth = logging.currentframe(), 2
		while frame.f_code.co_filename == logging.__file__:
			frame = frame.f_back
			depth += 1

		logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=1)
logger.add(os.path.join(LOG_DIR,'log.txt'), rotation='5 MB')

from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger
selenium_logger.setLevel(logging.WARNING)

logging.basicConfig(level=logging.WARNING)