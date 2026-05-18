"""主入口：编排 B站视频 → 转写 → 推送到 QQ 群的全流程。"""
import argparse
import sys

from bilibili import get_latest_video
from downloader import download_video
from scene_detect import detect_scenes
from transcriber import transcribe_audio
from aligner import align_images_with_text
from qqbot import send_to_group


def run(bvid: str | None = None):
    """执行一次完整的抓取→推送流程。"""
    # 1. 获取今日视频
    if not bvid:
        bvid, title, pub_date = get_latest_video()
        if not bvid:
            print("今天没有新视频，退出。")
            return
        print(f"发现视频: [{bvid}] {title} ({pub_date})")
    else:
        title = "手动指定"

    # 2. 下载视频
    video_path = download_video(bvid)
    print(f"视频已下载: {video_path}")

    # 3. 场景检测 + 提取关键帧
    frames, scene_timestamps = detect_scenes(video_path)
    print(f"提取到 {len(frames)} 个关键帧")

    # 4. 语音转文字
    segments = transcribe_audio(video_path)
    print(f"转写出 {len(segments)} 个片段")

    # 5. 图文对齐
    items = align_images_with_text(frames, scene_timestamps, segments)
    print(f"对齐得到 {len(items)} 条资讯")

    # 6. 发送到 QQ 群
    send_to_group(items)
    print("推送完成！")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="B站视频图文抓取推送")
    parser.add_argument("--bvid", type=str, help="手动指定视频 bvid（跳过今日检测）")
    args = parser.parse_args()
    run(bvid=args.bvid)
