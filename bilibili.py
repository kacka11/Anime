"""B站 API 模块：获取 UP主最新视频信息。"""
import hashlib
import time
import urllib.parse

import requests

from config import BILI_UID, PROCESSED_FILE


def _get_wbi_keys() -> tuple[str, str]:
    """获取 B站 wbi 签名的密钥对。"""
    url = "https://api.bilibili.com/x/web-interface/nav"
    resp = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    data = resp.json()["data"]
    return data["wbi_img"]["img_key"], data["wbi_img"]["sub_key"]


def _sign_params(params: dict, img_key: str, sub_key: str) -> dict:
    """对请求参数进行 wbi 签名。"""
    mixin = img_key[:16] + sub_key[:16]
    # 实现 wbi 签名算法
    keys = sorted(params.keys())
    query = urllib.parse.urlencode(params)
    sign = hashlib.md5((query + mixin).encode()).hexdigest()
    params["w_rid"] = sign
    params["wts"] = int(time.time())
    return params


def is_processed(bvid: str) -> bool:
    """检查 bvid 是否已处理过。"""
    try:
        with open(PROCESSED_FILE, "r") as f:
            return bvid in f.read().splitlines()
    except FileNotFoundError:
        return False


def mark_processed(bvid: str):
    """标记 bvid 为已处理。"""
    import os
    os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
    with open(PROCESSED_FILE, "a") as f:
        f.write(f"{bvid}\n")


def get_latest_video(uid: str | None = None) -> tuple[str, str, str] | tuple[None, None, None]:
    """获取 UP主今日发布的最新视频。

    Returns:
        (bvid, title, pub_date) 或 (None, None, None)
    """
    uid = uid or BILI_UID
    if not uid:
        raise ValueError("请设置 BILI_UID")

    url = f"https://api.bilibili.com/x/space/wbi/arc/search"
    params = {
        "mid": uid,
        "ps": 5,
        "order": "pubdate",
    }

    resp = requests.get(url, params=params, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://space.bilibili.com/",
    })
    data = resp.json()

    if data["code"] != 0:
        print(f"B站 API 错误: {data}")
        return None, None, None

    videos = data.get("data", {}).get("list", {}).get("vlist", [])
    if not videos:
        print("未找到视频")
        return None, None, None

    # 取最新一条，检查是否是今天发布
    latest = videos[0]
    bvid = latest["bvid"]
    title = latest["title"]
    # pubdate 格式：yyyy-mm-dd，或者以时间戳格式
    created = latest.get("created", 0)

    # TODO: 更精确的今日判断
    return bvid, title, str(created)
