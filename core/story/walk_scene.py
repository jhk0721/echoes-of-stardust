# 局部探索场景：进入 POI 地点 → WASD 走到 NPC 旁 → 按 E 对话
# 星露谷式体验：角色在场景里自由移动，NPC 站在场景中等待互动
import math
import os

import pygame

from core import config, audio, ui

NPC_DIR = "assets/_new/Lively_NPCs_v3.0/individual sprites/medieval"
SEA_DIR = "assets/_new/FREE - Pixel Art Sidescroller Sea Backgrounds"

# Sea 分层背景（1024×346，按层序叠加 → 缩放 480×270）
_sea_cache = {}


def _sea_layer(name):
    if name in _sea_cache:
        return _sea_cache[name]
    import glob
    p = glob.glob(f"{SEA_DIR}/**/{name}.png", recursive=True)
    if not p:
        return None
    img = pygame.image.load(p[0])
    img = pygame.transform.scale(img, (config.W, config.H))
    _sea_cache[name] = img
    return img


def _make_sea_bg(day=True, boat=False):
    """组合海景：天空 + 远海 + 船 + 近海 + 云 + 太阳/月亮"""
    s = pygame.Surface((config.W, config.H))
    layers = ["BG_DAY" if day else "BG_NIGHT",
              "OCEANB_DAY" if day else "OCEANB_NIGHT",
              "BOAT" if boat else None,
              "OCEANF_DAY" if day else "OCEANF_NIGHT",
              "CLOUDS_DAY" if day else "CLOUDS_NIGHT",
              "SUN_DAY" if day else "MOON_NIGHT"]
    for L in layers:
        if not L:
            continue
        img = _sea_layer(L)
        if img:
            s.blit(img, (0, 0))
    return s


def _bg_img(name):
    if name == "sea_boat":
        return _make_sea_bg(day=True, boat=True)
    if name == "sea":
        return _make_sea_bg(day=True)
    if name == "sea_night":
        return _make_sea_bg(day=False)
    for root in ("assets/_new",):
        p = os.path.join(root, name)
        if os.path.exists(p):
            img = pygame.image.load(p)
            return pygame.transform.scale(img, (config.W, config.H))
    return None


def _npc_img(path, size=(40, 48)):
    """加载 NPC 图（支持切 Wraith 帧）"""
    try:
        if "Wraith" in path:
            sheet = pygame.image.load(path).convert_alpha()
            img = sheet.subsurface((0, 0, 16, 16))
        else:
            img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, size)
        return img
    except Exception:
        return None


