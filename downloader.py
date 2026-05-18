"""视频下载模块：通过 yt-dlp 下载 B站视频。"""
import subprocess

from config import VIDEO_DIR


def download_video(bvid: str, output_dir: str | None = None) -> str:
    """下载指定 bvid 的视频。

    Returns:
        下载后的视频文件路径
    """
    import os
    output_dir = output_dir or VIDEO_DIR
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{bvid}.mp4")
    url = f"https://www.bilibili.com/video/{bvid}"

    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "-o", output_path,
        "--merge-output-format", "mp4",
        url,
    ]

    subprocess.run(cmd, check=True, timeout=300)
    return output_path
