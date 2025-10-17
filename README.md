<h1 align="center">
    <strong>asgi-logging-middleware</strong>
</h1>

<p align="center">
    <a href="https://github.com/alv2017/asgi-logging-middleware" target="_blank">
        <!-- Last commit -->
        <img src="https://img.shields.io/github/last-commit/alv2017/asgi-logging-middleware" alt="Latest Commit">
        <!-- GitHub Actions build status -->
        <img src="https://img.shields.io/github/actions/workflow/status/alv2017/asgi-logging-middleware/ci.yml?branch=main" alt="Build Status">
        <!-- Codecov coverage -->
        <img src="https://img.shields.io/codecov/c/github/alv2017/asgi-logging-middleware" alt="Code Coverage">
    </a>
    <br/>
    <a href="https://pypi.org/project/asgi-logging-middleware" target="_blank">
        <img src="https://img.shields.io/pypi/v/asgi-logging-middleware" alt="Package version">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/asgi-logging-middleware" alt="Python Version">
    <img src="https://img.shields.io/github/license/alv2017/asgi-logging-middleware">
</p>

## Overview

This project was created as a fork of [asgi-logger](https://github.com/Kludex/asgi-logger) project. 

ASGI logging middleware logs HTTP request/response data in a configurable format, similar to how web servers 
like Nginx or Apache log requests. Initially it was created as an alternative for the uvicorn 
access logger.

Primarily the middleware is targeted at Starlette and FastAPI applications, but it can be used with any 
ASGI application.


## Installation

``` bash
pip install asgi-logging-middleware
```

## Usage

If you're using it with uvicorn, remember that you need to erase the handlers from uvicorn's logger that is writing the access logs.
To do that, just:

```python
logging.getLogger("uvicorn.access").handlers = []
```

Below you can see an example with FastAPI, but you can use it with any other ASGI application:

```python
from fastapi import FastAPI
from fastapi.middleware import Middleware
from asgi_logging_middleware import AccessLoggerMiddleware

app = FastAPI(middleware=[Middleware(AccessLoggerMiddleware)])


@app.get("/")
async def home():
    return "Hello world!"
```

In case you want to add a custom format to the access logs, you can do it using the `format` parameter on the `AccessLoggerMiddleware`:

```python
AccessLoggerMiddleware(app, format="%(s)s")
```

For now you can verify the possible format values [here](https://github.com/alv2017/asgi-logging-middleware/blob/main/asgi_logging_middleware/middleware.py).
The documentation will be available soon.

## License

This project is licensed under the terms of the MIT license.
