# 地图探索流程测试：MapScene → POI → StoryScene(mode=poi) → 回地图 → 全部完成
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from core import main
from core.combat import finale as F
from core.story.map_scene import MapScene, POIS
from core.story.scene import StoryScene

g = main.Game()
g.set_scene(MapScene())
INTERACT = {"water": pygame.K_l, "wind": pygame.K_j, "fire": pygame.K_k, "earth": pygame.K_i}


def frames(n):
    for _ in range(n):
        g.scene.update(1 / 60)
        g.scene.draw(g.surf)


def key(k):
    g.scene.event(pygame.event.Event(pygame.KEYDOWN, key=k))


for guard in range(600):
    sc = g.scene
    if isinstance(sc, MapScene):
        if sc._all_done() and sc.near and sc.near["key"] == "finale":
            break
        if sc.near:
            key(pygame.K_e)
        else:
            for p in POIS:              # 依次定位到未完成探索点旁
                if p["key"] not in sc.pois_done:
                    sc.player.x = p["pos"][0] + 1
                    sc.player.y = p["pos"][1] + 1
                    break
        frames(3)
    elif isinstance(sc, StoryScene):
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
            k = INTERACT.get(it.get("note"), pygame.K_u) if it.get("type") == "note" else pygame.K_u
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

print("  场景:", type(g.scene).__name__, getattr(g.scene, "state", "?"))
d = __import__("core.save", fromlist=["save"]).load()
print("  存档 pois:", d and d["pois"], "memory:", d and d["memory"], "fragments:", d and d["fragments"])
assert d and set(d["pois"]) == {p["key"] for p in POIS}, "探索点未全部完成"
print("MAP OK · 全部探索点完成")
pygame.quit()
