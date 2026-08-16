# 解压安装：把 assets 根目录的素材包按类型分拣到对应目录
import os
import shutil
import zipfile

ROOT = "assets"
ARCHIVE = "_dl"
os.makedirs(ARCHIVE, exist_ok=True)

# 规则：zip 文件名关键词 → 目标目录
RULES = [
    ("fusion-pixel-font", "assets/fonts"),          # 字体
    ("kenney_particle", "assets/particles"),        # 粒子特效
    ("kenney_ui-pack", "assets/ui"),                # UI 面板
    ("kenney_cursor", "assets/ui/cursor"),          # 光标
    ("kenney_ui-audio", "assets/audio/kenney"),     # UI 音效
    ("platformer", "assets/sprites/oga"),           # OGA 平台素材
    ("Pixel Redux", "assets/sprites/oga"),
]

zips = [f for f in os.listdir(ROOT) if f.lower().endswith(".zip")]
print(f"找到 {len(zips)} 个素材包：{zips}\n")

for z in zips:
    src = os.path.join(ROOT, z)
    target = None
    for key, dest in RULES:
        if key.lower() in z.lower():
            target = dest
            break
    if not target:
        target = "assets/misc"
    os.makedirs(target, exist_ok=True)
    try:
        with zipfile.ZipFile(src) as zf:
            names = zf.namelist()
            zf.extractall(target)
        # 移走 zip 归档
        shutil.move(src, os.path.join(ARCHIVE, z))
        print(f"✓ {z} → {target} ({len(names)} 项)")
    except Exception as ex:
        print(f"✗ {z} FAIL: {ex}")
