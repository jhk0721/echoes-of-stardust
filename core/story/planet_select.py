# 星球选择场景：选择记忆星球降落（上下键 + 回车 / 鼠标点击）
import math

import pygame

from core import config, audio, ui
from core.story.worlds import WORLDS


class PlanetSelectScene:
    """记忆星球选择：通关后解锁全部星球，自由降落"""

    def __init__(self):
        self.t = 0.0
        self.sel = 0
        # 星球顺序：主线五章 + 自由探索
        self.order = ["qianhai", "storm_city", "notre_dame", "flat", "finale_world",
                      "qiancao", "kassel", "friends", "library", "ward",
                      "math", "alive", "ditan", "paper_boat", "sea_old", "b612"]
        self.worlds = [(k, WORLDS[k]) for k in self.order if k in WORLDS]

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(self.worlds)
                audio.play("ui_move")
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(self.worlds)
                audio.play("ui_move")
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                audio.play("ui_ok")
                self._land(self.sel)
            elif e.key == pygame.K_ESCAPE:
                from core.main import TitleScene
                self.game.set_scene(TitleScene())
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = pygame.mouse.get_pos()
            for i, (k, w) in enumerate(self.worlds):
                r = pygame.Rect(20, 20 + i * 26, config.W - 40, 22)
                if r.collidepoint(mx // config.SCALE, my // config.SCALE):
                    self.sel = i
                    audio.play("ui_ok")
                    self._land(i)

    def _land(self, i):
        from core.story.map_scene import MapScene
        self.game.set_scene(MapScene(self.worlds[i][0]))

    def update(self, dt):
        self.t += dt
        audio.play_loop("bgm", 0.28)

    def draw(self, s):
        # 夜空背景
        for y in range(config.H):
            k = y / config.H
            s.fill((int(6 * (1 - k * 0.6)), int(10 * (1 - k * 0.6)),
                    int(24 * (1 - k * 0.5))), (0, y, config.W, 1))
        ui.text(s, "选择记忆星球 · 降落", (config.W // 2, 8), size=12,
                color=(200, 215, 245), center=True)
        for i, (k, w) in enumerate(self.worlds):
            r = pygame.Rect(20, 24 + i * 26, config.W - 40, 22)
            sel = i == self.sel
            ui.gold_panel(s, r, alpha=140 if sel else 70, selected=sel)
            t = w.get("tone", (10, 16, 48))
            pygame.draw.circle(s, (min(255, t[0] + 60), min(255, t[1] + 60),
                                   min(255, t[2] + 60)), (r.x + 12, r.centery), 5)
            ui.text(s, f"{w['name']} · {w['npc']}", (r.x + 24, r.centery),
                    size=12, color=ui.config.GOLD_HI if sel else ui.config.GOLD)
        ui.text(s, "↑↓ 选择 · 回车降落 · ESC 返回", (config.W // 2, config.H - 14),
                size=12, color=(140, 160, 200), center=True)
