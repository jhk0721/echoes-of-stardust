# 冒烟测试：无头模式跑通 主界面→战斗→填谱→结算 闭环
# 用法：python tools/smoke_test.py
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from tools import generate_assets

generate_assets.ensure()

from core import main
from core.combat import finale as F


def frames(g, n, dt=1 / 60):
    for _ in range(n):
        for e in pygame.event.get():
            pass
        g.scene.update(dt)
        g.scene.draw(g.surf)


g = main.Game()
g.set_scene(main.TitleScene())
frames(g, 20)                       # 主界面 20 帧
g.set_scene(main.BattleScene())
frames(g, 30)                       # 战斗 30 帧
b = g.scene
b.ling = 3
b.composer = F.Composer()           # 触发即兴终结技
b.composer_t = 5.0
for i in range(8):
    b.composer.fill()               # 填满 8 槽
    b.composer.move(1)
b.resolve_finale()                  # 解析序列 → 结算
frames(g, 40)
assert b.over in ("win", "lose")
print("SMOKE OK · 闭环通过 · 结算:", b.over, "· 最终hp:", b.hp)
pygame.quit()
