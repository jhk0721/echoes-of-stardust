# 无头渲染主界面截图（供验收视觉）：标题期 + 菜单期
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from core import config  # noqa: E402
from core import main as M  # noqa: E402


def snap(g, frames, out):
    for _ in range(frames):
        dt = g.clock.tick(60) / 1000.0
        g.scene.update(dt)
        g.surf.fill(config.INK)
        g.scene.draw(g.surf)
    pygame.transform.scale(g.surf, (config.SW, config.SH), g.screen)
    pygame.image.save(g.screen, out)
    print("已保存:", out)


g = M.Game()
g.set_scene(M.TitleScene())
snap(g, 75, os.path.join(config.DOCS, "main_menu_1.png"))    # 1.25s：标题期
snap(g, 75, os.path.join(config.DOCS, "main_menu_2.png"))    # 2.5s：菜单期
pygame.quit()
