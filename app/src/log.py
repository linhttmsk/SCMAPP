import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def logIni(folder_path):
    # log file
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    log_formart = logging.Formatter("%(asctime)s::%(levelname)s::%(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formart)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)


    file_handler = RotatingFileHandler(
        os.path.join(folder_path, 'info.log'), maxBytes=5 * (2**20), backupCount=2, encoding="utf-8")
    file_handler.setFormatter(log_formart)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    return logging