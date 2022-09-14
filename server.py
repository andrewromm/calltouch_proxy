from aiohttp import web
import logging


async def index(request):
    print(request.headers)
    return web.Response(text="Welcome home!")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    server = web.Application()
    server.router.add_post('/', index)

    web.run_app(server, path="127.0.0.1", port="8080")


# async def my_web_app():
#     app = web.Application()
#     app.router.add_post('/', index)
#     return app