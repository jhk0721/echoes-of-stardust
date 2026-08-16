# 素材下载安装脚本：下载 zip → 解压到 assets 对应目录
import os
import time
import urllib.request
import zipfile

DL = "_dl"
os.makedirs(DL, exist_ok=True)

# (名称, 目标目录, url)
TASKS = [
    ("font_pixel", "assets/fonts",
     "https://gh-proxy.com/https://github.com/TakWolf/fusion-pixel-font/releases/download/2026.02.27/fusion-pixel-font-10px-proportional-ttf-v2026.02.27.zip"),
    ("kenney_ui", "assets/ui",
     "https://kenney.nl/media/pages/assets/ui-pack-pixel-adventure/405ba5278a-1729196257/kenney_ui-pack-pixel-adventure.zip"),
    ("oga_pixel", "assets/sprites",
     "https://opengameart.org/sites/default/files/Platformer%20Art%20Pixel%20Redux.zip"),
]


def get(url, dest, timeout=240):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r, open(dest, "wb") as f:
        total = int(r.headers.get("content-length") or 0)
        done = 0
        while True:
            chunk = r.read(65536)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if total:
                print(f"    {done/total*100:.0f}%", end="\r")
    return done


for name, target, url in TASKS:
    print(f"[{name}] 下载中...")
    os.makedirs(target, exist_ok=True)
    t = time.time()
    try:
        size = get(url, f"{DL}/{name}.zip")
        print(f"    {size/1024/1024:.1f} MB · {time.time()-t:.1f}s")
        with zipfile.ZipFile(f"{DL}/{name}.zip") as z:
            z.extractall(target)
        print(f"    → 已解压到 {target}")
    except Exception as ex:
        print(f"    FAIL: {type(ex).__name__}: {ex}")
