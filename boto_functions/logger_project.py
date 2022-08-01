from asyncio.log import logger
import logging
logging.basicConfig(filename='./logs/logger_logs.log', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger()
