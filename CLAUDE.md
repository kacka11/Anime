# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目定位

自动抓取 B站 UP主「芊莜-每日二次元速递」的每日资讯视频（《做今天二次元发生了啥？》），提取视频中的配图+解说文字，通过 napcat 以用户本人 QQ 号发送到指定 QQ 群。

## 核心架构

```
main.py (编排器)
  → bilibili.py   (B站 API：获取今日视频 bvid + wbi 签名)
  → downloader.py (yt-dlp 下载视频)
  → scene_detect.py (ffmpeg 场景检测提取配图)
  → transcriber.py  (faster-whisper 语音转文字 → 带时间戳的片段)
  → aligner.py      (时间戳对齐：将帧与文字片段配对)
  → qqbot.py        (napcat OneBot v11 HTTP API 发送图文消息)
```

### 关键对齐逻辑

视频格式为幻灯片：每张配图 + 对应语音解说。
- ffmpeg `select='gt(scene,0.3)'` 检测画面切换，提取每张配图的时间戳
- faster-whisper 输出带 `start/end` 的字幕片段
- aligner 将落在同一场景区间的字幕合并 → 该条资讯的文案

### 数据流

```
bvid → mp4 → frames/*.jpg + timestamps.json
           → audio.wav → whisper segments
                              ↓
           aligner → [(image_path, text), ...] → qqbot
```

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行主流程
python main.py

# 只测试某个模块
python -c "from bilibili import get_latest_video; print(get_latest_video('UID'))"

# 手动触发（指定 bvid）
python main.py --bvid BV1xx411c7mD
```

## 外部依赖

| 工具 | 用途 | 安装 |
|------|------|------|
| ffmpeg | 场景检测、音频提取 | `winget install ffmpeg` 或 PATH 中需有 |
| yt-dlp | B站视频下载 | `pip install yt-dlp` |
| faster-whisper | 语音转文字 | `pip install faster-whisper` |
| napcat | QQ 消息发送 | 需单独安装并运行 NTQQ + napcat |

## 配置

`config.py` 中的敏感值通过环境变量或 `config.local.py` 覆盖：
- `BILI_UID`: UP主的 B站 UID
- `QQ_GROUP_ID`: 目标 QQ 群号
- `NAPCAT_URL`: napcat HTTP API 地址（默认 http://localhost:3000）

## 注意事项

- napcat 依赖 NTQQ 客户端运行，执行前确保 QQ 已登录且 napcat 已启动
- bvid 去重通过 `data/texts/processed_bvids.txt` 实现
- 发送消息时每条间隔 1-2 秒，避免 QQ 风控
- 不要将 `config.local.py`、视频文件、模型文件提交到 git
