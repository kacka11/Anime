"""视频下载模块：通过 yt-dlp + cookies 下载 B站视频。"""
import os
import subprocess

from config import VIDEO_DIR, FFMPEG_BIN

COOKIE_FILE = os.path.join(os.path.dirname(__file__), "data", "bilibili_cookies.txt")


def download_video(bvid: str, output_dir: str | None = None) -> str:
    """下载指定 bvid 的视频。

    Returns:
        下载后的视频文件路径
    """
    output_dir = output_dir or VIDEO_DIR
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{bvid}.mp4")
    url = f"https://www.bilibili.com/video/{bvid}"

    env = os.environ.copy()
    env["PATH"] = FFMPEG_BIN + os.pathsep + env.get("PATH", "")

    cmd = [
        "yt-dlp",
        "--cookies", COOKIE_FILE,
        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "-o", output_path,
        "--merge-output-format", "mp4",
        url,
    ]

    subprocess.run(cmd, check=True, timeout=300, env=env)
    return output_path
