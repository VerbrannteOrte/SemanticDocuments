from xmlrpc.client import ServerProxy, Binary
import os
import functools
import pickle

from semdoc import logging

logger = logging.getLogger("semdoc.xmlrpc")
remote_functions = {}


def server_dispatch(name, bin_args):
    if name not in remote_functions:
        return None, False
    args, kwargs = pickle.loads(bin_args.data)
    func = remote_functions[name]
    try:
        result = func(*args, **kwargs)
    except Exception:
        return None, False
    bin_result = Binary(pickle.dumps(result))
    return bin_result, True


def remote(func=None, *, name=None):
    if isinstance(func, str):
        name = func
        func = None
    elif not name:
        name = func.__name__

    def remote_decorator(func):
        global remote_functions
        remote_functions[name] = func

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if "SEMDOC_XMLRPC" in os.environ:
                server = os.environ["SEMDOC_XMLRPC"]
                logger.debug(
                    f"SEMDOC_XMLRPC is set, trying to execute <{name}> on '{server}'"
                )
                client = ServerProxy(server)
                bin_args = Binary(pickle.dumps((args, kwargs)))
                try:
                    bin_result, okay = client.dispatch(name, bin_args)
                except Exception as e:
                    logger.warning(
                        f"could not execute function <{name}> on '{server}': {e}"
                    )
                else:
                    result = pickle.loads(bin_result.data)
                    return result
            logger.debug(f"executing <{name}> locally")
            return func(*args, **kwargs)

        return wrapper

    if func:
        return remote_decorator(func)
    else:
        return remote_decorator
