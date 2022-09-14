from aiohttp import web
import logging


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
    if self.headers["token_ct"] != token:
        print("Incerrect TOKEN")
        return web.Response(status=500)
    post_data = await self.post()
    ct_entry = CalltouchEntry(
        phone_number=post_data["phone"] if "phone" in post_data else "", 
        request_url=self.headers["Referer"],
        session_id=post_data["_ct_session_id"] if "_ct_session_id" in post_data else "",
        fio=post_data["name"] if "name" in post_data else "",
        email=post_data["email"] if "email" in post_data else "",
        comment=post_data["comments"] if "comments" in post_data else ""
    )
    print("CT_ENTRY:", ct_entry.__dict__)
    return web.Response(status=200)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    server = web.Application()
    server.router.add_post('/', index)

    web.run_app(server, path="127.0.0.1", port="8080")


# async def my_web_app():
#     app = web.Application()
#     app.router.add_post('/', index)
#     return app