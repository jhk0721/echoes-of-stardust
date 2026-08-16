# 自查：主界面星球颜色是否多样（纯白修复验证）
import collections
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from core import main as M

g = M.Game()
g.set_scene(M.TitleScene())
for _ in range(140):
    g.scene.update(1 / 60)
    g.scene.draw(g.surf)

cols = collections.Counter()
white = 0
for y in range(0, 270, 4):
    for x in range(0, 480, 4):
        c = tuple(g.surf.get_at((x, y))[:3])
        s = sum(c)
        if s > 40:
            cols[c] += 1
            if s > 700:
                white += 1
print("非黑采样颜色种类:", len(cols))
print("TOP8:", [c for c, _ in cols.most_common(8)])
print("近白色像素(>700):", white, "（应为少量：星尘/高光）")
pygame.quit()
