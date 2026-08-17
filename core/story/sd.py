# 星露谷素材适配器：地块拼地面 / 角色精灵 / 星球专属背景
# 素材仅限非商业学习用途（见 assets/stardew/StardewValley-Assets-main/README.md）
import math
import os
import random

import pygame

from core import config

SD = os.path.join(config.BASE, "assets", "stardew", "素材", "星露谷物语素材", "Stardew valley")
CHARS = os.path.join(SD, "Characters")

_sheet_cache = {}
_strip_cache = {}
_bg_cache = {}
_char_cache = {}

# ------------------------------------------------------------- 基础加载
def _load(path):
    if path in _sheet_cache:
        return _sheet_cache[path]
    img = None
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
        except Exception:
            img = None
    _sheet_cache[path] = img
    return img


def sheet(name):
    return _load(os.path.join(SD, name))


def _tiles(surf):
    """切 16px 瓦片，返回 [(tile, 平均色)]"""
    out = []
    for ty in range(0, surf.get_height() - 15, 16):
        for tx in range(0, surf.get_width() - 15, 16):
            t = surf.subsurface(tx, ty, 16, 16)
            r = g = b = n = 0
            for y in range(0, 16, 4):
                for x in range(0, 16, 4):
                    c = t.get_at((x, y))
                    if c[3] > 200:
                        r += c[0]; g += c[1]; b += c[2]; n += 1
            if n > 6:
                out.append((t, (r / n, g / n, b / n)))
    return out


def pick(sheet_name, target, n=4):
    """按颜色相似度从图集中挑 n 块瓦片（找不到则返回空列表）"""
    s = sheet(sheet_name)
    if not s:
        return []
    scored = sorted(_tiles(s), key=lambda tc: abs(tc[1][0] - target[0])
                    + abs(tc[1][1] - target[1]) + abs(tc[1][2] - target[2]))
    return [t for t, _ in scored[:n]]


# ------------------------------------------------------------- 角色精灵
# NPC → 星露谷角色（帧布局：64 宽 = 4 列方向，第 1 行站立帧，单帧 16x32）
WHO_SPRITE = {
    "老渔夫": "Willy", "小女孩": "Jas", "楚子航": "Sebastian", "夏弥": "Haley",
    "卡西莫多": "Dwarf", "爱斯梅拉达": "Emily", "老科学家": "Demetrius", "母亲": "Caroline",
    "赵馨语": "Leah", "上杉绘梨衣": "Penny", "绘梨衣": "Penny", "昂热": "Lewis", "路明非": "Sam",
    "刘子墨": "Vincent", "张子硕": "Alex", "敬嘉轩": "Sam",
    "邓布利多": "Wizard", "斯内普": "Krobus", "李白": "Linus", "福贵": "George",
    "高教授": "Gunther", "史铁生": "Marlon", "小辉": "Toddler", "桑提亚哥": "Willy",
    "小王子": "Toddler", "林辰": "Shane", "造物主": "MrQi",
}
MONSTER_SPRITE = {"暗影兽": "Monsters/Shadow Brute", "虚空歌者": "Monsters/Ghost"}


def char_idle(name, scale=2):
    """取角色站立帧（正面）并放大；name 可为剧情角色名或星露谷文件名"""
    key = (name, scale)
    if key in _char_cache:
        return _char_cache[key]
    fn = WHO_SPRITE.get(name) or MONSTER_SPRITE.get(name) or name
    # 星露谷角色表命名统一为 "<名字>..png"；怪物在 Monsters/ 子目录
    p = os.path.join(SD, "Characters", fn + "..png")
    if not os.path.exists(p):
        p = os.path.join(SD, "Characters", fn)
    img = _load(p)
    out = None
    if img:
        w, h = img.get_size()
        if w >= 16 and h >= 32:
            try:
                out = img.subsurface(0, 0, 16, 32)
                out = pygame.transform.scale(out, (16 * scale, 32 * scale))
            except Exception:
                out = None
    _char_cache[key] = out
    return out


def player_img(scale=2):
    return char_idle(os.path.join("Farmer", "farmer_base"), scale)


