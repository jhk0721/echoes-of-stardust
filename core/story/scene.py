# 星球剧情场景：对话 / 教学互动 / 选项分支 / 战斗衔接 / 挽歌结算
import math
import random

import pygame

from core import config, audio, ui
from core.story.planet import QIANHAI

TYPE_SPEED = 22          # 打字机：字符/秒
INTERACT_WAIT = 0.9      # 聆听互动最短时长

# 场景背景配置：不同剧情节点 = 不同天空/海面/太阳/雾（像素氛围）
BG = {
    "tutorial": {"sky": (8, 12, 36), "sea": (16, 34, 80), "sun": None, "fog": 0.2, "lamp": False},
    "open":     {"sky": (10, 16, 48), "sea": (18, 40, 90), "sun": None, "fog": 0.10, "lamp": True},
    "mend_net": {"sky": (16, 26, 64), "sea": (24, 52, 104),
                  "sun": (0.72, 0.20, (255, 220, 150)), "fog": 0.15, "lamp": False},
    "find_oar": {"sky": (12, 16, 42), "sea": (16, 30, 72), "sun": None, "fog": 0.50, "lamp": False},
    "battle":   {"sky": (6, 6, 22), "sea": (10, 12, 38), "sun": None, "fog": 0.30, "lamp": False},
    "shells":   {"sky": (44, 26, 56), "sea": (86, 66, 96),
                  "sun": (0.45, 0.28, (255, 190, 120)), "fog": 0.18, "lamp": False},
    "night":    {"sky": (4, 6, 20), "sea": (10, 18, 46), "sun": None, "fog": 0.08,
                  "lamp": True, "rain": True, "sit": True},
    "farewell": {"sky": (34, 22, 32), "sea": (56, 44, 64),
                  "sun": (0.50, 0.34, (255, 140, 90)), "fog": 0.25,
                  "rain": True, "sunrise": True},
    "finale":   {"sky": (8, 14, 42), "sea": (22, 48, 92), "sun": None, "fog": 0.18, "lamp": False},
}


