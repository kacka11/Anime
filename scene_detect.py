"""场景检测模块：用 ffmpeg 检测视频画面切换并提取关键帧。"""
import json
import os
import re
import subprocess

from config import FRAME_DIR, FFMPEG_BIN

_FFMPEG = os.path.join(FFMPEG_BIN, "ffmpeg.exe")


def detect_scenes(video_path: str, threshold: float = 0.3) -> tuple[list[str], list[float]]:
    """检测视频场景切换，提取关键帧。

    Args:
        video_path: 视频文件路径
        threshold: 场景切换灵敏度 (0~1)

    Returns:
        (frame_paths, timestamps): 帧图片路径列表和时间戳列表（秒）
    """
    import os
    output_dir = os.path.join(FRAME_DIR, os.path.splitext(os.path.basename(video_path))[0])
    os.makedirs(output_dir, exist_ok=True)

    output_pattern = os.path.join(output_dir, "frame_%04d.jpg")

    cmd = [
        _FFMPEG,
        "-i", video_path,
        "-vf", f"select='gt(scene,{threshold})',showinfo",
        "-vsync", "vfr",
        "-q:v", "2",
        output_pattern,
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    # 从 stderr 的 showinfo 输出中解析时间戳
    timestamps = []
    for line in result.stderr.split("\n"):
        match = re.search(r"pts_time:([\d.]+)", line)
        if match:
            timestamps.append(float(match.group(1)))

    # 收集生成的帧文件
    frames = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".jpg")
    ])

    # 保存时间戳
    ts_file = os.path.join(output_dir, "timestamps.json")
    with open(ts_file, "w", encoding="utf-8") as f:
        json.dump({"frames": frames, "timestamps": timestamps}, f, indent=2, ensure_ascii=False)

    return frames, timestamps
