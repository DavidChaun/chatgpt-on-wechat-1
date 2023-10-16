# encoding:utf-8

import os
import signal
import sys

from channel import channel_factory
from common.log import logger
from config import conf, load_config
from plugins import *

import uvicorn
import requests
import threading
import time

from fastapi import FastAPI, Request, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from channel.wechat.wechat_channel import _cache


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 请求头
)


@app.get(
    "/login",
    description="login",
)
def login(access: str):
    if access != "9527":
        return {"code": 500, "msg": "error"}
    threading.Thread(target=run).start()

    times = 0
    max_times = 50
    qr_url = None
    while times < max_times:
        qr_url = _cache.get("login_qr")
        if qr_url:
            _cache.pop("login_qr")
            break
        else:
            times += 1
            time.sleep(3)

    if not qr_url:
        return {"code": 500, "msg": "no qr"}
    response = requests.get(
        url=qr_url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"},
        verify=False
    )
    _byte = response.content

    return Response(content=_byte)


def sigterm_handler_wrap(_signo):
    old_handler = signal.getsignal(_signo)

    def func(_signo, _stack_frame):
        logger.info("signal {} received, exiting...".format(_signo))
        conf().save_user_datas()
        if callable(old_handler):  #  check old_handler
            return old_handler(_signo, _stack_frame)
        sys.exit(0)

    signal.signal(_signo, func)


def run():
    try:
        # load config
        load_config()
        # ctrl + c
        # sigterm_handler_wrap(signal.SIGINT)
        # kill signal
        # sigterm_handler_wrap(signal.SIGTERM)

        # create channel
        channel_name = conf().get("channel_type", "wx")

        if "--cmd" in sys.argv:
            channel_name = "terminal"

        if channel_name == "wxy":
            os.environ["WECHATY_LOG"] = "warn"
            # os.environ['WECHATY_PUPPET_SERVICE_ENDPOINT'] = '127.0.0.1:9001'

        channel = channel_factory.create_channel(channel_name)
        if channel_name in ["wx", "wxy", "terminal", "wechatmp", "wechatmp_service", "wechatcom_app", "wework"]:
            PluginManager().load_plugins()

        # startup channel
        channel.startup()
    except Exception as e:
        logger.error("App startup failed!")
        logger.exception(e)


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
    )
