# 浅海星自由探索地图：WASD 移动 · 靠近探索点按 E 互动 · 全部完成触发挽歌
import math
import random

import pygame

from core import config, audio, ui
from core.combat import notes as N

# 探索点定义（坐标在 480x270 逻辑屏上；walk=局部探索场景配置）
POIS = [
    {"key": "boat",    "name": "渔夫的船",   "pos": (118, 150), "node": "open",
     "icon": "船",    "desc": "老渔夫和小女孩在船头",
     "walk": {"bg": "beach1.png", "npc_pos": (290, 130), "npc_name": "老渔夫",
               "npc_img": "adventurer_03/adventurer_03_1.png",
               "enter": (70, 200), "exit": (30, 230)}},
    {"key": "mend",    "name": "沉底的渔网",  "pos": (330, 110), "node": "mend_net",
     "icon": "网",    "desc": "用「水」音符托起渔网",
     "walk": {"bg": "HR_Ocean Sunrise.png", "npc_pos": (310, 140), "npc_name": "小女孩",
               "npc_img": "adventurer_02/adventurer_02_00.png",
               "enter": (60, 200), "exit": (30, 230)}},
    {"key": "oar",     "name": "迷雾船桨",   "pos": (92, 210),  "node": "find_oar",
     "icon": "桨",    "desc": "用「风」音符吹散迷雾",
     "walk": {"bg": "beach1.png", "npc_pos": (150, 120), "npc_name": "老渔夫",
               "npc_img": "adventurer_03/adventurer_03_1.png",
               "enter": (60, 200), "exit": (30, 230)}},
    {"key": "mist",    "name": "海雾·暗影",   "pos": (392, 160), "node": "battle",
     "icon": "雾",    "desc": "「寂静」的爪牙",
     "walk": {"bg": "HR_Ocean Sunrise.png", "npc_pos": (320, 130), "npc_name": "暗影兽",
               "npc_img": "adventurer_05/adventurer_05_1.png",
               "enter": (60, 200), "exit": (30, 230)}},
    {"key": "shells",  "name": "贝壳浅滩",    "pos": (238, 222), "node": "shells",
     "icon": "贝",    "desc": "陪小女孩捡贝壳",
     "walk": {"bg": "beach1.png", "npc_pos": (230, 130), "npc_name": "小女孩",
               "npc_img": "adventurer_02/adventurer_02_00.png",
               "enter": (60, 200), "exit": (30, 230)}},
    {"key": "lamp",    "name": "灯塔夜谈",    "pos": (416, 62),  "node": "night",
     "icon": "灯",    "desc": "雨夜，老渔夫的坦白",
     "walk": {"bg": "HR_Ocean Sunrise.png", "npc_pos": (340, 120), "npc_name": "老渔夫",
               "npc_img": "adventurer_03/adventurer_03_1.png",
               "enter": (60, 200), "exit": (30, 230)}},
]


