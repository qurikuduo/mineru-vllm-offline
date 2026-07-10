"""Offline Swagger UI / ReDoc support for the mineru FastAPI app.

Mounts vendored swagger-ui / redoc static assets and overrides the
``/docs`` and ``/redoc`` routes so they work in air-gapped (no-internet)
environments.

Used by patching ``mineru/cli/fast_api.py`` to call
``apply_offline_docs(app)`` right after ``app = create_app()``.
"""
from __future__ import annotations

import pathlib
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

# vLLM ships swagger-ui-bundle.js + swagger-ui.css in its instrumentator
# static dir. We drop redoc.standalone.js next to them at build time.
#STATIC_DIR = pathlib.Path(
#    "/usr/local/lib/python3.12/dist-packages/vllm/"
#    "entrypoints/serve/instrumentator/static"
#)
STATIC_DIR = pathlib.Path("/opt/mineru-static")

SWAGGER_JS_URL = "/static/swagger-ui-bundle.js"
SWAGGER_CSS_URL = "/static/swagger-ui.css"
REDOC_JS_URL = "/static/redoc.standalone.js"
# Inline 1x1 transparent gif so the browser stops asking for /favicon.ico
# from the external site.
FAVICON_DATA_URL = (
    "data:image/gif;base64,"
    "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
)


def _replace_routes(app: FastAPI, paths: set[str]) -> None:
    """Drop any existing routes whose path matches one of ``paths``."""
    kept = [r for r in app.router.routes if getattr(r, "path", None) not in paths]
    app.router.routes = kept


def apply_offline_docs(app: FastAPI) -> None:
    """Mount vendored assets and override the docs routes.

    Idempotent — calling twice is a no-op.
    """
    if getattr(app.state, "_mineru_offline_docs_applied", False):
        return

    if not STATIC_DIR.is_dir():
        import logging
        logging.getLogger(__name__).warning(
            "Offline docs static dir not found: %s", STATIC_DIR
        )
        return

    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="mineru_offline_static",
    )

    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url or "/docs/oauth2-redirect"
    _replace_routes(app, {"/docs", "/redoc", oauth2_redirect_url})

    @app.get("/docs", include_in_schema=False)
    async def _custom_swagger_ui_html() -> Any:
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=(app.title or "API") + " - Swagger UI",
            oauth2_redirect_url=oauth2_redirect_url,
            swagger_js_url=SWAGGER_JS_URL,
            swagger_css_url=SWAGGER_CSS_URL,
            swagger_favicon_url=FAVICON_DATA_URL,
        )

    @app.get(oauth2_redirect_url, include_in_schema=False)
    async def _swagger_ui_redirect() -> Any:
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def _custom_redoc_html() -> Any:
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=(app.title or "API") + " - ReDoc",
            redoc_js_url=REDOC_JS_URL,
            redoc_favicon_url=FAVICON_DATA_URL,
            with_google_fonts=False,
        )

    app.state._mineru_offline_docs_applied = True
