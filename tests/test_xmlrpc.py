from diskcache import Cache
import logging
import multiprocessing
import pytest
import socket
import time

import semdoc.server

import helpers.xmlrpc as helper


@pytest.fixture(scope="module")
def server():
    host = "127.0.0.1"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen()
        port = sock.getsockname()[1]
        sock.close()
    # it is most convenient to fork here, because this way we have a separate
    # process and the makeshift call counter in helpers.xmlrpc works. this
    # produces a warning which we ignore via pyproject.toml
    mp = multiprocessing.get_context("fork")
    p = mp.Process(target=semdoc.server.run, args=(host, port))
    p.start()
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            sock.close()
            break
        else:
            time.sleep(1)
        sock.close()
    yield f"http://{host}:{port}"
    p.terminate()


def test_no_env(monkeypatch):
    monkeypatch.delenv("SEMDOC_XMLRPC", raising=False)
    calls_before = helper.local_calls
    greeting = helper.greet("world")
    assert calls_before + 1 == helper.local_calls
    assert greeting == "Hello, world!"


def test_server_unreachable(monkeypatch, caplog):
    monkeypatch.setenv("SEMDOC_XMLRPC", "http://127.0.0.222:12321")

    calls_before = helper.local_calls
    with caplog.at_level(logging.WARNING):
        greeting = helper.greet("world")
    assert calls_before + 1 == helper.local_calls
    assert greeting == "Hello, world!"
    assert "WARNING" in caplog.text
    assert "could not execute function" in caplog.text


def test_remote_working(monkeypatch, server):
    monkeypatch.setenv("SEMDOC_XMLRPC", server)
    calls_before = helper.local_calls
    greeting = helper.greet("world")
    assert greeting == "Hello, world!"
    assert calls_before == helper.local_calls


def test_different_name_local(monkeypatch, caplog):
    monkeypatch.delenv("SEMDOC_XMLRPC", raising=False)
    calls_before = helper.local_calls
    with caplog.at_level(logging.DEBUG):
        sum = helper.add(21, 21)
    assert sum == 42
    assert calls_before + 1 == helper.local_calls
    assert "helper-adder" in caplog.text


def test_different_name_remote(monkeypatch, server, caplog):
    monkeypatch.setenv("SEMDOC_XMLRPC", server)
    calls_before = helper.local_calls
    with caplog.at_level(logging.DEBUG):
        sum = helper.add(21, 21)
    assert sum == 42
    assert calls_before == helper.local_calls
    assert "helper-adder" in caplog.text


def test_name_keyword_local(monkeypatch, caplog):
    monkeypatch.delenv("SEMDOC_XMLRPC", raising=False)
    calls_before = helper.local_calls
    with caplog.at_level(logging.DEBUG):
        sum = helper.mul(6, 7)
    assert sum == 42
    assert calls_before + 1 == helper.local_calls
    assert "helper-multiplier" in caplog.text


def test_name_keyword_remote(monkeypatch, server, caplog):
    monkeypatch.setenv("SEMDOC_XMLRPC", server)
    calls_before = helper.local_calls
    with caplog.at_level(logging.DEBUG):
        sum = helper.mul(6, 7)
    assert sum == 42
    assert calls_before == helper.local_calls
    assert "helper-multiplier" in caplog.text


def test_rpc_before_cache_local(monkeypatch, tmp_path):
    monkeypatch.delenv("SEMDOC_XMLRPX", raising=False)
    monkeypatch.setattr(helper.cache, "cache", Cache(directory=tmp_path / "cache"))
    calls_before = helper.local_calls
    diff = helper.sub(43, 1)
    assert diff == 42
    # first call should be processed locally
    assert helper.local_calls == calls_before + 1
    diff = helper.sub(43, 1)
    assert diff == 42
    # second call should be cached
    assert helper.local_calls == calls_before + 1


def test_rpc_before_cache_remote(monkeypatch, server, tmp_path):
    monkeypatch.setenv("SEMDOC_XMLRPC", server)
    monkeypatch.setattr(helper.cache, "cache", Cache(directory=tmp_path / "cache"))
    calls_before = helper.local_calls
    diff = helper.sub(43, 1)
    assert diff == 42
    # should be processed on server
    assert helper.local_calls == calls_before
    monkeypatch.delenv("SEMDOC_XMLRPC")
    diff = helper.sub(43, 1)
    assert diff == 42
    # this is not in the cache yet
    assert helper.local_calls == calls_before + 1


def test_cache_before_rpc_local(monkeypatch, tmp_path):
    monkeypatch.delenv("SEMDOC_XMLRPC", raising=False)
    monkeypatch.setattr(helper.cache, "cache", Cache(directory=tmp_path / "cache"))
    calls_before = helper.local_calls
    quot = helper.div(84, 2)
    assert quot == 42
    # first call is processed locally
    assert helper.local_calls == calls_before + 1
    quot = helper.div(84, 2)
    assert quot == 42
    # second call is cached
    assert helper.local_calls == calls_before + 1


def test_cache_before_rpc_remote(monkeypatch, server, tmp_path):
    monkeypatch.setenv("SEMDOC_XMLRPC", server)
    monkeypatch.setattr(helper.cache, "cache", Cache(directory=tmp_path / "cache"))
    calls_before = helper.local_calls
    quot = helper.div(84, 2)
    assert quot == 42
    # first call is processed on server
    assert helper.local_calls == calls_before

    monkeypatch.delenv("SEMDOC_XMLRPC")
    quot = helper.div(84, 2)
    assert quot == 42
    # second call is cached
    assert helper.local_calls == calls_before
