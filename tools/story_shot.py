# 剧情场景截图：对话界面 / 互动提示 / 选项（单实例）
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from core import config
from core import main as M
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


snap(StoryScene("qianhai", "open"), 75, os.path.join(config.DOCS, "story_dialog.png"))
snap(StoryScene("qianhai", "mend_net"), 75, os.path.join(config.DOCS, "story_interact.png"))
snap(StoryScene("qianhai", "shells"), 75, os.path.join(config.DOCS, "story_choices.png"))
snap(StoryScene("qianhai", "night"), 120, os.path.join(config.DOCS, "story_rain.png"))
from core.story.map_scene import MapScene
snap(MapScene(), 75, os.path.join(config.DOCS, "map_explore.png"))
pygame.quit()
