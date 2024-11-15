# encoding:utf-8

import time

import requests

from bot.chatgpt.chat_gpt_bot import ChatGPTBot
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf


local_bot_callback_url = conf().get("bot_local_url")
local_bot_username_white_list = list(conf().get("bot_local_username_white_list", "").split("|"))

class MessageQueueBot(ChatGPTBot):
    def __init__(self):
        super().__init__()

    def reply(self, query, context=None):
        from_username = context["msg"].from_user_nickname
        is_patpat = (query == "请你随机使用一种风格介绍你自己，并告诉用户输入#help可以查看帮助信息。")
        if from_username in local_bot_username_white_list:
            session_id = context["session_id"]
            receiver = context["receiver"]
            is_group = context["msg"].is_group

            data = {
                "from_username": from_username,
                "to_username": "bot",
                "session_id": receiver if is_group else session_id,
                "is_group": is_group,
            }

            # acquire reply content
            if context.type == ContextType.TEXT:
                data["type"] = "text"
                data["content"] = "remake" if is_patpat else query
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

        # 不在白名单或没有合适的文件类型
        if context.type not in (ContextType.IMAGE):
            return super().reply(query, context)
        return Reply(ReplyType.NOTHING, "")


def _send_msg(**payload):
    response = requests.post(local_bot_callback_url, **payload)
    logger.info(f"local bot receive state: {response.status_code}, msg: {response.text}")
