"""图文对齐模块：按时间戳将关键帧与转写文字配对。"""

from typing import TypedDict

class NewsItem(TypedDict):
    image: str
    text: str


def align_images_with_text(
    frames: list[str],
    scene_timestamps: list[float],
    segments: list[dict],
    min_text_length: int = 5,
) -> list[NewsItem]:
    """将场景帧与字幕片段按时间戳对齐。

    算法：
    - 场景时间戳 [t0, t1, t2, ...] 定义了每个场景的起始时间
    - 每个场景的区间是 [t_i, t_{i+1})（最后一个到视频结束）
    - 将字幕片段分配到对应的场景区间内
    - 合并同一场景内的所有字幕片段

    Args:
        frames: 帧图片路径列表
        scene_timestamps: 场景切换时刻（秒），长度应与 frames 一致
        segments: Whisper 转写的字幕片段，含 start/end/text
        min_text_length: 合并后最短文案长度，短于此值的资讯将被丢弃

    Returns:
        配对好的图文列表
    """
    if not frames or not scene_timestamps or not segments:
        return []

    # 构建场景区间
    scenes = []
    for i, (frame, ts_start) in enumerate(zip(frames, scene_timestamps)):
        if i + 1 < len(scene_timestamps):
            ts_end = scene_timestamps[i + 1]
        else:
            ts_end = float("inf")  # 最后一个场景到视频结束
        scenes.append({
            "image": frame,
            "start": ts_start,
            "end": ts_end,
            "texts": [],
        })

    # 将字幕分配到场景
    for seg in segments:
        seg_start = seg["start"]
        seg_text = seg["text"].strip()
        if not seg_text:
            continue

        for scene in scenes:
            if scene["start"] <= seg_start < scene["end"]:
                scene["texts"].append(seg_text)
                break

    # 合并输出
    items: list[NewsItem] = []
    for scene in scenes:
        full_text = " ".join(scene["texts"]).strip()
        if len(full_text) >= min_text_length:
            items.append(NewsItem(image=scene["image"], text=full_text))

    return items
