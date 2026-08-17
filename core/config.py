# 全局配置：分辨率 / 调色板 / 路径 / 字体链
# 设计原则：低分辨率像素风(480x270)，整数倍放大，程序化绘制，零美术素材依赖
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, "assets")
AUDIO = os.path.join(ASSETS, "audio")
SPRITES = os.path.join(ASSETS, "sprites")
FONTS = os.path.join(ASSETS, "fonts")
UI_DIR = os.path.join(ASSETS, "ui")
PARTICLES = os.path.join(ASSETS, "particles")
KENNEY_AUDIO = os.path.join(ASSETS, "audio", "kenney")
KENNEY2_AUDIO = os.path.join(ASSETS, "audio", "kenney2")
DOCS = os.path.join(BASE, "docs")
NATIVE = os.path.join(BASE, "native")
STARDEW = os.path.join(ASSETS, "stardew", "素材", "星露谷物语素材", "Stardew valley")
UNDERTALE = os.path.join(ASSETS, "undertale")

# --- 分辨率 ---
W, H = 480, 270          # 逻辑分辨率（像素风）
SCALE = 3                # 整数倍放大
SW, SH = W * SCALE, H * SCALE  # 实际窗口
FPS = 60

# --- 转场配置 ---
TRANSITION_FADE_DURATION = 0.3
TRANSITION_SLIDE_DURATION = 0.4

# --- 调色板（记忆星球配色体系）---
INK     = (0, 0, 0)       # 纯黑宇宙底
DEEP    = (12, 18, 46)    # 深蓝
PANEL   = (16, 26, 64)    # UI 半透明深蓝底
GOLD    = (232, 200, 120) # 1px 金边
GOLD_HI = (255, 238, 176) # 选中高亮金
STAR    = (225, 232, 255) # 星光
AURA    = (170, 205, 245) # 记忆体光晕（淡蓝）

# 四元素音符色（风/火/水/地）
NOTE_COLORS = {
    "wind":  (140, 230, 220),  # 淡青
    "fire":  (242, 138, 82),   # 橙红
    "water": (88, 150, 236),   # 湛蓝
    "earth": (172, 120, 92),   # 赭石
}

# 灵韵槽三色
LING_COLORS = [(176, 205, 244), (236, 172, 96), (206, 150, 240)]  # 银蓝/暖橙/彩虹

# 节奏型金色
RHYTHM_GOLD = (255, 224, 140)

# --- 字体（OFL-1.1 缝合像素字体优先，失败退回系统链）---
FONT_PIXEL = os.path.join(FONTS, "fusion-pixel-10px-proportional-zh_hans.ttf")
FONT_PIXEL_12 = os.path.join(FONTS, "fusion-pixel-12px-monospaced-zh_hans.ttf")
FONT_PIXEL_8 = os.path.join(FONTS, "fusion-pixel-8px-monospaced-zh_hans.ttf")
FONT_CHAIN = ["microsoftyahei", "msyh", "simhei", "simsun", "dengxian", "freesansbold"]

# --- 音符按键映射 ---
NOTE_KEY_MAP = {
    "wind":  "j",
    "fire":  "k",
    "water": "l",
    "earth": "i",
}

# --- 玩家移动速度 ---
PLAYER_SPEED = 130

# --- 战斗参数 ---
BATTLE_PLAYER_HP = 5
BATTLE_ENEMY_BASE_HP = 100
RESONANCE_DMG_MULT = 2.0

# --- 存档路径 ---
SAVE_PATH = os.path.join(BASE, "save.json")

# --- 星球顺序（主线+自由探索）---
PLANET_ORDER = [
    "qianhai", "storm_city", "notre_dame", "flat", "finale_world",
    "qiancao", "kassel", "friends", "library", "ward",
    "math", "alive", "ditan", "paper_boat", "sea_old", "b612"
]
