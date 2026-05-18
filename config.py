"""项目配置。敏感值通过 config.local.py 或环境变量覆盖。"""
import os

# B站 UP主 UID（芊莜-每日二次元速递）
BILI_UID = os.getenv("BILI_UID", "528881")

# QQ 群号
QQ_GROUP_ID = os.getenv("QQ_GROUP_ID", "695751650")

# napcat HTTP API 地址
NAPCAT_URL = os.getenv("NAPCAT_URL", "http://localhost:3000")

# faster-whisper 模型大小: tiny, base, small, medium, large
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

# 场景检测灵敏度 (0~1，越低越敏感)
SCENE_THRESHOLD = float(os.getenv("SCENE_THRESHOLD", "0.35"))

# 最小场景间隔（秒）：间隔小于此值视为同一场景，合并
MIN_SCENE_GAP = float(os.getenv("MIN_SCENE_GAP", "1.5"))

# ffmpeg 路径（winget 安装的默认路径）
FFMPEG_BIN = os.path.join(
    os.path.expandvars(r"%LOCALAPPDATA%"),
    "Microsoft", "WinGet", "Packages",
    "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe",
    "ffmpeg-8.1.1-full_build", "bin",
)

# 数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
VIDEO_DIR = os.path.join(DATA_DIR, "videos")
FRAME_DIR = os.path.join(DATA_DIR, "frames")
TEXT_DIR = os.path.join(DATA_DIR, "texts")
PROCESSED_FILE = os.path.join(TEXT_DIR, "processed_bvids.txt")

# 尝试加载本地覆盖配置
try:
    from config_local import *  # noqa
except ImportError:
    pass