# ------------------------------------------------------------- 地面
# 星球 → (图集, 目标色)：按颜色挑地面瓦片
GROUND = {
    "qianhai": ("spring_beach..png", (90, 160, 225)),
    "storm_city": ("spring_town..png", (150, 145, 140)),
    "notre_dame": ("spring_town..png", (196, 168, 118)),
    "finale_world": ("winter_outdoorsTileSheet..png", (160, 185, 235)),
    "qiancao": ("spring_outdoorsTileSheet..png", (105, 170, 95)),
    "kassel": ("spring_outdoorsTileSheet..png", (112, 168, 96)),
    "friends": ("spring_outdoorsTileSheet..png", (108, 172, 92)),
    "library": ("townInterior..png", (122, 84, 52)),
    "ward": ("townInterior..png", (96, 96, 116)),
    "alive": ("spring_beach..png", (216, 186, 130)),
    "ditan": ("spring_outdoorsTileSheet..png", (92, 152, 82)),
    "paper_boat": ("spring_outdoorsTileSheet..png", (118, 176, 98)),
    "sea_old": ("spring_beach..png", (64, 148, 168)),
    "b612": ("spring_beach..png", (222, 192, 122)),
}


def ground(planet_key, w=config.W, rows=7, night=False):
    """星球地面条：挑色瓦片平铺（种子固定，帧间稳定）"""
    key = (planet_key, w, rows, night)
    if key in _strip_cache:
        return _strip_cache[key]
    h = rows * 16
    s = pygame.Surface((w, h))
    conf = GROUND.get(planet_key)
    ts = pick(conf[0], conf[1], n=5) if conf else []
    if ts:
        rng = random.Random(hash(planet_key) & 0xFFFF)
        for ty in range(0, h, 16):
            for tx in range(0, w, 16):
                s.blit(rng.choice(ts), (tx, ty))
    else:
        s.fill((30, 40, 70))
    if night:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((10, 16, 46, 120))
        s.blit(f, (0, 0))
    if planet_key == "flat":   # 降维：白底黑线
        s.fill((246, 246, 242))
        for x in range(0, w, 48):
            pygame.draw.line(s, (30, 30, 34), (x, 0), (x, h), 1)
        pygame.draw.line(s, (30, 30, 34), (0, 3), (w, 3), 2)
    if planet_key == "math":   # 数学：方格纸
        s.fill((238, 244, 250))
        for x in range(0, w, 16):
            pygame.draw.line(s, (170, 195, 225), (x, 0), (x, h), 1)
        for y in range(0, h, 16):
            pygame.draw.line(s, (170, 195, 225), (0, y), (w, y), 1)
    _strip_cache[key] = s
    return s


# ------------------------------------------------------------- 专属背景
def _stars(s, n=70, seed=1):
    rng = random.Random(seed)
    for _ in range(n):
        c = rng.randint(120, 235)
        pygame.draw.circle(s, (c, c, min(255, c + 20)),
                           (rng.randrange(s.get_width()), rng.randrange(int(s.get_height() * 0.6))), 1)


def _grad(s, c0, c1):
    h = int(s.get_height() * 0.62)
    for y in range(h):
        k = y / max(1, h - 1)
        s.fill(tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3)), (0, y, s.get_width(), 1))


def scene_bg(planet_key, tone=(10, 16, 48), night=False, boat=False):
    """整屏星球背景：天空渐变 + 星尘 + 专属点缀 + 地面瓦片"""
    key = (planet_key, night, boat)
    if key in _bg_cache:
        return _bg_cache[key]
    w, h = config.W, config.H
    s = pygame.Surface((w, h))
    dark = 0.45 if night else 1.0
    _grad(s, tuple(int(c * dark * 0.55) for c in tone), tuple(int(c * dark) for c in tone))
    _stars(s, seed=hash(planet_key) & 0xFF)
    gy = h - 7 * 16
    _accents(s, planet_key, gy, night)
    s.blit(ground(planet_key, w, 7, night), (0, gy))
    if boat:   # 海上小船剪影
        pygame.draw.polygon(s, (70, 50, 34), [(w - 120, gy + 26), (w - 60, gy + 26),
                                              (w - 70, gy + 38), (w - 112, gy + 38)])
        pygame.draw.line(s, (60, 44, 30), (w - 90, gy + 26), (w - 90, gy - 6), 2)
    if night:
        f = pygame.Surface((w, h), pygame.SRCALPHA)
        f.fill((6, 10, 30, 70))
        s.blit(f, (0, 0))
    img = s.convert() if pygame.display.get_surface() else s
    _bg_cache[key] = img
    return img


