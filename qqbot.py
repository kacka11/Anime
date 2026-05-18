"""QQ 机器人模块：通过 napcat OneBot v11 HTTP API 发送群消息。"""
import time

import requests

from config import QQ_GROUP_ID, NAPCAT_URL


def _send_group_image(file_path: str, group_id: str | None = None) -> dict | None:
    """发送图片到群。"""
    group_id = group_id or QQ_GROUP_ID
    url = f"{NAPCAT_URL}/send_group_msg"
    payload = {
        "group_id": int(group_id),
        "message": [
            {"type": "image", "data": {"file": f"file:///{file_path}"}},
        ],
    }
    resp = requests.post(url, json=payload, timeout=30)
    return resp.json()


def _send_group_text(text: str, group_id: str | None = None) -> dict | None:
    """发送文字到群。"""
    group_id = group_id or QQ_GROUP_ID
    url = f"{NAPCAT_URL}/send_group_msg"
    payload = {
        "group_id": int(group_id),
        "message": [
            {"type": "text", "data": {"text": text}},
        ],
    }
    resp = requests.post(url, json=payload, timeout=30)
    return resp.json()


def send_to_group(
    items: list[dict],
    group_id: str | None = None,
    title: str = "",
    delay: float = 1.5,
):
    """将图文资讯逐条发送到 QQ 群。

    Args:
        items: 图文列表，每项含 image 和 text
        group_id: QQ 群号
        title: 开头标题（可选）
        delay: 每条消息间隔秒数
    """
    if not items:
        print("没有内容可发送。")
        return

    # 发送标题
    if title:
        _send_group_text(title, group_id)
        time.sleep(delay)

    # 逐条发送图片+文字
    for i, item in enumerate(items, 1):
        image_path = item["image"]
        text = item["text"]

        # 发送配图
        result = _send_group_image(image_path, group_id)
        if result and result.get("status") == "ok":
            print(f"[{i}/{len(items)}] 图片已发送: {image_path}")
        else:
            print(f"[{i}/{len(items)}] 图片发送失败: {result}")

        time.sleep(0.5)

        # 发送文字
        result = _send_group_text(text, group_id)
        if result and result.get("status") == "ok":
            print(f"[{i}/{len(items)}] 文字已发送: {text[:50]}...")
        else:
            print(f"[{i}/{len(items)}] 文字发送失败: {result}")

        time.sleep(delay)
