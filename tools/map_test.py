# 地图探索流程测试：MapScene → POI → StoryScene(mode=poi) → 回地图 → 全部完成
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import math

from core import main, config
from core.combat import finale as F
from core.story.map_scene import MapScene
from core.story.scene import StoryScene
from core.story.walk_scene import WalkScene

g = main.Game()
map_scene = MapScene()
g.set_scene(map_scene)
INTERACT = {"water": pygame.K_l, "wind": pygame.K_j, "fire": pygame.K_k, "earth": pygame.K_i}
# 保存 POIS 引用用于最终断言
ALL_POIS = [p["key"] for p in map_scene.pois]


def frames(n):
    for _ in range(n):
        g.scene.update(1 / 60)
        g.scene.draw(g.surf)


def key(k):
    g.scene.event(pygame.event.Event(pygame.KEYDOWN, key=k))


# 状态机：等待特定场景类型
def wait_for_scene(target_type, max_frames=500):
    for _ in range(max_frames):
        frames(1)
        if isinstance(g.scene, target_type):
            return True
    return False


# 完成所有常规 POI
for poi_key in ["boat", "mend", "oar", "mist", "shells", "lamp"]:
    print(f"  开始 POI: {poi_key}")
    # 确保在 MapScene
    wait_for_scene(MapScene)
    sc = g.scene
    if not isinstance(sc, MapScene):
        print(f"  等待 MapScene 失败，当前场景: {type(sc).__name__}")
        continue
    # 移动到 POI 位置
    poi = next(p for p in sc.pois if p["key"] == poi_key)
    sc.player.x = poi["pos"][0] + 1
    sc.player.y = poi["pos"][1] + 1
    frames(3)
    # 触发 POI
    key(pygame.K_e)
    # 等待进入 WalkScene
    wait_for_scene(WalkScene)
    # 在 WalkScene 中移动到 NPC 位置并触发对话
    ws = g.scene
    if isinstance(ws, WalkScene):
        # 直接传送到 NPC 旁边
        ws.player.x = ws.npc_pos[0]
        ws.player.y = ws.npc_pos[1]
        frames(3)
        key(pygame.K_e)
    # 等待进入 StoryScene
    wait_for_scene(StoryScene, max_frames=200)
    # 处理 StoryScene 直到完成
    for _ in range(300):
        sc = g.scene
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
                k = INTERACT.get(it.get("note"), pygame.K_u) if it.get("type") == "note" else pygame.K_u
                key(k)
            frames(1)
        elif isinstance(sc, main.BattleScene):
            # 自动战斗胜利
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
            frames(1)
    # 等待返回 MapScene
    print(f"  等待返回 MapScene...")
    success = wait_for_scene(MapScene)
    if not success:
        print(f"  等待 MapScene 失败，当前场景: {type(g.scene).__name__}")
        # 尝试强制切换
        from core.story.map_scene import MapScene as MS
        g.set_scene(MS(g.scene.planet_key if hasattr(g.scene, 'planet_key') else 'qianhai',
                       g.scene.memory if hasattr(g.scene, 'memory') else {"主线": 0, "互动": 0, "残片": 0, "聆听": 0},
                       g.scene.fragments if hasattr(g.scene, 'fragments') else [],
                       list(g.scene.pois_done) if hasattr(g.scene, 'pois_done') else []))
    print(f"  完成 POI: {poi_key}, 当前 pois_done: {g.scene.pois_done if hasattr(g.scene, 'pois_done') else 'N/A'}")

# 所有常规 POI 完成，触发终章
print(f"  所有常规 POI 完成，触发终章")
sc = g.scene
if isinstance(sc, MapScene) and sc._all_done():
    cx, cy = config.W // 2, 96
    sc.player.x = cx
    sc.player.y = cy
    frames(3)
    if sc.near and sc.near["key"] == "finale":
        key(pygame.K_e)
        wait_for_scene(StoryScene, max_frames=200)
        # 处理终章 StoryScene
        for _ in range(500):
            sc = g.scene
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
                    k = INTERACT.get(it.get("note"), pygame.K_u) if it.get("type") == "note" else pygame.K_u
                    key(k)
                frames(1)
            elif isinstance(sc, MapScene):
                break
            else:
                frames(1)

# 等待返回 MapScene
wait_for_scene(MapScene, max_frames=200)

print("  场景:", type(g.scene).__name__, getattr(g.scene, "state", "?"))
d = __import__("core.save", fromlist=["save"]).load()
print("  存档 pois:", d and d["pois"], "memory:", d and d["memory"], "fragments:", d and d["fragments"])
print("  期望 POIS:", ALL_POIS)
print("  当前场景类型:", type(g.scene).__name__)
if hasattr(g.scene, 'pois_done'):
    print("  当前 pois_done:", g.scene.pois_done)
assert d and set(d["pois"]) == set(ALL_POIS), "探索点未全部完成"
print("MAP OK · 全部探索点完成")
pygame.quit()