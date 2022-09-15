from aiohttp import web, ClientSession
from aiojobs.aiohttp import setup, spawn
import logging
import re


TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtZWRhbHZpYW4iLCJuYW1lIjoiRnVja1lvdSIsImlhdCI6MTUxNjIzOTAyMn0.0wgLveTkc5tbyjmwltvBDMy4XSyII5HCMnx0iKKRnbE"
CT_MEDALVIAN_ID = "3295"
CT_CMZMEDICAL_ID = "16474"

class CalltouchEntry():
    def __init__(self, phone_number, request_url, session_id, fio="", email="", comment="") -> None:
        self.fio = fio
        self.phoneNumber = phone_number
        self.email = email
        self.subject = "Заявка с сайта"
        self.comment = comment
        self.requestUrl = request_url
        self.sessionId = session_id
        self.subject = ""


async def index(request):
    if "token_ct" not in request.headers or request.headers["token_ct"] != TOKEN:
        print("Incorrect TOKEN")
        return web.Response(status=500)
    post_data = await request.post()
    print("POST from site:", post_data)
    session_id = re.search(r"_ct_session_id=\d*", post_data["COOKIES"]) if "COOKIES" in post_data else None
    ct_entry = CalltouchEntry(phone_number=post_data["phone"] if "phone" in post_data else "", request_url=request.headers["Referer"] if "Referer" in request.headers else "", session_id=session_id[0][15:] if session_id is not None else "", fio=post_data["name"] if "name" in post_data else "", email=post_data["email"] if "email" in post_data else "", comment=post_data["comments"] if "comments" in post_data else "")

    await spawn(request, push_to_calltouch(ct_entry))
    
    return web.Response(status=200)


async def push_to_calltouch(ct_entry: CalltouchEntry):
    url = None
    if "medalvian.ru" in ct_entry.requestUrl:
        url = f"https://api.calltouch.ru/calls-service/RestAPI/requests/{CT_MEDALVIAN_ID}/register/"
    elif "cmzmedical.ru" in ct_entry.requestUrl:
        url = f"https://api.calltouch.ru/calls-service/RestAPI/requests/{CT_CMZMEDICAL_ID}/register/"

    if url is not None:
        ct_entry.subject = "Заявка с сайта"
        async with ClientSession() as session:
            async with session.post(
                url=url,
                data=ct_entry.__dict__
            ) as resp:
                resp = await resp.json(encoding="utf8")
                if "requestId" in resp:
                    print(f'CT request was created at {resp["dateStr"]}, id {resp["requestId"]}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    server = web.Application()
    server.router.add_post('/', index)

    setup(server)
    web.run_app(server, path="127.0.0.1", port="8080")


# async def my_web_app():
#     app = web.Application()
#     app.router.add_post('/', index)
#     return app