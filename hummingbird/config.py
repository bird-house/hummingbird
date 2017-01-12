import os
from pywps import configuration as wpsconfig

import logging
logger = logging.getLogger(__name__)


def cache_path():
    cache_path = None
    try:
        cache_path = wpsconfig.get_config_value("cache", "cache_path")
    except:
        logger.warn("No cache path configured. Using default value.")
        cache_path = os.path.join(os.sep, "tmp", "cache")
    return cache_path
