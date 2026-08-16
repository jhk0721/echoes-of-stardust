# 全场景截图（自查用）
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from core import config
from core import main as M
from core.story.map_scene import MapScene, POIS
from core.story.walk_scene import WalkScene
from core.story.scene import StoryScene

g = M.Game()


def snap(scene, frames, out):
    g.set_scene(scene)
    for _ in range(frames):
        dt = g.clock.tick(60) / 1000.0
        g.scene.update(dt)
        g.surf.fill(config.INK)
        g.scene.draw(g.surf)
    pygame.transform.scale(g.surf, (config.SW, config.SH), g.screen)
    pygame.image.save(g.screen, out)
    print("已保存:", out)


snap(MapScene(), 75, os.path.join(config.DOCS, "map_world.png"))
snap(WalkScene(POIS[0]), 75, os.path.join(config.DOCS, "walk_boat.png"))
snap(WalkScene(POIS[3]), 75, os.path.join(config.DOCS, "walk_mist.png"))
snap(WalkScene(POIS[4]), 75, os.path.join(config.DOCS, "walk_shells.png"))
snap(M.BattleScene(), 75, os.path.join(config.DOCS, "battle.png"))
snap(M.TitleScene(), 120, os.path.join(config.DOCS, "title.png"))
pygame.quit()
