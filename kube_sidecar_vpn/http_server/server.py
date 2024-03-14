import asyncio
import logging
from typing import Callable

from aiohttp import web


class RequestHandler:
    def __init__(self, status_func: Callable[[], bool]):
        self.status_func = status_func

    async def handler(self, request):
        return web.json_response({"status": self.status_func()})


async def run_http_server(status_func: Callable[[], bool], port: int):
    logging.info(f"Starting http server on port {port}")

    rqhandler = RequestHandler(status_func)
    app = web.Application()
    app.add_routes([web.get("/", rqhandler.handler)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=port)
    await site.start()

    while True:
        await asyncio.sleep(3600)
