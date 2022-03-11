import logging
import sys


def configure_logger(path: str, file: str):
    log_formatter = logging.Formatter('%(asctime)s: %(levelname)s - %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("{0}/{1}.log".format(path, file), mode='w')
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)
