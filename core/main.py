# 主程序：场景管理器 / 主界面（星尘粒子增强版）/ 织曲战斗
import math
import os
import random

import pygame

from core import config, audio, ui
from core.combat import finale as F
from core.combat import notes as N
from core.combat import rhythm as R
from native import planet_shader as PS

IMG = {}
PART = {}      # 粒子族：{"star": [surf...], "circle": [...], ...}（Kenney CC0）
SCALE_CACHE = {}


def img(name):
    return IMG[name]


def _load_particles():
    """加载 Kenney 粒子包（透明背景版），按族名归类并预缩到 64px"""
    base = os.path.join(config.PARTICLES, "PNG (Transparent)")
    if not os.path.isdir(base):
        return {}
    fam = {}
    for fn in sorted(os.listdir(base)):
        if fn.endswith(".png"):
            name = fn[:-4]
            try:
                img = pygame.image.load(os.path.join(base, fn)).convert_alpha()
                img = pygame.transform.smoothscale(img, (64, 64))
                fam.setdefault(name.split("_")[0], []).append(img)
            except Exception:
                pass
    return fam


def part(imgs, i, scale=1.0):
    """粒子图带缩放缓存（超限自动清空，防内存膨胀）"""
    if len(SCALE_CACHE) > 400:
        SCALE_CACHE.clear()
    img = imgs[i % len(imgs)]
    if scale == 1.0:
        return img
    key = (id(img), scale)
    if key not in SCALE_CACHE:
        w = max(1, int(img.get_width() * scale))
        h = max(1, int(img.get_height() * scale))
        SCALE_CACHE[key] = pygame.transform.smoothscale(img, (w, h))
    return SCALE_CACHE[key]


# ---------------------------------------------------------------------------
# 星尘粒子（Kenney 粒子图 + 彩色星点混合 · 视差滚动 + 闪烁 + 流星）
# ---------------------------------------------------------------------------
class Star:
    DOTS = [(190, 205, 255), (255, 228, 175), (178, 210, 255), (255, 185, 200),
            (208, 188, 255), (255, 215, 160), (170, 255, 220)]   # 冷暖混合不单调

    def __init__(self, w, h):
        self.w = self.h = 0
        self.reset(w, h)

    def reset(self, w, h):
        self.w, self.h = w, h
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.z = random.uniform(0.1, 1.0)          # 深度：远=慢/小，近=快/亮
        self.mode = "dot" if random.random() < 0.65 else "img"
        self.phase = random.uniform(0, math.tau)
        self.speed = random.uniform(4, 12) * self.z
        if self.mode == "dot":
            self.col = random.choice(self.DOTS)
            self.r2 = max(0.6, random.uniform(0.6, 1.8) * (0.4 + self.z))
            self.img = None
        else:
            pool = PART.get("star", []) + PART.get("circle", [])
            self.img = random.choice(pool) if pool else None
            self.size = max(3, int(random.choice([4, 5, 6, 8]) * (0.5 + self.z)))

    def update(self, dt, w, h):
        self.phase += dt * 0.8
        self.y += self.speed * dt
        if self.y > h + 2:
            self.y = -2
            self.x = random.uniform(0, w)

    def draw(self, s):
        if self.mode == "dot":
            bright = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(self.phase))
            c = (int(self.col[0] * bright), int(self.col[1] * bright),
                 int(self.col[2] * bright))
            pygame.draw.circle(s, c, (int(self.x), int(self.y)), max(1, int(self.r2)))
            return
        if self.img is None:
            return
        a = int(50 + 80 * (0.5 + 0.5 * math.sin(self.phase)))
        key = (id(self.img), self.size)
        if key not in SCALE_CACHE:
            SCALE_CACHE[key] = pygame.transform.smoothscale(self.img, (self.size, self.size))
        im = SCALE_CACHE[key]
        im.set_alpha(a)
        s.blit(im, (int(self.x - self.size / 2), int(self.y - self.size / 2)))


