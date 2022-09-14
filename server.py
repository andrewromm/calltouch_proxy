from urllib import request, response
from aiohttp import web
import asyncio
import logging
import re
from aiojobs import aiohttp


token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtZWRhbHZpYW4iLCJuYW1lIjoiRnVja1lvdSIsImlhdCI6MTUxNjIzOTAyMn0.0wgLveTkc5tbyjmwltvBDMy4XSyII5HCMnx0iKKRnbE"

class CalltouchEntry():
    def __init__(self, phone_number, request_url, session_id, fio="", email="", comment="") -> None:
        self.fio = fio
        self.phoneNumber = phone_number
        self.email = email
        self.subject = "Заявка с сайта"
        self.comment = comment
        self.requestUrl = request_url
        self.sessionId = session_id 


async def index(self):
    if "token_ct" not in self.headers or self.headers["token_ct"] != token:
        print("Incorrect TOKEN")
        return web.Response(status=500)
    post_data = await self.post()
    print("POST:", post_data)
    session_id = re.search(r"_ct_session_id=\d*", post_data["COOKIES"]) if "COOKIES" in post_data else None
    ct_entry = CalltouchEntry(phone_number=post_data["phone"] if "phone" in post_data else "", request_url=self.headers["Referer"], session_id=session_id[0][15:] if session_id is not None else "", fio=post_data["name"] if "name" in post_data else "", email=post_data["email"] if "email" in post_data else "", comment=post_data["comments"] if "comments" in post_data else "")

    start = asyncio.Event()
    await aiohttp.spawn(request, push_to_calltouch(ct_entry, start))
    response = web.Response(status=200)
    await response.prepare(request)
    await response.write_eof()
    start.set()
    
    return response


async def push_to_calltouch(data, start):
    await start.wait()
    print("send", data.__dict__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    server = web.Application()
    server.router.add_post('/', index)

    web.run_app(server, path="127.0.0.1", port="8080")


# async def my_web_app():
#     app = web.Application()
#     app.router.add_post('/', index)
#     return app