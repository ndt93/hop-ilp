import logging

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger.addHandler(handler)
