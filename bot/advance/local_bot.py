# encoding:utf-8

import time

import requests

from bot.chatgpt.chat_gpt_bot import ChatGPTBot
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf


class MessageQueueBot(ChatGPTBot):
    def __init__(self):
        super().__init__()

    def reply(self, query, context=None):
        session_id = context["session_id"]
        from_username = context["msg"].from_user_nickname
        is_group = context["msg"].is_group

        data = {
            "from_username": from_username,
            "to_username": "bot",
            "session_id": session_id,
            "is_group": is_group,
        }

        # acquire reply content
        if context.type == ContextType.TEXT:
            data["type"] = "text"
            data["content"] = query
            _send_msg(
                data=data
            )

            # 获取到本地缓存的url。。。
            return Reply(ReplyType.NOTHING, "")

        elif context.type == ContextType.IMAGE:
            data["type"] = "pic"
            files = {
                "uploaded_file": open(query, "rb")  # Provide the file path here
            }
            _send_msg(
                data=data,
                files=files,
            )

            return Reply(ReplyType.NOTHING, "")
        else:
            return super().reply(query, context)


def _send_msg(**payload):
    url = conf().get("bot_local_url")
    response = requests.post(url, **payload)
    logger.info(f"local bot receive state: {response.status_code}, msg: {response.text}")
