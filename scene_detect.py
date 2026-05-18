"""场景检测模块：用 ffmpeg 检测视频画面切换并提取关键帧。"""
import json
import os
import re
import subprocess

from config import FRAME_DIR, FFMPEG_BIN, SCENE_THRESHOLD, MIN_SCENE_GAP

_FFMPEG = os.path.join(FFMPEG_BIN, "ffmpeg.exe")


def _merge_close_scenes(
    frames: list[str],
    timestamps: list[float],
    min_gap: float,
) -> tuple[list[str], list[float]]:
    """合并间隔过近的场景，保留每组的第一帧。

    幻灯片视频中，同一页的微小动画会触发多次场景切换。
    将间隔 < min_gap 的场景合并，只保留每组的第一帧。
    """
    if not timestamps or min_gap <= 0:
        return frames, timestamps

    merged_frames = [frames[0]]
    merged_ts = [timestamps[0]]
    last_kept = timestamps[0]

    for f, t in zip(frames[1:], timestamps[1:]):
        if t - last_kept >= min_gap:
            merged_frames.append(f)
            merged_ts.append(t)
            last_kept = t

    skipped = len(frames) - len(merged_frames)
    if skipped:
        print(f"  合并了 {skipped} 个过近场景 (间隔 < {min_gap}s)")

    return merged_frames, merged_ts


def detect_scenes(
    video_path: str,
    threshold: float | None = None,
    min_gap: float | None = None,
) -> tuple[list[str], list[float]]:
    """检测视频场景切换，提取关键帧。

    Args:
        video_path: 视频文件路径
        threshold: 场景切换灵敏度 (0~1)，默认使用 config.SCENE_THRESHOLD
        min_gap: 最小场景间隔（秒），小于此值的相邻场景合并

    Returns:
        (frame_paths, timestamps): 帧图片路径列表和时间戳列表（秒）
    """
    threshold = threshold if threshold is not None else SCENE_THRESHOLD
    min_gap = min_gap if min_gap is not None else MIN_SCENE_GAP

    import os
    output_dir = os.path.join(FRAME_DIR, os.path.splitext(os.path.basename(video_path))[0])
    os.makedirs(output_dir, exist_ok=True)

    # 清理旧帧
    for old in os.listdir(output_dir):
        if old.endswith(".jpg"):
            os.remove(os.path.join(output_dir, old))

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

    timestamps = []
    for line in result.stderr.split("\n"):
        match = re.search(r"pts_time:([\d.]+)", line)
        if match:
            timestamps.append(float(match.group(1)))

    frames = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".jpg")
    ])

    # 合并间隔过近的场景
    frames, timestamps = _merge_close_scenes(frames, timestamps, min_gap)

    ts_file = os.path.join(output_dir, "timestamps.json")
    with open(ts_file, "w", encoding="utf-8") as f:
        json.dump({"frames": frames, "timestamps": timestamps, "threshold": threshold, "min_gap": min_gap},
                  f, indent=2, ensure_ascii=False)

    return frames, timestamps
