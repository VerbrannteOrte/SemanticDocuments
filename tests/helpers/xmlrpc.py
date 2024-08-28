from math import floor
from semdoc.xmlrpc import remote
import semdoc.cache as cache

local_calls = 0


@remote
def greet(whom: str) -> str:
    global local_calls
    local_calls += 1
    return f"Hello, {whom}!"


@remote("helper-adder")
def add(a: int, b: int) -> int:
    global local_calls
    local_calls += 1
    return a + b


@remote(name="helper-multiplier")
def mul(a: int, b: int) -> int:
    global local_calls
    local_calls += 1
    return a * b


@remote
@cache.cache_for("a", "b")
def sub(a: int, b: int) -> int:
    global local_calls
    local_calls += 1
    return a - b


@cache.cache_for("a", "b")
@remote
def div(a: int, b: int) -> int:
    global local_calls
    local_calls += 1
    return floor(a / b)
