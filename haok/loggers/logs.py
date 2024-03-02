import logging


def setup_logger(level=logging.INFO, name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