class StoryScene:
    """浅海星《船》：按剧情节点推进，穿插织曲战斗与记忆收集"""

    def __init__(self, planet_key="qianhai", scene_key="open", memory=None, fragments=None,
                 mode="story", poi_key=None):
        self.planet = QIANHAI
        self.scene_key = scene_key
        self.scene = self.planet["scenes"][scene_key]
        self.bg = BG.get(scene_key, BG["open"])
        self.mode = mode                # story 线性 / poi 探索点 / tutorial 教程
        self.poi_key = poi_key
        self.flash = 0.0                # 互动成功白闪
        self.memory = memory or {"主线": 0, "互动": 0, "残片": 0, "聆听": 0}
        self.fragments = fragments or []
        self.state = "lines"          # lines / interact / choices / battle / finale / done
        self.line_i = 0
        self.char_i = 0
        self.t = 0.0
        self.fade_in = 0.0
        self.sel = 0
        self.typing = True
        self.done_played = False
        self.ship_t = 0.0
        self.end_t = 0.0
        self.toast = ""
        self.toast_t = 0.0
        # 环境：星尘 + 浅海倒影点 + 灯塔光
        self.stars = []
        from core.main import Star
        for _ in range(90):
            self.stars.append(Star(config.W, config.H))
        self.lamp = {"x": config.W - 60, "y": 60, "t": 0.0}
        # 雨丝（雨景节点启用）
        self.drops = [{"x": random.uniform(0, config.W), "y": random.uniform(0, config.H),
                       "l": random.uniform(6, 14), "spd": random.uniform(180, 320)}
                      for _ in range(60)]
        self.ship_parts = []
        self._ship_phase = 0

    # ------------------------------------------------------------------ 事件
    def event(self, e):
        if e.type != pygame.KEYDOWN:
            return
        if self.state == "lines":
            if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                cur = ""
                if self._lines():
                    cur = self._lines()[min(self.line_i, len(self._lines()) - 1)].get("text", "")
                if self.char_i < len(cur):       # 打字中：先显示全句
                    self.char_i = 999
                else:
                    audio.play("ui_move")
                    self._advance()
            elif e.key == pygame.K_ESCAPE:
                self._back_title()
            elif e.key == pygame.K_s:
                audio.play("ui_select")
                self.skip_node()
        elif self.state == "interact":
            self._interact_event(e)
        elif self.state == "choices":
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(self._choices()); audio.play("ui_move")
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(self._choices()); audio.play("ui_move")
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                audio.play("ui_ok"); self._choose()

    def _interact_event(self, e):
        it = self.scene["interact"]
        if it["type"] == "note" and e.key == self._note_key(it["note"]):
            audio.play("note_" + it["note"])
            self._finish_interact()
        elif it["type"] == "listen" and e.key == pygame.K_u:
            audio.play("resonance")
            self._finish_interact()

    @staticmethod
    def _note_key(note):
        return {"wind": pygame.K_j, "fire": pygame.K_k,
                "water": pygame.K_l, "earth": pygame.K_i}[note]

    # ------------------------------------------------------------------ 推进
    def _lines(self):
        return self.scene.get("lines", [])

    def _choices(self):
        return self.scene.get("choices", [])

    def _advance(self):
        self.line_i += 1
        self.char_i = 0
        if self.line_i >= len(self._lines()):
            self._lines_done()

    def _lines_done(self):
        sc = self.scene
        if sc.get("choices"):
            self.state = "choices"
            self.sel = 0
        elif sc.get("interact"):
            self.state = "interact"
            self._toast(sc["interact"]["desc"])
        elif sc.get("battle"):
            self._start_battle(sc["battle"])
        elif sc.get("finale"):
            self.state = "finale"
            self._ship_phase = 0
        else:
            self._advance_scene()

    def _choose(self):
        # 选项分支：播对应 lines，记录碎片，移除选项防死循环
        choice = self._choices()[self.sel]
        self.scene = dict(self.scene)
        self.scene["lines"] = choice["lines"]
        self.scene.pop("choices", None)
        if choice.get("fragment") and "再见的见" not in self.fragments:
            self.fragments.append("再见的见")
            self.memory["残片"] += 1
            self._toast("获得记忆残片 · 再见的见")
        self.state = "lines"
        self.line_i = 0
        self.char_i = 0

    def _start_battle(self, enemy_key):
        self.state = "battle"
        audio.stop_all_loops()                  # 战斗环境无雨
        from core.main import BattleScene
        bs = BattleScene(enemy_key)
        bs.on_win = lambda: self._battle_won()
        self.game.set_scene(bs)

    def _battle_won(self):
        self._advance_scene()
        if self.mode != "poi":
            self.game.set_scene(self)      # poi 模式内部已回地图，勿覆盖

    def _advance_scene(self):
        # 完成当前节点：记维度 + 碎片 + 存档 + 进下一节点 / 回地图
        sc = self.scene
        if self.mode in ("poi", "tutorial"):
            self._poi_done()
            return
        dim = sc.get("dim")
        if dim:
            self.memory[dim] = min(99, self.memory.get(dim, 0) + 1)
        frag = sc.get("fragments")
        if frag and frag not in self.fragments:
            self.fragments.append(frag)
            self._toast(f"获得记忆残片 · {frag}")
        nxt = sc.get("next")
        if nxt:
            self.scene_key = nxt
            self.scene = self.planet["scenes"][nxt]
            self.state = "lines"
            self.line_i = 0
            self.char_i = 0
        else:
            self.state = "done"
            self._save()
        self._save()

    def _finish_interact(self):
        sc = self.scene
        done = sc.get("done", [])
        self.scene = dict(sc)
        self.scene["lines"] = done
        self.scene["interact"] = None
        self.state = "lines"
        self.line_i = 0
        self.char_i = 0
        self.flash = 0.18                 # 成功反馈：闪白
        if done:
            self._toast(done[0].get("who", "") + "：成功了！")

    def _poi_done(self):
        """探索点完成：标记 + 存档 + 回地图"""
        from core import save as S
        d = S.load() or {}
        pois = list(d.get("pois", []))
        if self.poi_key and self.poi_key not in pois:
            pois.append(self.poi_key)
        # 教程节点也计入主线记忆
        dim = self.scene.get("dim")
        if dim:
            self.memory[dim] = min(99, self.memory.get(dim, 0) + 1)
        frag = self.scene.get("fragments")
        if frag and frag not in self.fragments:
            self.fragments.append(frag)
            self._toast(f"获得记忆残片 · {frag}")
        S.save({"planet": "qianhai", "scene": self.scene_key,
                "fragments": self.fragments, "memory": self.memory,
                "pois": pois, "done": False, "unlocked": ["qianhai"]})
        from core.story.map_scene import MapScene
        self.game.set_scene(MapScene(self.memory, self.fragments, pois))

    def _save(self):
        from core import save as S
        S.save({"planet": "qianhai", "scene": self.scene_key,
                "fragments": self.fragments, "memory": self.memory,
                "done": self.state == "done", "unlocked": ["qianhai"]})

    def _back_title(self):
        from core.main import TitleScene
        self.game.set_scene(TitleScene())

    def skip_node(self):
        """一键跳过：快进当前节点（右上角 [S]）"""
        if self.state in ("lines", "choices"):
            self._advance_scene()
        elif self.state == "interact":
            self._finish_interact()
        elif self.state == "finale":
            self.done_played = True
            self.state = "done"
            self.end_t = 0.0
            self._save()

    def _toast(self, t):
        self.toast = t
        self.toast_t = 2.0

    # ------------------------------------------------------------------ 更新
    def update(self, dt):
        self.t += dt
        self.fade_in = min(1.0, self.fade_in + dt * 1.2)
        for st in self.stars:
            st.update(dt, config.W, config.H)
        self.lamp["t"] += dt
        # 雨声跟随场景（幂等）
        if self.bg.get("rain"):
            audio.play_loop("rain", 0.35)
        else:
            audio.stop_loop("rain")
        # 雨丝下落
        if self.bg.get("rain"):
            for d in self.drops:
                d["y"] += d["spd"] * dt
                d["x"] -= d["spd"] * dt * 0.22       # 风向左斜
                if d["y"] > config.H + 16:
                    d["y"] = -16
                    d["x"] = random.uniform(0, config.W + 20)
        if self.state == "lines" and self.typing:
            self.char_i += TYPE_SPEED * dt
        if self.state == "finale":
            self._update_ship(dt)
            if self.ship_t > 4.5 and not self.done_played:
                self.done_played = True
                self.state = "done"
                self.end_t = 0.0
                self._save()
        self.flash = max(0.0, self.flash - dt)
        if self.state == "done":
            self.end_t += dt
            if self.end_t > 3.5:
                self._back_title()
        if self.toast_t > 0:
            self.toast_t -= dt
        if not pygame.mixer.get_busy():
            audio.play("whisper", 0.25)

    def _update_ship(self, dt):
        self.ship_t += dt
        if self.ship_t > 1.0 and self._ship_phase == 0:
            self._ship_phase = 1
        # 星光船：光点汇聚 → 右上行进
        for i in range(26):
            if self.ship_t > 0.5 + i * 0.04:
                ang = random.uniform(0, math.tau)
                r = random.uniform(2, 26)
                self.ship_parts.append([config.W * 0.28 + math.cos(ang) * r,
                                        config.H * 0.62 + math.sin(ang) * r * 0.5,
                                        random.uniform(0.5, 1.5)])
        for p in self.ship_parts:
            p[0] += dt * 26
            p[1] -= dt * 5 + math.sin(self.ship_t * 3 + p[0]) * 0.4

    # ------------------------------------------------------------------ 绘制
    def draw(self, s):
        self._draw_bg(s)
        self._draw_npc(s)
        if self.state in ("lines", "choices"):
            self._draw_dialog(s)
        elif self.state == "interact":
            self._draw_dialog(s)
            self._draw_interact(s)
        elif self.state == "finale":
            self._draw_finale(s)
        elif self.state == "done":
            self._draw_result(s)
        if self.toast_t > 0:
            ui.text(s, self.toast, (config.W // 2, config.H - 34), size=12,
                    color=config.GOLD_HI, center=True)
        if self.flash > 0:
            f = pygame.Surface((config.W, config.H), pygame.SRCALPHA)
            f.fill((255, 245, 200, int(160 * self.flash / 0.18)))
            s.blit(f, (0, 0))

    def _draw_bg(self, s):
        bg = self.bg
        sea_top = config.H - 90
        # 天空渐变（顶→海平线，调亮让背景可见）
        for y in range(sea_top):
            t = y / sea_top
            r = min(255, int(bg["sky"][0] * (1.5 - t * 0.6)))
            g2 = min(255, int(bg["sky"][1] * (1.5 - t * 0.6)))
            b2 = min(255, int(bg["sky"][2] * (1.5 - t * 0.6)))
            s.fill((r, g2, b2), (0, y, config.W, 1))
        # 星尘
        for st in self.stars:
            st.draw(s)
        # 太阳 / 晨光（日出节点：从海平线下缓缓升起）
        sun = bg.get("sun")
        if sun:
            sx, sy, scol = int(sun[0] * config.W), int(sun[1] * sea_top), sun[2]
            if bg.get("sunrise"):
                rise = min(1.0, self.t / 7)
                sy = int(sy + (1 - rise) * 26)          # 缓慢升起
            else:
                rise = 1.0
            for rr, a in ((28, int(14 * rise)), (18, int(30 * rise)), (10, int(55 * rise))):
                circ = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
                pygame.draw.circle(circ, (*scol, a), (rr, rr), rr)
                s.blit(circ, (sx - rr, sy - rr))
            pygame.draw.circle(s, scol, (sx, sy), 9)
            if bg.get("sunrise"):                       # 朝霞映海
                glow = pygame.Surface((config.W, 40), pygame.SRCALPHA)
                for y in range(40):
                    glow.fill((*scol, int(36 * (1 - y / 40) * rise)),
                              (0, y, config.W, 1))
                s.blit(glow, (0, sea_top - 20))
        # 浅海：底部渐变水面 + 星点倒影
        sea = pygame.Surface((config.W, 90), pygame.SRCALPHA)
        for y in range(90):
            a = int(160 * (1 - y / 90))
            sea.fill((min(255, bg["sea"][0] * 1.25), min(255, bg["sea"][1] * 1.25),
                      min(255, bg["sea"][2] * 1.25), a), (0, y, config.W, 1))
        s.blit(sea, (0, sea_top))
        for i in range(40):                      # 倒影星点
            x = (i * 53.7 + self.t * 6) % config.W
            y = config.H - 12 - ((i * 37.3 + self.t * 4) % 66)
            pygame.draw.circle(s, (140, 170, 220), (int(x), int(y)), 1)
        # 灯塔（剪影 + 微光）
        if bg.get("lamp"):
            lx, ly = config.W - 46, sea_top - 40
            pygame.draw.rect(s, (40, 44, 70), (lx - 3, ly + 12, 6, 40))
            pygame.draw.rect(s, (40, 44, 70), (lx - 5, ly + 4, 10, 14))
            blink = 0.5 + 0.5 * math.sin(self.t * 1.6)
            pygame.draw.circle(s, (255, 240, 180), (lx, ly), int(2 + blink * 3))
            pygame.draw.circle(s, (255, 240, 180, 60), (lx, ly), int(6 + blink * 5))
        # 岸边两人剪影（雨夜：老渔夫 + 聆星者坐在海边）
        if bg.get("sit"):
            sk = (8, 12, 30)
            x1, y1 = int(config.W * 0.40), config.H - 64
            x2, y2 = int(config.W * 0.52), config.H - 62
            # 老渔夫（大）：头 + 蓑衣身 + 斗笠
            pygame.draw.circle(s, sk, (x1, y1), 7)
            pygame.draw.ellipse(s, sk, (x1 - 13, y1 + 4, 26, 18))
            pygame.draw.ellipse(s, sk, (x1 - 11, y1 - 8, 22, 8))   # 斗笠
            # 聆星者（小，背竖琴）：头 + 斗篷 + 琴凸起
            pygame.draw.circle(s, sk, (x2, y2), 6)
            pygame.draw.ellipse(s, sk, (x2 - 10, y2 + 3, 20, 14))
            pygame.draw.rect(s, sk, (x2 + 8, y2 - 8, 4, 16))       # 背上竖琴
            # 脚下浪花
            for i in range(4):
                wxx = x1 + i * 22 - 6
                pygame.draw.ellipse(s, (70, 90, 140, 40), (wxx, config.H - 20 + i, 40, 6))
        # 雨丝（斜向）
        if bg.get("rain"):
            for d in self.drops:
                pygame.draw.line(s, (140, 170, 210),
                                 (int(d["x"]), int(d["y"])),
                                 (int(d["x"] - d["l"] * 0.22), int(d["y"] - d["l"])), 1)
        # 雾层（降低，保证背景可见）
        fog = bg.get("fog", 0)
        if fog > 0.02:
            f = pygame.Surface((config.W, config.H), pygame.SRCALPHA)
            f.fill((200, 210, 230, int(70 * fog)))
            s.blit(f, (0, 0))
        # 右上角：一键跳过
        f8 = ui.load_font(12)
        sk = f8.render("跳过 [S]", True, (150, 165, 205))
        s.blit(sk, (config.W - sk.get_width() - 8, 8))

    def _draw_npc(self, s):
        # 记忆体：半透明光团 + 名字标签（说话人）
        who = ""
        if self.state in ("lines", "choices") and self._lines():
            who = self._lines()[min(self.line_i, len(self._lines()) - 1)].get("who", "")
        if not who or who in ("", "母亲"):
            return
        x, y = config.W - 120, config.H - 150
        r = 18 + math.sin(self.t * 2) * 2
        # 光晕 + 光团（记忆体：半透明、边缘柔和光晕）
        for rr, a in ((r + 10, 20), (r + 6, 34), (r + 2, 60)):
            circ = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
            pygame.draw.circle(circ, (170, 205, 245, a), (rr, rr), rr)
            s.blit(circ, (int(x - rr), int(y - rr)))
        pygame.draw.circle(s, (200, 225, 255), (int(x), int(y)), int(r))
        pygame.draw.circle(s, (240, 250, 255), (int(x - r * 0.3), int(y - r * 0.3)), int(r * 0.4))
        ui.text(s, who, (int(x), int(y + r + 12)), size=12,
                color=(190, 215, 250), center=True)

    def _draw_dialog(self, s):
        # 底部紧凑对话框：说话人 + 打字机文本
        who = ""
        if self._lines():
            who = self._lines()[min(self.line_i, len(self._lines()) - 1)].get("who", "")
        box = pygame.Rect(10, config.H - 56, config.W - 20, 48)
        ui.gold_panel(s, box, alpha=150)
        if who:
            ui.text(s, who, (18, config.H - 50), size=10, color=config.GOLD_HI)
        text = ""
        if self._lines():
            text = self._lines()[min(self.line_i, len(self._lines()) - 1)].get("text", "")
        shown = text[:int(self.char_i)]
        ui.text(s, shown, (18, config.H - 38), size=12, color=config.STAR)
        # 提示箭头
        if self.char_i >= len(text):
            blink = 0.5 + 0.5 * math.sin(self.t * 5)
            if blink > 0.3:
                ui.text(s, "▼", (config.W - 22, config.H - 20), size=10,
                        color=config.GOLD if self.state == "lines" else (100, 120, 160))
        # 选项
        if self.state == "choices":
            for i, ch in enumerate(self._choices()):
                r = pygame.Rect(46, 84 + i * 26, config.W - 92, 20)
                ui.gold_panel(s, r, alpha=110, selected=(i == self.sel))
                ui.text(s, ch["text"], r.center, size=12,
                        color=config.GOLD_HI if i == self.sel else config.GOLD, center=True)

    def _draw_interact(self, s):
        # 互动提示条
        it = self.scene.get("interact")
        if not it:
            return
        r = pygame.Rect(config.W // 2 - 120, 70, 240, 26)
        ui.gold_panel(s, r, alpha=130, selected=True)
        ui.text(s, it["desc"], r.center, size=12, color=config.GOLD_HI, center=True)
        # 按键高亮
        if it["type"] == "note":
            k = "J" if it["note"] == "wind" else "K" if it["note"] == "fire" else \
                "L" if it["note"] == "water" else "I"
            ui.text(s, f"按下 {k}", (config.W // 2, 108), size=24,
                    color=config.NOTE_COLORS[it["note"]], center=True)
        else:
            ui.text(s, "按住 U", (config.W // 2, 108), size=24,
                    color=config.AURA, center=True)

    def _draw_finale(self, s):
        # 星光船 + 字幕
        for p in self.ship_parts:
            pygame.draw.circle(s, (255, 245, 200), (int(p[0]), int(p[1])), max(1, int(p[2])))
        if self.ship_t > 0.5:
            ui.text(s, "一艘由星光凝结的船，驶向海天之间", (config.W // 2, 40),
                    size=12, color=(200, 225, 255), center=True)
        if self.ship_t > 2.2:
            ui.text(s, "「弹琴的人，你叫什么名字？」", (config.W // 2, config.H // 2),
                    size=24, color=config.GOLD_HI, center=True)

    def _draw_result(self, s):
        # 挽歌结算
        f = pygame.Surface((config.W, config.H), pygame.SRCALPHA)
        f.fill((4, 8, 24, int(230 * min(1.0, self.end_t * 2))))
        s.blit(f, (0, 0))
        ui.text(s, "挽 歌 奏 响", (config.W // 2, 60), size=36, color=config.GOLD, center=True)
        ui.text(s, "浅海星 · 《船》 · 记忆完整度 100%", (config.W // 2, 110),
                size=12, color=config.STAR, center=True)
        ui.text(s, f"主线 {self.memory.get('主线', 0)} · 互动 {self.memory.get('互动', 0)}"
                    f" · 残片 {self.memory.get('残片', 0)} · 聆听 {self.memory.get('聆听', 0)}",
                (config.W // 2, 132), size=12, color=config.AURA, center=True)
        if self.fragments:
            ui.text(s, "碎片：" + " · ".join(self.fragments), (config.W // 2, 154),
                    size=12, color=config.GOLD_HI, center=True)
        ui.text(s, "「记住他们。但别成为他们。」", (config.W // 2, 190),
                size=12, color=(200, 225, 255), center=True)
        if self.end_t > 2.0:
            blink = 0.5 + 0.5 * math.sin(self.t * 4)
            if blink > 0.3:
                ui.text(s, "回到宇宙……", (config.W // 2, 232), size=12,
                        color=(140, 160, 200), center=True)
