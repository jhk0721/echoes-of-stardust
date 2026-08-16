# 完整性自查：所有素材路径存在性 + 关键流程
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

checks = [
    "assets/_new/beach1.png",
    "assets/_new/HR_Ocean Sunrise.png",
    "assets/_new/Lively_NPCs_v3.0/individual sprites/medieval/elder/elder_1.png",
    "assets/_new/Lively_NPCs_v3.0/individual sprites/medieval/princess/princess_1.png",
    "assets/_new/Bitcrawl_Free_Roguelike_v1/Characters/Normal_Outline_Sheet/Animation_Normal_Outline_Wraith.png",
    "assets/_new/FREE - Pixel Art Sidescroller Sea Backgrounds",
    "assets/audio/bgm.wav",
    "assets/audio/rain.wav",
    "assets/fonts/fusion-pixel-12px-monospaced-zh_hans.ttf",
    "assets/sprites/harp_real.png",
]
ok = True
for c in checks:
    exists = os.path.exists(c)
    if not exists:
        ok = False
    print(("OK  " if exists else "MISS"), c)

sea = glob.glob("assets/_new/FREE - Pixel Art Sidescroller Sea Backgrounds/**/*.png", recursive=True)
print("Sea 分层 png 数:", len(sea))
print("总体:", "PASS" if ok else "FAIL")
