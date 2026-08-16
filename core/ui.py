# UI 模块：统一样式 —— 1px 金边 + 半透明深蓝底 + 四角星尘装饰
# 字体：优先缝合像素字体 ttf（OFL-1.1），缺失退回系统字体链
import os
import pygame
from core import config

_font_cache = {}
_text_cache = {}          # (text,size,color,bold) → surface，限 512 项防膨胀


def load_font(size, bold=False):
    """像素字体优先（12px→10px→8px，字号取整数倍最锐利），失败退回系统链"""
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    f = None
    for path, base in ((config.FONT_PIXEL_12, 12), (config.FONT_PIXEL, 10),
                       (config.FONT_PIXEL_8, 8)):
        if os.path.exists(path) and size % base == 0:
            try:
                f = pygame.font.Font(path, size)
                break
            except Exception:
                f = None
    if f is None:
        for name in config.FONT_CHAIN:
            try:
                f = pygame.font.SysFont(name, size, bold=bold)
                if f:
                    break
            except Exception:
                pass
    _font_cache[key] = f or pygame.font.Font(None, size)
    return _font_cache[key]


def text(surf, s, pos, size=14, color=config.STAR, center=False, bold=False):
    key = (s, size, color, bold)
    img = _text_cache.get(key)
    if img is None:
        img = load_font(size, bold=bold).render(s, False, color)   # 无抗锯齿：像素字体锐利
        if len(_text_cache) > 512:
            _text_cache.clear()
        _text_cache[key] = img
    r = img.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surf.blit(img, r)
    return r


def gold_panel(surf, rect, alpha=140, border=config.GOLD, selected=False):
    """半透明深蓝面板 + 1px 金边 + 四角星尘点"""
    x, y, w, h = rect
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((*config.PANEL, alpha))
    surf.blit(panel, (x, y))
    c = config.GOLD_HI if selected else border
    pygame.draw.rect(surf, c, rect, 1)
    for dx, dy in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)):
        surf.set_at((x + dx, y + dy), c)


def menu_item(surf, rect, label, selected=False):
    """菜单项按钮：选中时金边变亮 + 文字变亮（12px 像素字原生渲染最锐利）"""
    gold_panel(surf, rect, alpha=110 if selected else 70, selected=selected)
    text(surf, label, rect.center, size=12,
         color=config.GOLD_HI if selected else config.GOLD, center=True)
