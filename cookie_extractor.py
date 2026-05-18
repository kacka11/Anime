"""Edge headless + CDP 协议提取 B站 cookies 并保存为 Netscape 格式。"""
import json
import os
import subprocess
import sys
import time
import urllib.request

import websocket

CDP_PORT = 9223
EDGE_PATH = None
for candidate in [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]:
    if os.path.exists(candidate):
        EDGE_PATH = candidate
        break

USER_DATA = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")
COOKIE_OUT = os.path.join(os.path.dirname(__file__), "data", "bilibili_cookies.txt")


def start_edge() -> subprocess.Popen:
    cmd = [
        EDGE_PATH,
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        f"--user-data-dir={USER_DATA}",
        "--headless=new",
        "https://www.bilibili.com/",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)
    return proc


def cdp_send(ws_url: str, method: str, params: dict | None = None) -> dict:
    """通过 CDP WebSocket 发送命令并返回结果。"""
    ws = websocket.create_connection(ws_url, timeout=15)
    msg = {"id": 1, "method": method}
    if params:
        msg["params"] = params
    ws.send(json.dumps(msg))
    result = json.loads(ws.recv())
    ws.close()
    return result.get("result", {})


def get_cookies() -> list[dict]:
    """启动 Edge 并提取 B站 cookies。"""
    print("启动 Edge headless...")
    proc = start_edge()

    try:
        # 获取页面列表
        resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json", timeout=10)
        pages = json.loads(resp.read())

        # 找到 bilibili 页面
        ws_url = None
        for page in pages:
            if page.get("type") == "page":
                ws_url = page["webSocketDebuggerUrl"]
                break
        if not ws_url:
            raise RuntimeError("找不到 CDP 页面")

        # 获取所有 cookies
        cookies = cdp_send(ws_url, "Network.getCookies")["cookies"]

        # 过滤 B站相关
        bili_cookies = [
            c for c in cookies
            if "bilibili" in c.get("domain", "")
        ]
        print(f"获取到 {len(bili_cookies)} 条 B站 cookies")

        return bili_cookies
    finally:
        proc.terminate()
        time.sleep(1)


def save_netscape(cookies: list[dict], path: str):
    """保存为 Netscape HTTP Cookie 格式（兼容 yt-dlp）。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for c in cookies:
            domain = c["domain"]
            flag = "TRUE" if domain.startswith(".") else "FALSE"
            secure = "TRUE" if c.get("secure") else "FALSE"
            expires = str(int(c.get("expires", 0))) if c.get("expires") else "0"
            name = c["name"]
            value = c["value"]
            path = c.get("path", "/")
            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
    print(f"已保存到 {path}")


if __name__ == "__main__":
    cookies = get_cookies()
    save_netscape(cookies, COOKIE_OUT)

    # 检查关键 cookie
    names = {c["name"] for c in cookies}
    for key in ["SESSDATA", "DedeUserID", "bili_jct", "buvid3"]:
        status = "OK" if key in names else "MISSING"
        print(f"  [{status}] {key}")
