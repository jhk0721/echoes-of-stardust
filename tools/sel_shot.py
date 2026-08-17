# 星球选择界面截图
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from core import config
from core import main as M
from core.story.planet_select import PlanetSelectScene

g = M.Game()
g.set_scene(PlanetSelectScene())
for _ in range(75):
    dt = g.clock.tick(60) / 1000.0
    g.scene.update(dt)
    g.surf.fill(config.INK)
    g.scene.draw(g.surf)
pygame.transform.scale(g.surf, (config.SW, config.SH), g.screen)
pygame.image.save(g.screen, os.path.join(config.DOCS, "planet_select.png"))
print("已保存 planet_select.png")
pygame.quit()
