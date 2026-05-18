"""B站 模块：通过 yt-dlp + cookies 获取 UP主最新视频信息。"""
import json
import os
import subprocess
from datetime import datetime, timezone, timedelta

from config import BILI_UID, PROCESSED_FILE

COOKIE_FILE = os.path.join(os.path.dirname(__file__), "data", "bilibili_cookies.txt")
TZ = timezone(timedelta(hours=8))


def _yt_dlp(*args, timeout: int = 60) -> subprocess.CompletedProcess:
    """运行 yt-dlp 命令，自动附加 cookies。"""
    cmd = ["yt-dlp", "--cookies", COOKIE_FILE, *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def is_processed(bvid: str) -> bool:
    try:
        with open(PROCESSED_FILE, "r") as f:
            return bvid in f.read().splitlines()
    except FileNotFoundError:
        return False


def mark_processed(bvid: str):
    os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
    with open(PROCESSED_FILE, "a") as f:
        f.write(f"{bvid}\n")


def _is_today(upload_date: str) -> bool:
    """判断 yyyyMMdd 格式的日期是否为今天（北京时间）。"""
    if not upload_date or len(upload_date) != 8:
        return False
    video_date = datetime.strptime(upload_date, "%Y%m%d").date()
    today = datetime.now(TZ).date()
    return video_date == today


def get_latest_video(uid: str | None = None) -> tuple[str | None, str | None, str | None]:
    """获取 UP主今日发布的最新视频。

    Returns:
        (bvid, title, pub_date) — 今天没有则全部为 None
    """
    uid = uid or BILI_UID
    if not uid:
        raise ValueError("请设置 BILI_UID")

    url = f"https://space.bilibili.com/{uid}/video"

    try:
        result = _yt_dlp(
            "--dump-json",
            "--playlist-end", "5",
            url,
            timeout=45,
        )
    except subprocess.TimeoutExpired:
        print("yt-dlp 获取视频列表超时")
        return None, None, None

    if result.returncode != 0:
        print(f"yt-dlp 错误: {result.stderr[:200]}")
        return None, None, None

    lines = result.stdout.strip().split("\n")
    for line in lines:
        if not line.strip():
            continue
        try:
            video = json.loads(line)
        except json.JSONDecodeError:
            continue

        bvid = video.get("id")
        title = video.get("title", "")
        upload_date = video.get("upload_date", "")

        if not bvid:
            continue

        if not _is_today(upload_date):
            print(f"最新视频非今日发布: [{bvid}] {title} ({upload_date})")
            return None, None, None

        if is_processed(bvid):
            print(f"视频 {bvid} 已处理过，跳过")
            return None, None, None

        pub_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
        return bvid, title, pub_date

    return None, None, None
