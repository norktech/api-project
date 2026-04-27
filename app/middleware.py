import time
from loguru import logger
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        url = request.url.path
        client = request.client.host if request.client else "unknown"

        logger.info(f"REQUEST  | {method} {url} | client: {client}")

        response = await call_next(request)

        duration = round((time.time() - start_time) * 1000, 2)
        status = response.status_code

        if status >= 400:
            logger.warning(f"RESPONSE | {method} {url} | status: {status} | {duration}ms")
        else:
            logger.success(f"RESPONSE | {method} {url} | status: {status} | {duration}ms")

        return response