# ---------------------------------------------------------------------------
# 游戏入口
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(44100, -16, 1, 512)
        except pygame.error:
            try:
                pygame.mixer.init()
            except pygame.error:
                pass
        from core import audio as A
        A.load_all()                      # 预加载程序化音效（此前从未调用 → 全静音）
        self.screen = pygame.display.set_mode((config.SW, config.SH), pygame.RESIZABLE)
        self.fullscreen = False
        pygame.display.set_caption("星尘回响 · Echoes of Stardust")
        self.surf = pygame.Surface((config.W, config.H))
        self.clock = pygame.time.Clock()
        self.scene = None
        self.running = True
        for name in ("harp_real",):
            try:
                IMG[name] = pygame.image.load(f"{config.SPRITES}/{name}.png")
            except Exception:
                pass
        PART.update(_load_particles())

    def now(self):
        return pygame.time.get_ticks()

    def set_scene(self, s):
        s.game = self
        self.scene = s

    def run(self):
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.screen = pygame.display.set_mode((config.SW, config.SH),
                                                              pygame.RESIZABLE)
                elif self.scene:
                    self.scene.event(e)
            if self.scene:
                self.scene.update(dt)
            self.surf.fill(config.INK)
            if self.scene:
                self.scene.draw(self.surf)
            pygame.transform.scale(self.surf, self.screen.get_size(), self.screen)
            pygame.display.flip()
        pygame.quit()


# 八种星球主色（亮色系：气态×3 / 岩石×3 / 类地×2）
PLANET_COLS = [(255, 205, 110), (120, 190, 255), (215, 170, 255),
               (170, 135, 105), (195, 105, 85), (150, 152, 160),
               (65, 125, 235), (200, 203, 210)]


