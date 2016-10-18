import os
from pywps import config as wpsconfig

import logging
logger = logging.getLogger(__name__)


def cache_path():
    cache_path = None
    try:
        cache_path = wpsconfig.getConfigValue("cache", "cache_path")
    except:
        logger.warn("No cache path configured. Using default value.")
        cache_path = os.path.join(os.sep, "tmp", "cache")
    return cache_path
