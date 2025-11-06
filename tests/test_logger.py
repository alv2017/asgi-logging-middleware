from __future__ import annotations

import logging
import shlex
import sys
from typing import Any

import httpx
import pytest
from asgiref.typing import ASGIReceiveCallable as Receive
from asgiref.typing import ASGISendCallable as Send
from asgiref.typing import Scope

from asgi_logging_middleware import AccessLoggerMiddleware


class Match:
    def __eq__(self, other: Any) -> bool:
        return True


async def success_app(scope: Scope, receive: Receive, send: Send) -> None:
    await receive()
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/plain")],
        }
    )
    await send({"type": "http.response.body", "body": b"", "more_body": False})


async def failure_app(scope: Scope, receive: Receive, send: Send) -> None:
    raise RuntimeError()


async def invalid_status_code_app(scope: Scope, receive: Receive, send: Send) -> None:
    await receive()
    await send({"type": "http.response.start", "status": 700, "headers": []})
    await send({"type": "http.response.body", "body": b"", "more_body": False})


@pytest.mark.anyio
async def test_default_format_200_response(caplog: pytest.LogCaptureFixture) -> None:
    app = AccessLoggerMiddleware(success_app)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        res = await client.get("/")
    assert res.status_code == 200
    messages = [record.msg % record.args for record in caplog.records]
    assert len(messages) == 1
    assert shlex.split(messages[0]) == [Match(), "-", "GET / HTTP/1.1", "200", "OK"]


@pytest.mark.anyio
async def test_default_format_500_response(caplog: pytest.LogCaptureFixture) -> None:
    app = AccessLoggerMiddleware(failure_app)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        with pytest.raises(RuntimeError):
            await client.get("/")
    messages = [record.msg % record.args for record in caplog.records]
    assert len(messages) == 1
    assert shlex.split(messages[0]) == [
        Match(),
        "-",
        "GET / HTTP/1.1",
        "500",
        "Internal",
        "Server",
        "Error",
    ]


@pytest.mark.anyio
async def test_logger_argument(caplog: pytest.LogCaptureFixture) -> None:
    custom_logger = logging.getLogger("customLogger")
    custom_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(message)s"))
    custom_logger.addHandler(handler)

    app = AccessLoggerMiddleware(success_app, logger=custom_logger)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        res = await client.get("/")
    assert res.status_code == 200
    messages = [record.msg % record.args for record in caplog.records]
    assert len(messages) == 1
    assert shlex.split(messages[0]) == [Match(), "-", "GET / HTTP/1.1", "200", "OK"]


@pytest.mark.anyio
async def test_invalid_status_code(caplog: pytest.LogCaptureFixture) -> None:
    app = AccessLoggerMiddleware(invalid_status_code_app)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        res = await client.get("/")
    assert res.status_code == 700
    messages = [record.msg % record.args for record in caplog.records]
    assert len(messages) == 1
    assert shlex.split(messages[0]) == [Match(), "-", "GET / HTTP/1.1", "700", "-"]


@pytest.mark.anyio
async def test_cpu_time_logging_success_app(caplog: pytest.LogCaptureFixture) -> None:
    custom_format = "%(client_addr)s, %(request_line)s, %(status_code)s, %(cpu_time)s"
    app = AccessLoggerMiddleware(success_app, format=custom_format)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        res = await client.get("/")
        assert res.status_code == 200
    messages = [record.msg % record.args for record in caplog.records]
    assert len(messages) == 1
    parts = messages[0].split(", ")
    assert len(parts) == 4
    cpu_time = float(parts[3])
    assert cpu_time >= 0.0


@pytest.mark.anyio
async def test_cpu_time_logging_failure_app(caplog: pytest.LogCaptureFixture) -> None:
    custom_format = "%(client_addr)s, %(request_line)s, %(status_code)s, %(cpu_time)s"
    app = AccessLoggerMiddleware(failure_app, format=custom_format)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        with pytest.raises(RuntimeError):
            res = await client.get("/")
            assert res.status_code == 500
    messages = [record.msg % record.args for record in caplog.records]
    assert len(messages) == 1
    parts = messages[0].split(", ")
    assert len(parts) == 4
    cpu_time = float(parts[3])
    assert cpu_time >= 0.0
