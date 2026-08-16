# 剧情全流程测试：状态机驱动 对话→互动→战斗→选项→挽歌→存档
# 用法：python tools/story_test.py
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from core import main, save
from core.combat import finale as F
from core.story.scene import StoryScene

INTERACT_KEY = {"water": pygame.K_l, "wind": pygame.K_j,
                "fire": pygame.K_k, "earth": pygame.K_i}

g = main.Game()
g.set_scene(StoryScene("qianhai", "tutorial"))


def frames(n):
    for _ in range(n):
        g.scene.update(1 / 60)
        g.scene.draw(g.surf)


def key(k):
    g.scene.event(pygame.event.Event(pygame.KEYDOWN, key=k))


last = None
for guard in range(400):
    sc = g.scene
    if isinstance(sc, StoryScene):
        tag = f"story:{sc.scene_key}:{sc.state}:{sc.line_i}"
    else:
        tag = f"{type(sc).__name__}:{getattr(sc, 'state', '?')}:{int(getattr(sc, 'over_t', 0) * 10)}"
    if isinstance(sc, StoryScene):
        if sc.state == "done":
            break
        if sc.state == "finale":
            frames(2)
            continue
        if sc.state == "lines":
            sc.char_i = 999
            key(pygame.K_RETURN)
        elif sc.state == "choices":
            key(pygame.K_RETURN)
        elif sc.state == "interact":
            it = sc.scene.get("interact") or {}
            k = INTERACT_KEY.get(it.get("note"), pygame.K_u) if it.get("type") == "note" \
                else pygame.K_u
            key(k)
        frames(2)
    elif isinstance(sc, main.BattleScene):
        if sc.over is None:
            sc.ling = 3
            sc.composer = F.Composer()
            sc.composer_t = 5.0
            for i in range(8):
                sc.composer.fill()
                sc.composer.move(1)
            sc.resolve_finale()
        frames(2)
    else:
        frames(2)
    if tag == last and guard > 200:     # 卡死保护（同状态超 200 轮）
        print("  疑似卡死:", tag)
        break
    last = tag
else:
    print("  超时未完成，最后状态:", type(g.scene).__name__,
          getattr(g.scene, "state", "?"), getattr(g.scene, "scene_key", "?"))

d = save.load()
print("  场景:", type(g.scene).__name__, getattr(g.scene, "state", "?"),
      getattr(g.scene, "scene_key", ""))
print("  存档:", d and d.get("done"), d and d["memory"], d and d["fragments"])
assert d and d.get("done"), "存档未标记完成"
assert "再见的见" in d["fragments"], "选项碎片未收集"
print("STORY OK · 浅海星全流程闭环 · 存档完成")
pygame.quit()