# ---------------------------------------------------------------------------
# 记忆星球：网格均匀分布（4×2 槽位）· 生灭状态机（淡入→活跃→淡出→静默）
# ---------------------------------------------------------------------------
class Planet:
    SLOTS = 8

    def __init__(self, w, h, slot):
        self.w, self.h = w, h
        self.slot = slot
        cols, rows = 4, 2
        gw, gh = w / cols, h / rows
        self.rx0 = (slot % cols) * gw + 20          # 活动区域：格子内留边距
        self.ry0 = (slot // cols) * gh + 30
        self.rx1 = min(w - 20, (slot % cols + 1) * gw - 20)
        self.ry1 = min(h - 18, (slot // cols + 1) * gh - 14)
        self.state = "in"
        self.phase_t = random.uniform(0, 1.2)
        self.hidden_t = random.uniform(2, 4)
        self.ripples = []
        self.reset()

    def reset(self, others=()):
        # 同色去重（8 色轮流用，避免同色聚集）
        used = {p.col_i for p in others if p is not self}
        free = [i for i in range(8) if i not in used]
        self.col_i = random.choice(free or [random.randrange(8)])
        self.col = PLANET_COLS[self.col_i]
        # 新位置：仍在自己的网格区域内（保证全局均匀）
        self.x = random.uniform(self.rx0, self.rx1)
        self.y = random.uniform(self.ry0, self.ry1)
        self.vx = random.uniform(-7, 7)
        self.vy = random.uniform(-6, 6)
        if abs(self.vx) < 2:
            self.vx += random.choice((-4, 4))
        if abs(self.vy) < 2:
            self.vy += random.choice((-3, 3))
        self.size = random.randint(10, 16)          # 星球小星点：短暂出现又消散
        self.life = random.uniform(4, 8)            # 短暂亮起 4~8 秒 → 消散 → 他处再现
        self.ripples = []
        for _ in range(random.randint(2, 3)):
            self.ripples.append({
                "t": random.random(),
                "maxr": self.size * random.uniform(1.6, 2.6),
                "speed": random.uniform(0.3, 0.5),
                "width": 1,
            })

    def update(self, dt, planets):
        self.phase_t += dt
        if self.state == "in":                       # 淡入
            if self.phase_t >= 1.5:
                self.state = "alive"
                self.phase_t = 0
        elif self.state == "alive":                  # 活跃：区域内漫游
            self.x += self.vx * dt
            self.y += self.vy * dt
            if self.x < self.rx0 or self.x > self.rx1:
                self.vx *= -1
            if self.y < self.ry0 or self.y > self.ry1:
                self.vy *= -1
            for rp in self.ripples:
                rp["t"] += rp["speed"] * dt
                if rp["t"] >= 1.0:
                    rp["t"] = 0.0
            if self.phase_t >= self.life:
                self.state = "out"
                self.phase_t = 0
        elif self.state == "out":                    # 淡出
            if self.phase_t >= 1.5:
                self.state = "hidden"
                self.phase_t = 0
                self.reset(planets)                  # 换新位置/配色（同区域）
        elif self.state == "hidden":                 # 静默期：完全消失
            if self.phase_t >= self.hidden_t:
                self.state = "in"
                self.phase_t = 0

    def draw(self, s, mouse):
        # 生灭淡入淡出
        if self.state == "hidden":
            return
        if self.state == "in":
            fade = self.phase_t / 1.5
        elif self.state == "out":
            fade = 1 - self.phase_t / 1.5
        else:
            fade = 1.0
        if fade <= 0.02:
            return
        # 星球本体（逐像素渲染：明暗分明、无伪影）
        hover = mouse is not None and \
            math.hypot(mouse[0] - self.x, mouse[1] - self.y) < self.size + 16
        r = int(self.size * (1.15 if hover else 1.0))
        key = ("planet_final", self.col_i, r)
        if key not in SCALE_CACHE:
            SCALE_CACHE[key] = PS.render_python(r, self.col_i, self.col)
        im = SCALE_CACHE[key]
        im.set_alpha(int(255 * fade))
        s.blit(im, (int(self.x - im.get_width() / 2), int(self.y - im.get_height() / 2)))


# ---------------------------------------------------------------------------
# 动态五线谱：5 条波动白线 + 漂浮音符（二分/四分/八分）
# ---------------------------------------------------------------------------
class Staff:
    LINES = 5
    GAP = 8

    def __init__(self, w):
        self.base = 172          # 中下部，瀑布波浪（比底部上调）
        self.amp = 4
        self.tilt = 0.05         # 从左到右倾斜（瀑布）
        self.notes = []
        for _ in range(12):
            self.notes.append({
                "x": random.uniform(12, w - 12),
                "line": random.uniform(-2, self.LINES + 1),   # 上下分散（高低音）
                "kind": random.choice(("half", "quarter", "eighth")),
                "phase": random.uniform(0, math.tau),
                "speed": random.uniform(0.4, 1.0),
                "float": random.uniform(1.5, 3.5),
                "tw": random.uniform(0.5, 1.5),
            })

    def wave_y(self, x, t, i):
        """瀑布波浪：整体左高右低倾斜 + 柔和长波连续流动（无模运算跳变）+ 低频起伏"""
        return self.base + i * self.GAP + x * self.tilt \
            + math.sin(x * 0.024 + t * 0.30 + i * 0.5) * self.amp \
            + math.sin(t * 0.13 + i * 1.7) * 3

    def draw(self, s, t):
        for i in range(self.LINES):
            pts = [(x, self.wave_y(x, t, i)) for x in range(0, config.W, 2)]
            pygame.draw.lines(s, (72, 82, 122), False, pts, 1)
        for n in self.notes:
            n["x"] += random.uniform(-0.25, 0.25)      # 实时随机漂移（不固定动画）
            if n["x"] < 12:
                n["x"] = 12
            elif n["x"] > config.W - 12:
                n["x"] = config.W - 12
            y = int(self.wave_y(n["x"], t, n["line"])
                    + math.sin(t * n["speed"] * 2 + n["phase"]) * n["float"])
            bright = int(110 + 90 * math.sin(t * n["tw"] * 2 + n["phase"]
                                             + random.uniform(0, 0.4)))
            c = (bright, bright, min(255, bright + 40))
            self._note(s, n["kind"], int(n["x"]), y, c)

    def _note(self, s, kind, x, y, c):
        if kind == "half":
            pygame.draw.ellipse(s, c, (x - 3, y - 4, 7, 6), 1)
        else:
            pygame.draw.ellipse(s, c, (x - 3, y - 4, 7, 6), 0)
        pygame.draw.line(s, c, (x + 4, y - 3), (x + 4, y - 14), 1)
        if kind == "eighth":
            pygame.draw.line(s, c, (x + 4, y - 14), (x + 9, y - 10), 1)


# ---------------------------------------------------------------------------
# 主界面：动态宇宙乐章 · 五线谱 · 自由星球 · 右侧竖琴 · 标题下横排菜单
# ---------------------------------------------------------------------------
class TitleScene:
    MENU = ["新旅程", "继续聆听", "星尘之书", "洛水桥边", "告别"]
    STAR_COUNT = 260

    def __init__(self):
        self.t = 0.0
        self.sel = 0
        self.toast = ""
        self.toast_t = 0.0
        self.stars = [Star(config.W, config.H) for _ in range(self.STAR_COUNT)]
        # 记忆星球：4×2 网格均匀分布（8 颗，每颗固定槽位）
        self.planets = [Planet(config.W, config.H, i) for i in range(8)]
        # 黑洞：左上角，缓慢自旋的吸积盘
        self.hole = {"x": 36, "y": 30, "r": 18, "spin": 0.0}
        # 动态五线谱 + 漂浮音符
        self.staff = Staff(config.W)
        self.meteor = None          # 流星（背景点缀）

    def menu_rects(self):
        # "星尘回响"标题正下方竖排居中
        n = len(self.MENU)
        gap = 12
        total = n * 17 + (n - 1) * gap
        y0 = 98
        return [pygame.Rect((config.W - 96) // 2, y0 + i * (17 + gap), 96, 17)
                for i in range(n)]

    def event(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(self.MENU); audio.play("ui_move")
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(self.MENU); audio.play("ui_move")
            elif e.key == pygame.K_RETURN:
                audio.play("ui_ok"); self.pick(self.sel)
            elif e.key in N.KEY_MAP:                      # 主界面也回应音符（听觉反馈）
                audio.play("note_" + N.KEY_MAP[e.key])
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            mx, my = pygame.mouse.get_pos()
            for i, r in enumerate(self.menu_rects()):
                if r.collidepoint(mx // config.SCALE, my // config.SCALE):
                    self.sel = i
                    audio.play("ui_ok")
                    self.pick(i)

    def pick(self, i):
        name = self.MENU[i]
        if name == "新旅程":
            from core import save as S
            S.new_game()
            from core.story.map_scene import MapScene
            self.game.set_scene(MapScene())
        elif name == "继续聆听":
            from core import save as S
            d = S.load()
            if d and d.get("planet"):
                from core.story.map_scene import MapScene
                from core.story.scene import StoryScene
                if d.get("pois") is not None:
                    self.game.set_scene(MapScene(d["memory"], d["fragments"], d["pois"]))
                else:                                   # 旧档兼容：线性剧情
                    self.game.set_scene(StoryScene(d["planet"], d["scene"],
                                                   memory=d["memory"], fragments=d["fragments"]))
            else:
                self.toast = "尚未有存档 · 请先开始新旅程"
                self.toast_t = 2.0
        elif name == "告别":
            self.game.running = False
        else:
            self.toast = f"{name} · 尚未解锁"
            self.toast_t = 2.0

    def update(self, dt):
        self.t += dt
        for s in self.stars:
            s.update(dt, config.W, config.H)
        for p in self.planets:
            p.update(dt, self.planets)
        self.hole["spin"] += dt * 0.9
        # 流星：平均 8 秒一颗
        if self.meteor is None and random.random() < dt / 8:
            self.meteor = {"x": random.uniform(0, config.W * 0.75),
                           "y": random.uniform(0, config.H * 0.3),
                           "vx": random.uniform(90, 150), "vy": random.uniform(35, 65),
                           "t": 0.0}
        elif self.meteor is not None:
            m = self.meteor
            m["x"] += m["vx"] * dt
            m["y"] += m["vy"] * dt
            m["t"] += dt
            if m["x"] > config.W + 20 or m["y"] > config.H + 20 or m["t"] > 3:
                self.meteor = None
        if self.toast_t > 0:
            self.toast_t -= dt
        audio.play_loop("bgm", 0.30)     # 主界面氛围乐
        audio.stop_loop("rain")

    def draw(self, s):
        mouse = pygame.mouse.get_pos()
        mouse = (mouse[0] // config.SCALE, mouse[1] // config.SCALE)
        cx, cy = config.W // 2, config.H // 2 - 6
        # 星尘
        for st in self.stars:
            st.draw(s)
        # 流星（亮头 + 尾迹）
        if self.meteor:
            m = self.meteor
            pygame.draw.line(s, (255, 250, 225),
                             (int(m["x"] - m["vx"] * 0.07), int(m["y"] - m["vy"] * 0.07)),
                             (int(m["x"]), int(m["y"])), 1)
            pygame.draw.circle(s, (255, 255, 255), (int(m["x"]), int(m["y"])), 2)
        # 黑洞（左上）：吸积盘 + 事件视界
        hx, hy, hr = self.hole["x"], self.hole["y"], self.hole["r"]
        for rr, a in ((hr + 10, 12), (hr + 5, 22), (hr + 2, 36)):
            circ = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
            pygame.draw.circle(circ, (70, 44, 110, a), (rr, rr), rr, 1)
            s.blit(circ, (hx - rr, hy - rr))
        for i in range(5):
            a2 = self.hole["spin"] * (i * 0.8 + 1) + i * math.tau / 5
            px = hx + math.cos(a2) * hr * 1.55
            py = hy + math.sin(a2) * hr * 0.5
            pygame.draw.circle(s, (150, 112, 205), (int(px), int(py)), 2)
        pygame.draw.circle(s, (0, 0, 0), (hx, hy), hr)
        pygame.draw.circle(s, (22, 15, 36), (hx, hy), hr, 1)
        # 五线谱 + 漂浮音符
        self.staff.draw(s, self.t)
        # 自由漫游星球（生灭循环 + 涟漪 + 悬停发光）
        for p in self.planets:
            p.draw(s, mouse)
        # 标题（36px 像素字）
        f = ui.load_font(36, bold=False)
        img = f.render("星尘回响", True, config.GOLD)
        shd = f.render("星尘回响", True, (8, 7, 22))
        tw = img.get_width()
        tx = (config.W - tw) // 2
        s.blit(shd, (tx + 2, cy - 88 + 2))
        s.blit(img, (tx, cy - 88))
        # 副标题（8px 像素字）
        f8 = ui.load_font(16)
        sub = f8.render("ECHOES OF STARDUST", True, (150, 158, 190))
        s.blit(sub, ((config.W - sub.get_width()) // 2, cy - 46))
        # 手写小字
        if self.t >= 1.2:
            a = min(1.0, (self.t - 1.2) / 0.6)
            col = tuple(int(config.STAR[i] * a) for i in range(3))
            ui.text(s, "你还记得……第一颗消失的星球叫什么名字吗？", (10, 8), size=12, color=col)
        # 菜单（标题下方横排，悬停高亮，无闪烁粒子）
        if self.t >= 1.5:
            ma = min(1.0, (self.t - 1.5) / 0.5)
            for i, r in enumerate(self.menu_rects()):
                ui.menu_item(s, r, self.MENU[i], selected=(i == self.sel))
        if self.toast_t > 0:
            ui.text(s, self.toast, (config.W // 2, config.H - 22), size=12, center=True)


# ---------------------------------------------------------------------------
# 织曲战斗：J/K/L/I 弹奏 · U 聆听慢动作 · 共鸣节奏 · 三灵韵即兴终结技
# ---------------------------------------------------------------------------
class BattleScene:
    def __init__(self, enemy_key="shadow_beast"):
        self.e = R.ENEMIES[enemy_key]
        self.judge = R.Judge(self.e["notes"], self.e["gap_ms"])
        self.hp = self.maxhp = self.e["hp"]
        self.ph = 5
        self.ling = 0
        self.bolts = []
        self.ebolts = []
        self.pos = pygame.Vector2(70, 190)
        self.epos = pygame.Vector2(380, 120)
        self.flash = 0.0
        self.t = 0.0
        self.cd = 0.0
        self.composer = None
        self.composer_t = 0.0
        self.over = None
        self.over_t = 0.0
        self.toast = ""
        self.toast_t = 0.0
        self.listening = False
        self.fx = []
        self.on_win = None          # 战斗胜利回调（剧情衔接）
        self.last_dir = pygame.Vector2(1, 0)        # 像素风方向发射
        self.bstars = [Star(config.W, config.H) for _ in range(40)]

    def event(self, e):
        if self.over or e.type != pygame.KEYDOWN:
            return
        if self.composer:
            self._composer_event(e)
            return
        note = N.KEY_MAP.get(e.key)
        if note:
            self.fire(note)
        elif e.key == pygame.K_SPACE and self.ling >= 3:
            audio.play("ui_select")
            self.composer = F.Composer()
            self.composer_t = F.COMPOSE_TIME_S

    def _composer_event(self, e):
        if e.key == pygame.K_LEFT:
            self.composer.move(-1)
        elif e.key == pygame.K_RIGHT:
            self.composer.move(1)
        elif e.key == pygame.K_UP:
            self.composer.cycle(1)
        elif e.key == pygame.K_DOWN:
            self.composer.cycle(-1)
        elif e.key == pygame.K_RETURN:
            self.composer.fill(); audio.play("ui_move")
        elif e.key == pygame.K_BACKSPACE:
            self.composer.clear()
        elif e.key == pygame.K_ESCAPE:
            self.composer = None; audio.play("ui_select")

    def fire(self, note):
        # 方向发射：朝最近移动方向（上下左右移动即决定朝向）
        d = self.last_dir
        if d.length() == 0:
            d = self.epos - self.pos
        d = d.normalize() * 240
        self.bolts.append([self.pos.x + 20, self.pos.y, d.x, d.y, note])
        audio.play("note_" + note)
        res = self.judge.press(note, self.game.now())
        if res == "hit":
            self.ling = min(3, self.ling + 1)
            self.flash = 0.12
            audio.play("resonance")
            self._toast("共鸣 · 灵韵 +1")
        elif res == "miss":
            self._toast("节奏偏了 · 未共鸣")

    def _toast(self, t):
        self.toast = t
        self.toast_t = 1.4

    def update(self, dt):
        self.t += dt
        for st in self.bstars:
            st.update(dt, config.W, config.H)
        if self.over:
            self.over_t += dt
            if self.over_t > 2.5:
                if self.over == "win" and self.on_win:
                    self.on_win()
                else:
                    self.game.set_scene(TitleScene())
            return
        if self.composer:
            self.composer_t -= dt
            if self.composer_t <= 0:
                self.resolve_finale()
            return
        ts = 0.3 if self.listening else 1.0
        k = pygame.key.get_pressed()
        sp = 130 * ts
        if k[pygame.K_a]:
            self.pos.x -= sp * dt
            self.last_dir = pygame.Vector2(-1, 0)
        if k[pygame.K_d]:
            self.pos.x += sp * dt
            self.last_dir = pygame.Vector2(1, 0)
        if k[pygame.K_w]:
            self.pos.y -= sp * dt
            self.last_dir = pygame.Vector2(0, -1)
        if k[pygame.K_s]:
            self.pos.y += sp * dt
            self.last_dir = pygame.Vector2(0, 1)
        self.pos.x = max(10, min(config.W - 10, self.pos.x))
        self.pos.y = max(10, min(config.H - 30, self.pos.y))
        for b in self.bolts[:]:
            b[0] += b[2] * dt * ts
            b[1] += b[3] * dt * ts
            if not (0 <= b[0] <= config.W and 0 <= b[1] <= config.H):
                self.bolts.remove(b)
            elif math.hypot(b[0] - self.epos.x, b[1] - self.epos.y) < 22:
                self.bolts.remove(b)
                self.hp -= 10
                self.fx.append([b[0], b[1], 0.45])
        self.cd -= dt
        if self.cd <= 0:
            self.cd = random.uniform(1.2, 2.0)
            d = (self.pos - self.epos)
            if d.length() > 0:
                d = d.normalize() * 90
                self.ebolts.append([self.epos.x, self.epos.y, d.x, d.y])
        for b in self.ebolts[:]:
            b[0] += b[2] * dt * ts
            b[1] += b[3] * dt * ts
            if not (0 <= b[0] <= config.W and 0 <= b[1] <= config.H):
                self.ebolts.remove(b)
            elif math.hypot(b[0] - self.pos.x, b[1] - self.pos.y) < 12:
                self.ebolts.remove(b)
                self.ph -= 1
                audio.play("hurt")
                if self.ph <= 0:
                    self.over = "lose"; self.over_t = 0
        if self.hp <= 0:
            self.over = "win"; self.over_t = 0
            audio.play("ui_ok")
        self.listening = pygame.key.get_pressed()[pygame.K_u]
        audio.play_loop("bgm", 0.22)     # 战斗氛围乐
        for f2 in self.fx[:]:
            f2[2] -= dt
            if f2[2] <= 0:
                self.fx.remove(f2)
        self.flash = max(0.0, self.flash - dt)
        if self.toast_t > 0:
            self.toast_t -= dt

    def resolve_finale(self):
        res = self.composer.resolve()
        self.composer = None
        audio.play("resonance")
        self.flash = 0.25
        dmg = int(24 * res["dmg_mult"])
        self.hp -= dmg
        txt = f"终曲奏响 · 伤害 {dmg}"
        if res["effects"]:
            txt += " · " + res["effects"][0]
        self._toast(txt)

    def draw(self, s):
        # 星空背景 + 瓦片感地面（不再纯黑）
        for st in self.bstars:
            st.draw(s)
        pygame.draw.rect(s, (14, 17, 38), (0, config.H - 28, config.W, 28))
        for gx in range(0, config.W, 20):
            pygame.draw.line(s, (26, 32, 62), (gx, config.H - 28), (gx, config.H), 1)
        for gy in range(0, 28, 7):
            pygame.draw.line(s, (26, 32, 62), (0, config.H - 28 + gy), (config.W, config.H - 28 + gy), 1)
        ex, ey = int(self.epos.x), int(self.epos.y)
        # 暗影兽 · 寂静爪牙：黑影团 + 红眼 + 紫黑触手 + 边缘光
        for i in range(6):
            a = i * math.tau / 6 + self.t * 0.8
            x2 = ex + math.cos(a) * 30
            y2 = ey + math.sin(a) * 30
            pygame.draw.line(s, (42, 14, 52), (ex, ey), (int(x2), int(y2)), 2)
        for rr, c in ((26, (24, 8, 36)), (19, (36, 12, 46)), (12, (56, 20, 66))):
            pygame.draw.circle(s, c, (ex, ey), rr)
        pygame.draw.circle(s, (255, 70, 60), (ex - 8, ey - 4), 3)
        pygame.draw.circle(s, (255, 70, 60), (ex + 8, ey - 4), 3)
        pygame.draw.circle(s, (255, 150, 130), (ex - 8, ey - 4), 1)
        pygame.draw.circle(s, (255, 150, 130), (ex + 8, ey - 4), 1)
        ui.text(s, "寂静爪牙 · 暗影兽", (ex, ey - 48), size=12,
                color=(190, 130, 160), center=True)
        pygame.draw.rect(s, (70, 30, 40), (ex - 40, ey - 44, 80, 4))
        pygame.draw.rect(s, (200, 90, 80), (ex - 40, ey - 44, int(80 * self.hp / self.maxhp), 4))
        rn = "".join(N.NOTE_SYM[n] for n in self.e["notes"])
        done = "".join(N.NOTE_SYM[n] for n in self.e["notes"][:self.judge.progress])
        ui.text(s, rn, (ex, ey - 58), size=12, color=config.RHYTHM_GOLD, center=True)
        ui.text(s, done, (ex, ey - 58), size=12, color=config.GOLD_HI, center=True)
        harp_img = IMG.get("harp_real") or IMG.get("harp")
        if harp_img:
            hw = 40
            hh = int(harp_img.get_height() * hw / harp_img.get_width())
            key = ("harp_battle", hw, hh)
            if key not in SCALE_CACHE:
                SCALE_CACHE[key] = pygame.transform.smoothscale(harp_img, (hw, hh))
            hf = SCALE_CACHE[key]
            s.blit(hf, (int(self.pos.x - hw / 2), int(self.pos.y - hh / 2 + 8)))
        for i in range(self.ph):
            pygame.draw.circle(s, config.STAR, (int(self.pos.x - 20 + i * 10), int(self.pos.y - 40)), 3)
        for b in self.bolts:
            c = config.NOTE_COLORS[b[4]]
            tr = PART.get("trace") or PART.get("magic") or []
            if tr:
                t2 = part(tr, int(self.t * 16 + b[0]), 0.5)
                t2.set_alpha(140)
                s.blit(t2, (int(b[0] - t2.get_width() / 2), int(b[1] - t2.get_height() / 2)))
            pygame.draw.circle(s, c, (int(b[0]), int(b[1])), 3)
        for b in self.ebolts:
            sm = PART.get("smoke") or []
            if sm:
                sm2 = part(sm, int(self.t * 10) + int(b[0] + b[1]), 0.8)
                sm2.set_alpha(200)
                s.blit(sm2, (int(b[0] - sm2.get_width() / 2), int(b[1] - sm2.get_height() / 2)))
            pygame.draw.circle(s, (120, 60, 110), (int(b[0]), int(b[1])), 4)
        for i in range(3):
            c = config.LING_COLORS[i] if i < self.ling else (60, 60, 90)
            pygame.draw.rect(s, c, (8 + i * 16, 8, 10, 12))
        for f2 in self.fx:
            sp = PART.get("spark") or []
            if sp:
                for k in range(4):
                    sp3 = part(sp, random.randrange(len(sp)), 1.0 - f2[2])
                    sp3.set_alpha(int(255 * f2[2] / 0.45))
                    s.blit(sp3, (int(f2[0] + random.uniform(-10, 10)),
                                 int(f2[1] + random.uniform(-10, 10))))
        if self.listening:
            f = pygame.Surface((config.W, config.H), pygame.SRCALPHA)
            f.fill((10, 20, 60, 90))
            s.blit(f, (0, 0))
            ui.text(s, "聆 听", (config.W // 2, 14), size=24, color=(170, 205, 245), center=True)
        if self.composer:
            self._draw_composer(s)
        if self.flash > 0:
            f = pygame.Surface((config.W, config.H), pygame.SRCALPHA)
            f.fill((255, 255, 255, int(200 * self.flash / 0.25)))
            s.blit(f, (0, 0))
        if self.toast_t > 0:
            ui.text(s, self.toast, (config.W // 2, config.H - 26), size=12, color=config.GOLD_HI, center=True)
        if self.over == "win":
            sm = PART.get("smoke") or []
            st2 = PART.get("star") or []
            for i2 in range(8):
                if sm:
                    sm3 = part(sm, int(self.over_t * 20) + i2, 0.8 + i2 * 0.15)
                    sm3.set_alpha(int(200 * (1 - self.over_t / 2.5)))
                    s.blit(sm3, (ex - sm3.get_width() / 2 + (i2 - 4) * 6,
                                 ey - sm3.get_height() / 2 + (i2 % 3) * 8))
                if st2:
                    st3 = part(st2, i2 + int(self.over_t * 12), 0.8)
                    st3.set_alpha(220)
                    s.blit(st3, (ex + (i2 - 4) * 14, ey + (i2 % 5) * 10 - 20))
            ui.text(s, "挽歌奏响 · 星球归于星尘", (config.W // 2, config.H // 2), size=24,
                    color=config.GOLD_HI, center=True)
        elif self.over == "lose":
            ui.text(s, "琴弦断裂……再来一次", (config.W // 2, config.H // 2), size=24,
                    color=(200, 90, 80), center=True)
        else:
            ui.text(s, "J风 K火 L水 I地 · U聆听 · 共鸣三连得灵韵 · 空格即兴", (config.W // 2, config.H - 8),
                    size=12, color=(120, 130, 170), center=True)

    def _draw_composer(self, s):
        c = self.composer
        f = pygame.Surface((config.W, config.H), pygame.SRCALPHA)
        f.fill((5, 8, 20, 210))
        s.blit(f, (0, 0))
        ui.text(s, "即兴终结技 · 五线谱", (config.W // 2, 24), size=24, color=config.GOLD, center=True)
        ui.text(s, f"剩余 {max(0, self.composer_t):.1f}s", (config.W // 2, 48), size=12,
                color=(170, 205, 245), center=True)
        bw, gap = 40, 8
        x0 = config.W // 2 - (bw * 8 + gap * 7) // 2
        for i in range(c.slots):
            r = pygame.Rect(x0 + i * (bw + gap), 70, bw, 52)
            selected = i == c.cursor
            ui.gold_panel(s, r, alpha=150, selected=selected)
            ui.text(s, c.symbol(i), r.center, size=24,
                    color=config.GOLD_HI if selected else config.GOLD, center=True)
        picks = N.NOTES + ["·"]
        py0 = 140
        for i, p in enumerate(picks):
            r = pygame.Rect(x0 + i * (bw + gap), py0, bw, 30)
            ui.gold_panel(s, r, alpha=120, selected=(i == c.pick))
            col = config.NOTE_COLORS[p] if p in config.NOTE_COLORS else config.GOLD
            ui.text(s, {"wind": "风", "fire": "火", "water": "水", "earth": "地"}.get(p, "·"),
                    r.center, size=24, color=col, center=True)
        ui.text(s, "←→移动 · ↑↓选音 · 回车填入 · 退格清空 · ESC取消",
                (config.W // 2, config.H - 22), size=12, color=(120, 130, 170), center=True)


def main():
    g = Game()
    g.set_scene(TitleScene())
    g.run()


if __name__ == "__main__":
    main()