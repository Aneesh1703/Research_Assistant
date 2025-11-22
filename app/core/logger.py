import logging
from .config import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("research_assistant")