class WalkScene:
    """POI 局部场景：进入 → 自由移动 → 走近 NPC 按 E 对话 → 出口回大世界"""

    def __init__(self, poi, memory=None, fragments=None, pois_done=None, planet_key="qianhai"):
        self.poi = poi
        self.planet_key = planet_key
        self.memory = memory or {"主线": 0, "互动": 0, "残片": 0, "聆听": 0}
        self.fragments = fragments or []
        self.pois_done = set(pois_done or [])
        w = poi.get("walk", {})
        self.bg = _bg_img(w.get("bg", "sea"))
        # 玩家：从入口进入
        self.player = pygame.Vector2(w.get("enter", (60, 200)))
        # NPC：站在场景中
        self.npc_pos = w.get("npc_pos", (300, 130))
        self.npc_name = w.get("npc_name", "记忆体")
        self.npc_img = _npc_img(w.get("npc_img", ""), w.get("npc_size", (40, 48)))
        self.exit_pos = w.get("exit", (30, 230))
        self.t = 0.0
        self.toast = ""
        self.toast_t = 0.0

    # ------------------------------------------------------------- 事件
    def event(self, e):
        if e.type != pygame.KEYDOWN:
            return
        if e.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
            if self.near_npc():
                audio.play("ui_ok")
                self._talk()
            elif self.near_exit():
                audio.play("ui_move")
                self._back_map()
        elif e.key == pygame.K_ESCAPE:
            self._back_map()

    def near_npc(self):
        return math.hypot(self.player.x - self.npc_pos[0],
                          self.player.y - self.npc_pos[1]) < 46

    def near_exit(self):
        return math.hypot(self.player.x - self.exit_pos[0],
                          self.player.y - self.exit_pos[1]) < 30

    def _talk(self):
        from core.story.scene import StoryScene
        self.game.set_scene(StoryScene(self.planet_key, self.poi["node"],
                                       memory=self.memory, fragments=self.fragments,
                                       mode="poi", poi_key=self.poi["key"]))

    def _back_map(self):
        from core.story.map_scene import MapScene
        self.game.set_scene(MapScene(self.planet_key, self.memory, self.fragments,
                                     list(self.pois_done)))

    # ------------------------------------------------------------- 更新
    def update(self, dt):
        self.t += dt
        if self.toast_t > 0:
            self.toast_t -= dt
        k = pygame.key.get_pressed()
        sp = 95
        if k[pygame.K_a] or k[pygame.K_LEFT]:
            self.player.x -= sp * dt
        if k[pygame.K_d] or k[pygame.K_RIGHT]:
            self.player.x += sp * dt
        if k[pygame.K_w] or k[pygame.K_UP]:
            self.player.y -= sp * dt
        if k[pygame.K_s] or k[pygame.K_DOWN]:
            self.player.y += sp * dt
        self.player.x = max(16, min(config.W - 16, self.player.x))
        self.player.y = max(50, min(config.H - 16, self.player.y))
        audio.play_loop("bgm", 0.28)

    # ------------------------------------------------------------- 绘制
    def draw(self, s):
        # 背景
        if self.bg:
            s.blit(self.bg, (0, 0))
        else:
            s.fill((10, 16, 44))
        # 出口标记（左下角）
        ex, ey = self.exit_pos
        pygame.draw.rect(s, (120, 140, 200), (int(ex - 8), int(ey - 8), 16, 16), 1)
        ui.text(s, "离开", (ex, ey + 12), size=8, color=(140, 165, 210), center=True)
        # NPC：角色图 + 光晕 + 名字
        nx, ny = self.npc_pos
        pul = 0.6 + 0.4 * math.sin(self.t * 2.5)
        for rr, a in ((26, 14), (18, 26)):
            circ = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
            pygame.draw.circle(circ, (170, 205, 245, a), (rr, rr), rr)
            s.blit(circ, (int(nx - rr), int(ny - rr + 8)))
        if self.npc_img:
            s.blit(self.npc_img, (int(nx - 20), int(ny - 40)))
        else:
            pygame.draw.circle(s, (200, 225, 255), (int(nx), int(ny)), 14)
        ui.text(s, self.npc_name, (int(nx), int(ny + 16)), size=12,
                color=(235, 235, 250), center=True)
        if self.near_npc():
            pygame.draw.circle(s, config.GOLD_HI, (int(nx), int(ny)), 30, 1)
        # 玩家（聆星者：蓝斗篷 + 背琴）
        px, py = int(self.player.x), int(self.player.y)
        pygame.draw.circle(s, (80, 115, 205), (px, py - 8), 6)
        pygame.draw.ellipse(s, (52, 76, 148), (px - 9, py - 4, 18, 14))
        pygame.draw.rect(s, (235, 205, 130), (px + 7, py - 12, 3, 14))
        pygame.draw.circle(s, (255, 225, 155), (px + 8, py - 12), 2)
        # 提示
        if self.near_npc():
            ui.text(s, f"按 E · 与{self.npc_name}对话", (config.W // 2, config.H - 26),
                    size=12, color=config.GOLD_HI, center=True)
        elif self.near_exit():
            ui.text(s, "按 E · 离开此地", (config.W // 2, config.H - 26),
                    size=12, color=(160, 185, 225), center=True)
        else:
            ui.text(s, "WASD 移动 · 走近发光者", (config.W // 2, config.H - 26),
                    size=12, color=(150, 170, 210), center=True)
        if self.toast_t > 0:
            ui.text(s, self.toast, (config.W // 2, config.H - 44), size=12,
                    color=config.GOLD_HI, center=True)
