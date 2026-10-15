import logging
from time import perf_counter
from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid4())
        start_time = perf_counter()
        status_code = 500

        async def send_with_logging(message: dict) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("ascii")))
                message = {**message, "headers": headers}

            await send(message)

        try:
            await self.app(scope, receive, send_with_logging)
        except Exception:
            logger.exception(
                "Request failed request_id=%s method=%s path=%s",
                request_id,
                scope.get("method"),
                scope.get("path"),
            )
            raise
        finally:
            duration_ms = (perf_counter() - start_time) * 1000

            logger.info(
                "Request completed request_id=%s method=%s "
                "path=%s status_code=%s duration_ms=%.2f",
                request_id,
                scope.get("method"),
                scope.get("path"),
                status_code,
                duration_ms,
            )
