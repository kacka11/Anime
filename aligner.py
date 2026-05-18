"""图文对齐模块：按时间戳将关键帧与转写文字配对。"""

import re
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

    使用文本中点时间匹配场景区间。后处理合并同一条新闻的多个帧。
    """
    if not frames or not scene_timestamps or not segments:
        return []

    # 构建场景区间
    scenes = []
    for i, (frame, ts_start) in enumerate(zip(frames, scene_timestamps)):
        ts_end = scene_timestamps[i + 1] if i + 1 < len(scene_timestamps) else float("inf")
        scenes.append({
            "image": frame,
            "start": ts_start,
            "end": ts_end,
            "texts": [],
        })

    # 用文本中点时间分配到场景
    for seg in segments:
        text = seg["text"].strip()
        if not text:
            continue
        mid = (seg["start"] + seg["end"]) / 2
        for scene in scenes:
            if scene["start"] <= mid < scene["end"]:
                scene["texts"].append(text)
                break

    # 合并同一场景的文本
    raw_items = []
    for scene in scenes:
        full_text = " ".join(scene["texts"]).strip()
        if len(full_text) >= min_text_length:
            raw_items.append(NewsItem(image=scene["image"], text=full_text))

    # 后处理：合并同一条新闻被拆分的帧
    # 规则：如果后一条文案不以数字编号开头（如"2 xxx"、"3 xxx"），视为前一条的延续
    return _merge_split_news(raw_items)


_NEWS_NUMBER_RE = re.compile(r"^\d+\s")


def _starts_like_new_news(text: str) -> bool:
    """判断文案是否像一条新新闻的开头（以数字编号开头）。"""
    return bool(_NEWS_NUMBER_RE.match(text))


def _merge_split_news(items: list[NewsItem]) -> list[NewsItem]:
    """合并因场景切换被拆分的同一条新闻。

    规则：如果后一条文案不以数字编号开头（如"2 xxxx"），且前一条也不为空，
    则视为前一条的延续，合并进去。标题（第一条）和结尾（最后一条）始终独立。
    """
    if len(items) <= 1:
        return items

    merged = [items[0]]
    for i, item in enumerate(items[1:], start=1):
        is_last = (i == len(items) - 1)
        prev = merged[-1]

        # 如果当前以数字开头 → 新新闻，直接追加
        if _starts_like_new_news(item["text"]):
            merged.append(item)
        # 如果是最后一条且不是新闻开头 → 可能是结尾语，追加不合并
        elif is_last:
            merged.append(item)
        # 不是新闻开头也不是结尾 → 延续上条新闻
        else:
            merged[-1] = NewsItem(
                image=prev["image"],
                text=prev["text"] + " " + item["text"],
            )

    return merged
