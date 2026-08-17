# 全星球流程测试：每个星球降落 → 对话 → 碎片 → 挽歌
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from core import main, save
from core.story.map_scene import MapScene
from core.story.planet_select import PlanetSelectScene
from core.story.scene import StoryScene
from core.story.walk_scene import WalkScene
from core.story.worlds import WORLDS

g = main.Game()


def frames(n):
    for _ in range(n):
        g.scene.update(1 / 60)
        g.scene.draw(g.surf)


def key(k):
    g.scene.event(pygame.event.Event(pygame.KEYDOWN, key=k))


# 1. 星球选择界面
g.set_scene(PlanetSelectScene())
frames(10)
assert isinstance(g.scene, PlanetSelectScene), "星球选择界面异常"
print("星球选择界面 OK ·", len(g.scene.worlds), "颗星球")

# 2. 逐个星球降落跑通（简化星球：talk/frag/finale）
for k, w in g.scene.worlds:
    g.set_scene(MapScene(k))
    guard = 0
    while guard < 400:
        guard += 1
        sc = g.scene
        if isinstance(sc, MapScene):
            if sc._all_done():
                break
            if sc.near:
                key(pygame.K_e)
            else:
                for p in sc.pois:
                    if p["key"] not in sc.pois_done:
                        sc.player.x = p["pos"][0] + 1
                        sc.player.y = p["pos"][1] + 1
                        break
            frames(3)
        elif isinstance(sc, WalkScene):
            sc.player.x = sc.npc_pos[0] + 1
            sc.player.y = sc.npc_pos[1] + 1
            frames(2)
            key(pygame.K_e)
            frames(2)
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
                k = {"water": pygame.K_l, "wind": pygame.K_j,
                     "fire": pygame.K_k, "earth": pygame.K_i}.get(it.get("note"), pygame.K_u)
                key(k)
            frames(2)
        elif isinstance(sc, main.BattleScene):
            from core.combat import finale as F
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
    # 挽歌完成（StoryScene done）也算星球完成
    done_all = (isinstance(g.scene, MapScene) and g.scene._all_done()) or \
               (isinstance(g.scene, StoryScene) and g.scene.state == "done")
    if not done_all:
        print("  FAIL 场景:", type(g.scene).__name__,
              getattr(g.scene, "state", "?"), getattr(g.scene, "scene_key", "?"),
              "pois_done:", getattr(g.scene, "pois_done", set()))
    print(f"  {w['name']}: {'PASS' if done_all else 'FAIL'}")
    assert done_all, f"{w['name']} 流程未跑通"

print("ALL WORLDS OK · 全部星球闭环")
pygame.quit()