def _accents(s, pk, gy, night):
    """每颗星球的专属点缀（程序化剪影，贴合金边深蓝美学）"""
    w = config.W
    g = config.GOLD
    if pk == "qianhai":    # 灯塔
        lx = w - 52
        pygame.draw.rect(s, (36, 42, 74), (lx - 4, gy - 44, 8, 46))
        pygame.draw.rect(s, (36, 42, 74), (lx - 6, gy - 52, 12, 10))
        pygame.draw.circle(s, (255, 240, 180), (lx, gy - 47), 3)
    elif pk == "storm_city":   # 霓虹街灯
        for x in (60, 150, 260, 380):
            pygame.draw.rect(s, (30, 36, 66), (x, gy - 52, 3, 52))
            pygame.draw.circle(s, (120, 200, 255), (x + 1, gy - 54), 3)
        for i, c in enumerate(((255, 90, 140), (90, 220, 255), (255, 190, 90))):
            pygame.draw.rect(s, c, (90 + i * 120, gy - 40 - i * 6, 26, 10))
    elif pk == "notre_dame":   # 圣母院双塔剪影
        cx = w // 2
        for dx in (-34, 10):
            pygame.draw.rect(s, (54, 42, 30), (cx + dx, gy - 74, 24, 74))
            pygame.draw.polygon(s, (54, 42, 30), [(cx + dx, gy - 74), (cx + dx + 12, gy - 90),
                                                  (cx + dx + 24, gy - 74)])
        pygame.draw.rect(s, (54, 42, 30), (cx - 10, gy - 56, 20, 56))
        pygame.draw.circle(s, (255, 210, 120), (cx, gy - 36), 7, 1)
    elif pk == "flat":    # 黑白废墟线稿 + 向日葵
        for x, hh in ((70, 40), (150, 64), (330, 52), (410, 30)):
            pygame.draw.rect(s, (246, 246, 242), (x, gy - hh, 36, hh))
            pygame.draw.rect(s, (30, 30, 34), (x, gy - hh, 36, hh), 2)
        cx = w // 2
        pygame.draw.line(s, (60, 120, 50), (cx, gy), (cx, gy - 30), 2)
        pygame.draw.circle(s, (255, 200, 60), (cx, gy - 36), 8)
        pygame.draw.circle(s, (120, 80, 40), (cx, gy - 36), 4)
    elif pk == "finale_world":  # 巨琴
        cx = w // 2
        pygame.draw.arc(s, g, (cx - 26, gy - 84, 52, 80), math.radians(30), math.radians(150), 3)
        for i in range(6):
            x = cx - 18 + i * 7
            pygame.draw.line(s, g, (x, gy - 76), (x - 3, gy - 6), 1)
    elif pk == "qiancao":   # 樱花寺
        pygame.draw.rect(s, (80, 40, 44), (w // 2 - 40, gy - 46, 80, 46))
        pygame.draw.polygon(s, (96, 48, 52), [(w // 2 - 54, gy - 46), (w // 2, gy - 72),
                                              (w // 2 + 54, gy - 46)])
        rng = random.Random(7)
        for _ in range(60):
            pygame.draw.circle(s, (255, rng.randint(160, 200), 210),
                               (rng.randrange(w), rng.randrange(gy - 30)), 1)
    elif pk == "kassel":    # 钟楼 + 长影
        pygame.draw.rect(s, (58, 48, 38), (w - 90, gy - 66, 26, 66))
        pygame.draw.polygon(s, (58, 48, 38), [(w - 90, gy - 66), (w - 77, gy - 84), (w - 64, gy - 66)])
        pygame.draw.circle(s, (255, 230, 160), (w - 77, gy - 56), 4)
        for i in range(4):
            pygame.draw.polygon(s, (20, 24, 40, 90),
                                [(60 + i * 90, gy), (84 + i * 90, gy), (150 + i * 90, gy + 30)])
    elif pk == "friends":   # 路灯 + 长椅
        pygame.draw.rect(s, (40, 46, 70), (w // 2 + 40, gy - 46, 3, 46))
        pygame.draw.circle(s, (255, 230, 150), (w // 2 + 41, gy - 48), 4)
        pygame.draw.rect(s, (70, 52, 38), (w // 2 - 50, gy - 18, 44, 6))
        pygame.draw.rect(s, (70, 52, 38), (w // 2 - 48, gy - 12, 4, 12))
        pygame.draw.rect(s, (70, 52, 38), (w // 2 - 12, gy - 12, 4, 12))
    elif pk == "library":   # 书架
        for x in (40, 140, 300, 400):
            pygame.draw.rect(s, (66, 46, 30), (x, gy - 60, 46, 60))
            rng = random.Random(x)
            for yy in range(gy - 54, gy - 4, 14):
                for xx in range(x + 3, x + 42, 6):
                    pygame.draw.rect(s, (rng.randint(120, 230), rng.randint(100, 200),
                                         rng.randint(90, 170)), (xx, yy, 4, 10))
    elif pk == "ward":      # 病房窗 + 月光
        pygame.draw.rect(s, (60, 66, 92), (w - 130, gy - 64, 34, 44))
        pygame.draw.line(s, (30, 34, 56), (w - 113, gy - 64), (w - 113, gy - 20), 2)
        pygame.draw.line(s, (30, 34, 56), (w - 130, gy - 42), (w - 96, gy - 42), 2)
        pygame.draw.circle(s, (220, 230, 255), (w - 122, gy - 52), 5)
    elif pk == "math":      # 黑板
        pygame.draw.rect(s, (36, 60, 48), (w // 2 - 70, gy - 70, 140, 62))
        pygame.draw.rect(s, (90, 70, 50), (w // 2 - 70, gy - 70, 140, 62), 2)
        pygame.draw.line(s, (230, 235, 240), (w // 2 - 56, gy - 50), (w // 2 + 30, gy - 50), 1)
        pygame.draw.line(s, (230, 235, 240), (w // 2 - 56, gy - 36), (w // 2 + 56, gy - 36), 1)
    elif pk == "alive":     # 犁沟 + 老牛
        for i in range(6):
            y = gy + 8 + i * 16
            pygame.draw.line(s, (120, 96, 54), (0, y), (w, y + 6), 3)
        pygame.draw.ellipse(s, (96, 82, 62), (80, gy - 22, 40, 20))
        pygame.draw.circle(s, (96, 82, 62), (122, gy - 18), 7)
    elif pk == "ditan":     # 红墙 + 古柏
        pygame.draw.rect(s, (120, 52, 44), (0, gy - 26, 130, 26))
        pygame.draw.rect(s, (150, 70, 56), (0, gy - 30, 130, 6))
        for tx in (300, 390):
            pygame.draw.rect(s, (70, 52, 36), (tx, gy - 40, 6, 40))
            pygame.draw.circle(s, (46, 92, 54), (tx + 3, gy - 52), 18)
    elif pk == "paper_boat":   # 纸船 + 芦苇
        for x in (100, 240, 360):
            pygame.draw.polygon(s, (250, 246, 235), [(x, gy + 30), (x + 18, gy + 30),
                                                     (x + 9, gy + 20)])
            pygame.draw.polygon(s, (250, 246, 235), [(x + 9, gy + 20), (x + 9, gy + 8),
                                                     (x + 16, gy + 18)])
        for x in (30, 50, 440):
            pygame.draw.line(s, (110, 130, 70), (x, gy), (x + 3, gy - 22), 2)
    elif pk == "sea_old":   # 海上半日
        pygame.draw.circle(s, (255, 226, 150), (w // 2, gy + 2), 16)
        pygame.draw.circle(s, (255, 240, 190), (w // 2, gy + 2), 10)
    elif pk == "b612":      # 火山 + 玫瑰罩
        for i, x in enumerate((120, 200, 330)):
            pygame.draw.polygon(s, (110, 74, 48), [(x, gy), (x + 30, gy), (x + 15, gy - 24)])
            if i < 2:
                pygame.draw.circle(s, (255, 140, 70), (x + 15, gy - 24), 3)
        pygame.draw.arc(s, (190, 220, 255), (w // 2 - 12, gy - 26, 24, 26), 0, math.pi, 1)
        pygame.draw.circle(s, (255, 110, 130), (w // 2, gy - 10), 4)
