from diskcache import Cache
from xdg import BaseDirectory
from inspect import signature
import functools

cache = Cache(directory=BaseDirectory.save_cache_path("semdoc"))

memoize = cache.memoize
ENOVAL = ("ENOVAL",)


def cache_for(*params: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            s = signature(func)
            b = s.bind(*args, **kwargs)
            args_key = tuple((b.arguments[param] for param in params))
            key = (func.__module__, func.__qualname__, args_key)
            result = cache.get(key, default=ENOVAL, retry=True)
            if result is ENOVAL:
                result = func(*args, **kwargs)
                cache.set(key, result, retry=True)
            return result

        return wrapper

    return decorator
