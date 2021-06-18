import asyncio
import os

import fastapi
# noinspection PyPackageRequirements
import pytest
from jinja2.exceptions import TemplateNotFound
from starlette.requests import Request

import fastapi_jinja as fj

here = os.path.dirname(__file__)
folder = os.path.join(here, "templates")

fake_request = Request(scope={'type': 'http'})


def test_cannot_decorate_missing_template():
    with pytest.raises(TemplateNotFound):

        @fj.template("home/missing.j2")
        def view_method(request: Request):
            return {}

        view_method(fake_request)


def test_can_decorate_dict_sync_method():
    @fj.template("home/index.j2")
    def view_method(request: Request, a, b, c):
        return {"a": a, "b": b, "c": c}

    resp = view_method(fake_request, 1, 2, 3)
    assert isinstance(resp, fastapi.Response)
    assert resp.status_code == 200


def test_can_decorate_dict_async_method():
    @fj.template("home/index.j2")
    async def view_method(request: Request, a, b, c):
        return {"a": a, "b": b, "c": c}

    try:
        # python 3.7+
        resp = asyncio.run(view_method(fake_request, 1, 2, 3))
    except AttributeError:
        # python 3.6
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(asyncio.wait(view_method(fake_request, 1, 2, 3)))

    assert isinstance(resp, fastapi.Response)
    assert resp.status_code == 200


def test_direct_response_pass_through():
    @fj.template("home/index.j2")
    def view_method(request: Request, a, b, c):
        return fastapi.Response(content="abc", status_code=418)

    resp = view_method(fake_request, 1, 2, 3)
    assert isinstance(resp, fastapi.Response)
    assert resp.status_code == 418
    assert resp.body == b"abc"
