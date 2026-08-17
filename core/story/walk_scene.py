# 局部探索场景：进入 POI 地点 → WASD 走到 NPC 旁 → 按 E 对话
# 星露谷式体验：角色在场景里自由移动，NPC 站在场景中等待互动
import math
import os

import pygame

from core import config, audio, ui
from core.story import sd, ut

NPC_DIR = os.path.join(config.BASE, "assets", "_new", "Lively_NPCs_v3.0",
                       "individual sprites", "medieval")
NEW_DIR = os.path.join(config.BASE, "assets", "_new")
WR = os.path.join(NEW_DIR, "Bitcrawl_Free_Roguelike_v1", "Characters",
                  "Normal_Outline_Sheet", "Animation_Normal_Outline_Wraith.png")


def _bg_img(name, planet_key="qianhai", tone=(10, 16, 48)):
    """场景背景：优先星露谷瓦片拼接的星球专属背景，兜底旧素材"""
    night = "night" in name
    boat = "boat" in name
    try:
        return sd.scene_bg(planet_key, tone, night=night, boat=boat)
    except Exception:
        pass
    if name.startswith("sea"):
        return None
    p = os.path.join(NEW_DIR, name)
    if os.path.exists(p):
        img = pygame.image.load(p)
        return pygame.transform.scale(img, (config.W, config.H))
    return None


def _npc_img(path, npc_name="记忆体", size=(32, 64)):
    """NPC 图：优先星露谷角色站立帧，兜底旧素材/Wraith/光团"""
    img = sd.char_idle(npc_name)
    if img:
        return img
    try:
        if path and "Wraith" in path:
            sheet = pygame.image.load(path).convert_alpha()
            img = sheet.subsurface((0, 0, 16, 16))
        elif path and os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
        else:
            return None
        return pygame.transform.scale(img, size)
    except Exception:
        return None


class WalkScene:
    """POI 局部场景：进入 → 自由移动 → 走近 NPC 按 E 对话 → 出口回大世界"""

    def __init__(self, poi, memory=None, fragments=None, pois_done=None, planet_key="qianhai"):
        self.poi = poi
        self.planet_key = planet_key
        from core.story.worlds import WORLDS
        self.tone = WORLDS.get(planet_key, {}).get("tone", (10, 16, 48))
        self.memory = memory or {"主线": 0, "互动": 0, "残片": 0, "聆听": 0}
        self.fragments = fragments or []
        self.pois_done = set(pois_done or [])
        w = poi.get("walk", {})
        self.bg = _bg_img(w.get("bg", "sea"), planet_key, self.tone)
        # 玩家：从入口进入，使用 Undertale 风格 4向走路动画
        self.player = pygame.Vector2(w.get("enter", (60, 200)))
        self.player_frames = ut.get_char_frames("protagonist", scale=2)
        self.player_frame_idx = 0
        self.player_anim_timer = 0.0
        self.player_dir = 'down'  # 当前朝向
        self.player_moving = False
        # NPC：站在场景中
        self.npc_pos = w.get("npc_pos", (300, 130))
        self.npc_name = w.get("npc_name", "记忆体")
        self.npc_img = _npc_img(w.get("npc_img", ""), self.npc_name,
                                w.get("npc_size", (32, 64)))
        # NPC 动作状态机
        self.npc_action_type = ut.NPC_ACTIONS.get(self.npc_name, "idle")
        self.npc_action_timer = 0.0
        self.npc_action_frame = 0
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
        
        # 玩家移动与动画
        k = pygame.key.get_pressed()
        sp = 95
        dx = dy = 0
        moving = False
        if k[pygame.K_a] or k[pygame.K_LEFT]:
            dx -= sp * dt
            self.player_dir = 'left'
            moving = True
        if k[pygame.K_d] or k[pygame.K_RIGHT]:
            dx += sp * dt
            self.player_dir = 'right'
            moving = True
        if k[pygame.K_w] or k[pygame.K_UP]:
            dy -= sp * dt
            self.player_dir = 'up'
            moving = True
        if k[pygame.K_s] or k[pygame.K_DOWN]:
            dy += sp * dt
            self.player_dir = 'down'
            moving = True
        
        self.player.x += dx
        self.player.y += dy
        self.player.x = max(16, min(config.W - 16, self.player.x))
        self.player.y = max(50, min(config.H - 16, self.player.y))
        
        # 玩家走路动画
        self.player_moving = moving
        if moving:
            self.player_anim_timer += dt * 10  # 10帧/秒
            if self.player_anim_timer >= 1.0:
                self.player_anim_timer -= 1.0
                self.player_frame_idx = (self.player_frame_idx + 1) % 3  # 3个走路帧
        else:
            self.player_frame_idx = 0
            self.player_anim_timer = 0.0
        
        # NPC 动作动画
        self.npc_action_timer += dt
        if self.npc_action_timer >= 0.5:  # 0.5秒切换一次动作帧
            self.npc_action_timer -= 0.5
            self.npc_action_frame = (self.npc_action_frame + 1) % 2
        
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
            w2, h2 = self.npc_img.get_size()
            s.blit(self.npc_img, (int(nx - w2 / 2), int(ny - h2 + 6)))
        else:
            pygame.draw.circle(s, (200, 225, 255), (int(nx), int(ny)), 14)
        ui.text(s, self.npc_name, (int(nx), int(ny + 16)), size=12,
                color=(235, 235, 250), center=True)
        if self.near_npc():
            pygame.draw.circle(s, config.GOLD_HI, (int(nx), int(ny)), 30, 1)
        # 玩家（聆星者）：使用 4向走路动画
        px, py = int(self.player.x), int(self.player.y)
        dir_frames = self.player_frames.get(self.player_dir, self.player_frames.get('down', []))
        if dir_frames:
            # 站立帧是第0帧，走路帧是第1-3帧
            frame_idx = 0 if not self.player_moving else (self.player_frame_idx + 1)
            frame_idx = min(frame_idx, len(dir_frames) - 1)
            img = dir_frames[frame_idx]
            w2, h2 = img.get_size()
            s.blit(img, (px - w2 // 2, py - h2 + 4))
        else:
            # 兜底：程序化绘制
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
