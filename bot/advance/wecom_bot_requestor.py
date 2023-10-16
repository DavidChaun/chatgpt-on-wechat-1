import requests

from common.log import logger
from config import conf


def request(content: str) -> None:
    wecom_bot_webhook_key = conf().get("WECOM_BOT_WEBHOOK_KEY")
    response = requests.post(
        url=f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={wecom_bot_webhook_key}",
        headers={
            "Content-Type": "application/json;charset=utf-8",
        },
        json={"msgtype": "markdown", "markdown": {"content": content}},
    )

    _dict = response.json()
    if response.status_code != 200:
        logger.info(f"error request body: {_dict}")
        logger.error("webhook error.")
    else:
        logger.info(f"{_dict}")

