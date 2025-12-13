import logging
import os
import envs
from logging.handlers import RotatingFileHandler


logger = logging.getLogger("exec_logger")
logger.setLevel(logging.DEBUG) 

os.umask(0) 
open(envs.LOG, "a").close()
file_handler = RotatingFileHandler(envs.LOG, maxBytes=envs.LOG_MAX_SIZE)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
