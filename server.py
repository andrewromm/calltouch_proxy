from aiohttp import web, ClientSession
from aiojobs.aiohttp import setup, spawn
import logging
import re
import os

TOKEN = os.environ.get("TOKEN")
CT_MEDALVIAN_ID = os.environ.get("CT_MEDALVIAN_ID")
CT_CMZMEDICAL_ID = os.environ.get("CT_CMZMEDICAL_ID")

logging.basicConfig(
    filename="log.log",
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG)
logger = logging.getLogger()

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
    post_data = await request.post()
    referer = request.headers["Referer"] if "Referer" in request.headers else ""
    
    logger.debug(f"POST from {referer} headers: {request.headers}")
    logger.debug(f"POST from {referer} data: {post_data}")

    if "Token" not in request.headers or request.headers["Token"] != TOKEN:
        logger.error(f"Incorrect TOKEN from {referer}")
        return web.Response(status=500)
    
    session_id = re.search(r"_ct_session_id=\d*", post_data["COOKIES"]) if "COOKIES" in post_data else None
    ct_entry = CalltouchEntry(phone_number=post_data["phone"] if "phone" in post_data else "", request_url=referer, session_id=session_id[0][15:] if session_id is not None else "", fio=post_data["name"] if "name" in post_data else "", email=post_data["email"] if "email" in post_data else "", comment=post_data["comments"] if "comments" in post_data else "")

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
                    logger.debug(f'CT send request: {ct_entry.__dict__}')
                    logger.debug(f'CT request was created at {resp["dateStr"]}, id {resp["requestId"]}')



async def calltouch_proxy_app():
    server = web.Application()
    server.router.add_post('/', index)

    setup(server)
    return server
    # web.run_app(server, path="127.0.0.1", port="8080")
