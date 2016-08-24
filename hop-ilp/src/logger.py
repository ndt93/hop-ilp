import logging

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

fileHandler = logging.FileHandler('log/log.log', mode='w')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(fileHandler)