class MapScene:
    """自由探索：浅海星海岸，玩家漫游触发探索点"""

    def __init__(self, memory=None, fragments=None, pois=None):
        self.t = 0.0
        self.memory = memory or {"主线": 0, "互动": 0, "残片": 0, "聆听": 0}
        self.fragments = fragments or []
        self.pois_done = set(pois or [])
        self.player = pygame.Vector2(config.W // 2, config.H * 0.60)
        self.near = None
        self.toast = ""
        self.toast_t = 0.0
        self.note_fx = []                       # 音符反馈粒子
        self.guide_t = 6.0                      # 新手引导时长
        # 背景星尘 + 海面涟漪
        from core.main import Star
        self.stars = [Star(config.W, config.H) for _ in range(80)]
        self.waves = [{"x": random.uniform(0, config.W), "ph": random.uniform(0, math.tau)}
                      for _ in range(30)]
        self.lamp_t = 0.0

    # ------------------------------------------------------------- 事件
    def event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = pygame.mouse.get_pos()
            mx, my = mx // config.SCALE, my // config.SCALE
            for p in POIS:
                if p["key"] not in self.pois_done and \
                        math.hypot(mx - p["pos"][0], my - p["pos"][1]) < 24:
                    audio.play("ui_ok")
                    self._enter_poi(p)
                    return
        if e.type != pygame.KEYDOWN:
            return
        if e.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE) and self.near:
            audio.play("ui_ok")
            self._enter_poi(self.near)
        elif pygame.K_1 <= e.key <= pygame.K_6:          # 数字键直达探索点
            idx = e.key - pygame.K_1
            if idx < len(POIS):
                p = POIS[idx]
                if p["key"] not in self.pois_done:
                    audio.play("ui_ok")
                    self._enter_poi(p)
        elif e.key == pygame.K_ESCAPE:
            from core.main import TitleScene
            self.game.set_scene(TitleScene())
        elif e.key in N.KEY_MAP:                # 地图任意处弹奏都有反馈
            note = N.KEY_MAP[e.key]
            audio.play("note_" + note)
            c = config.NOTE_COLORS[note]
            for _ in range(6):
                self.note_fx.append([self.player.x, self.player.y - 8,
                                     random.uniform(-40, 40), random.uniform(-60, -10),
                                     c, 0.6])

    def _enter_poi(self, poi):
        # 进入 POI 局部探索场景：角色在里面移动，走近 NPC 对话
        from core.story.walk_scene import WalkScene
        self.game.set_scene(WalkScene(poi, self.memory, self.fragments,
                                      list(self.pois_done)))

    def _all_done(self):
        return all(p["key"] in self.pois_done for p in POIS)

    # ------------------------------------------------------------- 更新
    def update(self, dt):
        self.t += dt
        self.lamp_t += dt
        for st in self.stars:
            st.update(dt, config.W, config.H)
        k = pygame.key.get_pressed()
        sp = 90
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
        # 音符粒子更新
        for fx in self.note_fx[:]:
            fx[0] += fx[2] * dt
            fx[1] += fx[3] * dt
            fx[5] -= dt
            if fx[5] <= 0:
                self.note_fx.remove(fx)
        if self.guide_t > 0:
            self.guide_t -= dt
        # 最近的未完成探索点
        self.near = None
        best = 46
        for p in POIS:
            if p["key"] in self.pois_done:
                continue
            d = math.hypot(p["pos"][0] - self.player.x, p["pos"][1] - self.player.y)
            if d < best:
                best = d
                self.near = p
        if self.toast_t > 0:
            self.toast_t -= dt
        audio.play_loop("bgm", 0.30)

    # ------------------------------------------------------------- 绘制
    def draw(self, s):
        sea_top = config.H - 84
        # 夜空
        for y in range(sea_top):
            t = y / sea_top
            r = int(14 * (1.5 - t * 0.6))
            g = int(24 * (1.5 - t * 0.6))
            b = int(60 * (1.5 - t * 0.6))
            s.fill((r, g, b), (0, y, config.W, 1))
        for st in self.stars:
            st.draw(s)
        # 海面
        sea = pygame.Surface((config.W, 84), pygame.SRCALPHA)
        for y in range(84):
            a = int(170 * (1 - y / 84))
            sea.fill((26, 62, 118, a), (0, y, config.W, 1))
        s.blit(sea, (0, sea_top))
        for wv in self.waves:
            x = int(wv["x"] + math.sin(self.t * 1.2 + wv["ph"]) * 8)
            y = sea_top + int((wv["ph"] * 37) % 70)
            pygame.draw.ellipse(s, (90, 130, 190, 60), (x, y, 26, 3))
        # 灯塔剪影
        lx, ly = config.W - 46, sea_top - 42
        pygame.draw.rect(s, (46, 52, 86), (lx - 3, ly + 12, 6, 40))
        pygame.draw.rect(s, (46, 52, 86), (lx - 5, ly + 4, 10, 14))
        blink = 0.5 + 0.5 * math.sin(self.lamp_t * 1.6)
        pygame.draw.circle(s, (255, 240, 180), (lx, ly), int(2 + blink * 3))
        # 探索点
        for i, p in enumerate(POIS):
            done = p["key"] in self.pois_done
            px, py = p["pos"]
            if done:
                pygame.draw.circle(s, (70, 80, 120), (px, py), 3)
                ui.text(s, f"{i + 1} ✓", (px, py - 15), size=8,
                        color=(90, 100, 140), center=True)
                continue
            pul = 0.6 + 0.4 * math.sin(self.t * 3 + px * 0.1)
            glow = tuple(int(c * pul) for c in (255, 215, 130))
            pygame.draw.circle(s, glow, (px, py), 8)
            pygame.draw.circle(s, (255, 235, 170), (px, py), 4)
            ui.text(s, f"[{i + 1}] {p['name']}", (px, py - 16), size=12,
                    color=(235, 225, 200), center=True)
            ui.text(s, p["icon"], (px, py), size=12, color=config.GOLD_HI, center=True)
            # 悬停弹窗（8px 清秀小字）
            mx, my = pygame.mouse.get_pos()
            if math.hypot(mx // config.SCALE - px, my // config.SCALE - py) < 30:
                box = pygame.Rect(px - 90, py + 18, 180, 22)
                ui.gold_panel(s, box, alpha=150)
                ui.text(s, f"[{i + 1}] {p['desc']}", box.center, size=8,
                        color=config.GOLD_HI, center=True)
        # 玩家（聆星者剪影：深蓝斗篷 + 背琴）
        px, py = int(self.player.x), int(self.player.y)
        pygame.draw.circle(s, (70, 100, 180), (px, py - 8), 6)
        pygame.draw.ellipse(s, (46, 66, 130), (px - 9, py - 4, 18, 14))
        pygame.draw.rect(s, (232, 200, 120), (px + 7, py - 12, 3, 14))    # 背上竖琴
        pygame.draw.circle(s, (255, 220, 150), (px + 8, py - 12), 2)
        # 音符反馈粒子
        for fx in self.note_fx:
            pygame.draw.circle(s, fx[4], (int(fx[0]), int(fx[1])), 2)
        # 新手引导
        if self.guide_t > 0:
            blink = 0.5 + 0.5 * math.sin(self.t * 5)
            if blink > 0.3:
                ui.text(s, "点击光点或按数字 1-6 · 进入地点探索 · WASD 移动找 NPC",
                        (config.W // 2, 60), size=12, color=config.GOLD_HI, center=True)
        # 互动提示
        if self.near:
            p = self.near
            idx = next((i for i, q in enumerate(POIS) if q["key"] == p["key"]), 0) + 1
            ui.text(s, f"[{idx}] {p['desc']} · 按 E / 鼠标 / 数字键", (config.W // 2, config.H - 24),
                    size=12, color=config.GOLD_HI, center=True)
            pygame.draw.rect(s, config.GOLD_HI,
                             (int(p["pos"][0] - 14), int(p["pos"][1]) - 18, 28, 2))
        # HUD：进度
        done_n = len(self.pois_done)
        total = len(POIS)
        ui.text(s, f"探索 {done_n}/{total} · 碎片 {len(self.fragments)}",
                (10, 8), size=12, color=(170, 195, 235))
        mem = self.memory
        ui.text(s, f"记忆 主线{mem.get('主线',0)} 互动{mem.get('互动',0)}"
                    f" 残片{mem.get('残片',0)} 聆听{mem.get('聆听',0)}",
                (10, 24), size=12, color=(140, 165, 210))
        # 全部完成：挽歌光点
        if self._all_done():
            pul = 0.6 + 0.4 * math.sin(self.t * 4)
            cx, cy = config.W // 2, 96
            pygame.draw.circle(s, (255, 215, 130), (cx, cy), int(10 + pul * 4))
            ui.text(s, "挽 歌", (cx, cy + 16), size=16,
                    color=config.GOLD_HI, center=True)
            if math.hypot(self.player.x - cx, self.player.y - cy) < 44:
                self.near = {"key": "finale", "name": "挽歌", "pos": (cx, cy),
                             "node": "finale", "desc": "弹响终章挽歌"}
                ui.text(s, "按 E · 弹响终章挽歌", (config.W // 2, config.H - 24),
                        size=12, color=config.GOLD_HI, center=True)
        if self.toast_t > 0:
            ui.text(s, self.toast, (config.W // 2, config.H - 44), size=12,
                    color=config.GOLD_HI, center=True)
