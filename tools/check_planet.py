# 验证 render_python 星球颜色（非纯白、有色相）
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from core import main as M
from native import planet_shader as PS

M.PLANET_COLS = [(255, 205, 110), (120, 190, 255), (215, 170, 255), (170, 135, 105),
                 (195, 105, 85), (150, 152, 160), (65, 125, 235), (200, 203, 210)]
for i, c in enumerate(M.PLANET_COLS):
    s = PS.render_python(12, i, c)
    w, h = s.get_size()
    # 统计主体区域颜色（中心 50%）
    colors = set()
    bright = 0
    for y in range(h // 4, h * 3 // 4, 2):
        for x in range(w // 4, w * 3 // 4, 2):
            r, g, b, a = s.get_at((x, y))
            if a > 200:
                colors.add((r, g, b))
                if r + g + b > 700:
                    bright += 1
    print(f"星球{i} 主色 {c} → 主体颜色数 {len(colors)} 近白 {bright}")
pygame.quit()
