import logging

__all__ = ('logger',)

formatter = logging.Formatter(
    "%(asctime)s;%(levelname)s;%(message)s",
    datefmt="%H:%M:%S"
)
chanel = logging.StreamHandler()
chanel.setFormatter(formatter)
logger = logging.getLogger("infiray")
logger.setLevel(logging.INFO)
logger.addHandler(chanel)
