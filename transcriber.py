"""语音转文字模块：使用 faster-whisper 转写视频音频。"""
import json
import os
import subprocess
from typing import TypedDict

from config import TEXT_DIR, WHISPER_MODEL, FFMPEG_BIN

_FFMPEG = os.path.join(FFMPEG_BIN, "ffmpeg.exe")


class Segment(TypedDict):
    start: float
    end: float
    text: str


def extract_audio(video_path: str) -> str:
    """从视频中提取音频为 WAV。"""
    audio_path = video_path.rsplit(".", 1)[0] + ".wav"
    cmd = [
        _FFMPEG,
        "-i", video_path,
        "-q:a", "0",
        "-map", "a",
        "-y",
        audio_path,
    ]
    subprocess.run(
        cmd, check=True, capture_output=True,
        encoding="utf-8", errors="replace",
    )
    return audio_path


def transcribe_audio(
    video_path: str,
    model_size: str | None = None,
) -> list[Segment]:
    # 中国用户优先使用 HF 镜像
    if not os.environ.get("HF_ENDPOINT"):
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    """转写视频音频，返回带时间戳的片段列表。"""
    from faster_whisper import WhisperModel

    model_size = model_size or WHISPER_MODEL
    audio_path = extract_audio(video_path)

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments_result, _ = model.transcribe(audio_path, beam_size=5, language="zh")

    segments: list[Segment] = []
    for seg in segments_result:
        segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
        })

    # 保存转录结果
    import os
    base = os.path.basename(video_path)
    json_path = os.path.join(TEXT_DIR, base.rsplit(".", 1)[0] + "_transcript.json")
    os.makedirs(TEXT_DIR, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)

    return segments
