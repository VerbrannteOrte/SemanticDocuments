from diskcache import Cache
from xdg import BaseDirectory
from inspect import signature
from hashlib import sha256
from PIL.Image import Image
import functools
from surya.schema import TextDetectionResult
from copy import copy
from numpy import ndarray

from semdoc import logging

logger = logging.getLogger("semdoc.cache")
cache = Cache(directory=BaseDirectory.save_cache_path("semdoc"))

memoize = cache.memoize
ENOVAL = ("ENOVAL",)


def convert_key(key):
    if isinstance(key, Image) or isinstance(key, ndarray):
        data = key.tobytes()
        key = (type(key), sha256(data).digest())
    elif isinstance(key, TextDetectionResult):
        key = copy(key)
        data = key.heatmap.tobytes()
        key.heatmap = sha256(data).digest()
        data = key.affinity_map.tobytes()
        key.affinity_map = sha256(data).digest()
    return key


def cache_for(*params: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            s = signature(func)
            b = s.bind(*args, **kwargs)
            args_key = tuple(map(convert_key, (b.arguments[param] for param in params)))
            key = (func.__module__, func.__qualname__, args_key)
            logger.debug("trying to fetch function call from cache for key: %s", key)
            result = cache.get(key, default=ENOVAL, retry=True)
            if result is ENOVAL:
                logger.debug("cache miss")
                result = func(*args, **kwargs)
                cache.set(key, result, retry=True)
            return result

        return wrapper

    return decorator
