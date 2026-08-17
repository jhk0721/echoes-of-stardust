# Undertale 风格素材适配器：角色精灵表 / 程序化生成兜底
# 素材目录：assets/undertale/Characters/
import os
import math
import random

import pygame

from core import config

UT = os.path.join(config.BASE, "assets", "undertale")
CHARS = os.path.join(UT, "Characters")

_sheet_cache = {}
_char_cache = {}
_anim_cache = {}

# Undertale 角色映射：剧情角色 -> Undertale 角色文件名
WHO_SPRITE = {
    "老渔夫": "sans",
    "小女孩": "frisk",
    "楚子航": "chara",
    "绘梨衣": "undyne",
    "夏弥": "papyrus",
    "卡西莫多": "alphys",
    "爱斯梅拉达": "mettaton",
    "老科学家": "gaster",
    "母亲": "toriel",
    "赵馨语": "temmie",
    "上杉绘梨衣": "asriel",
    "绘梨衣": "asriel",
    "昂热": "asgore",
    "路明非": "flowey",
    "刘子墨": "napstablook",
    "张子硕": "burgerpants",
    "敬嘉轩": "monster_kid",
    "邓布利多": "grillby",
    "斯内普": "mufet",
    "李白": "lesser_dog",
    "福贵": "greater_dog",
    "高教授": "doggo",
    "史铁生": "dogamy",
    "小辉": "dogaressa",
    "桑提亚哥": "nice_cream",
    "小王子": "snowdrake",
    "林辰": "ice_cap",
    "造物主": "photoshop_flowey",
}

# Undertale 标准精灵布局：每角色 12x16 或 24x32，4向 x 4帧走路 + 站立帧
# 文件命名：<name>.png 或 <name>_walk.png

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

def _load_sheet(name):
    """加载角色精灵表，支持多种命名格式"""
    # 尝试多种路径
    paths = [
        os.path.join(CHARS, name + ".png"),
        os.path.join(CHARS, name + "_walk.png"),
        os.path.join(CHARS, name + "_sprites.png"),
        os.path.join(UT, "Sprites", name + ".png"),
    ]
    for p in paths:
        img = _load(p)
        if img:
            return img, p
    return None, None

def _slice_undertale_sheet(img, frame_w=24, frame_h=32):
    """切割 Undertale 风格精灵表
    假设布局：4行(下左上右) x 4列(站立+3走路帧) 或 4行 x 4列
    返回: {direction: [帧列表], 'idle': 站立帧}
    directions: 0=down, 1=left, 2=right, 3=up
    """
    frames = {}
    w, h = img.get_size()
    cols = w // frame_w
    rows = h // frame_h
    
    if cols >= 4 and rows >= 4:
        # 标准 4向 x 4帧布局
        dir_names = ['down', 'left', 'right', 'up']
        for row in range(4):
            dir_frames = []
            for col in range(min(4, cols)):
                x = col * frame_w
                y = row * frame_h
                try:
                    frame = img.subsurface(x, y, frame_w, frame_h)
                    dir_frames.append(frame)
                except Exception:
                    break
            if dir_frames:
                frames[dir_names[row]] = dir_frames
    elif cols >= 3 and rows >= 4:
        # 4向 x 3帧布局
        dir_names = ['down', 'left', 'right', 'up']
        for row in range(4):
            dir_frames = []
            for col in range(min(3, cols)):
                x = col * frame_w
                y = row * frame_h
                try:
                    frame = img.subsurface(x, y, frame_w, frame_h)
                    dir_frames.append(frame)
                except Exception:
                    break
            if dir_frames:
                frames[dir_names[row]] = dir_frames
    return frames

def _gen_undertale_char(name, color, frame_w=24, frame_h=32):
    """程序化生成 Undertale 风格角色精灵（像素画风）"""
    frames = {}
    dir_names = ['down', 'left', 'right', 'up']
    
    for dir_name in dir_names:
        dir_frames = []
        for f in range(4):  # 站立 + 3走路帧
            surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
            
            # 身体基础色
            body_color = color
            outline = tuple(max(0, c - 60) for c in color)
            shade = tuple(max(0, c - 30) for c in color)
            highlight = tuple(min(255, c + 40) for c in color)
            
            if dir_name == 'down':
                # 正面：头、身体、腿
                # 头
                pygame.draw.ellipse(surf, body_color, (8, 2, 8, 10))
                pygame.draw.ellipse(surf, outline, (8, 2, 8, 10), 1)
                # 眼睛
                eye_y = 5 + (1 if f in (1, 2) else 0)  # 走路时眨眼
                pygame.draw.circle(surf, (0, 0, 0), (11, eye_y), 1)
                pygame.draw.circle(surf, (0, 0, 0), (16, eye_y), 1)
                # 身体
                pygame.draw.rect(surf, body_color, (6, 12, 12, 14))
                pygame.draw.rect(surf, outline, (6, 12, 12, 14), 1)
                # 腿走路动画
                leg_offset = 2 if f in (1, 3) else 0
                pygame.draw.rect(surf, shade, (8, 24 + leg_offset, 4, 6))
                pygame.draw.rect(surf, shade, (12, 24 - leg_offset, 4, 6))
                
            elif dir_name == 'up':
                # 背面：头顶、背部
                pygame.draw.ellipse(surf, body_color, (8, 2, 8, 10))
                pygame.draw.ellipse(surf, outline, (8, 2, 8, 10), 1)
                pygame.draw.rect(surf, body_color, (6, 12, 12, 14))
                pygame.draw.rect(surf, outline, (6, 12, 12, 14), 1)
                leg_offset = 2 if f in (1, 3) else 0
                pygame.draw.rect(surf, shade, (8, 24 + leg_offset, 4, 6))
                pygame.draw.rect(surf, shade, (12, 24 - leg_offset, 4, 6))
                
            elif dir_name == 'left':
                # 左侧面
                pygame.draw.ellipse(surf, body_color, (6, 2, 10, 10))
                pygame.draw.ellipse(surf, outline, (6, 2, 10, 10), 1)
                pygame.draw.circle(surf, (0, 0, 0), (14, 5), 1)  # 眼睛
                pygame.draw.rect(surf, body_color, (4, 12, 14, 14))
                pygame.draw.rect(surf, outline, (4, 12, 14, 14), 1)
                leg_offset = 2 if f in (1, 3) else 0
                pygame.draw.rect(surf, shade, (6, 24 + leg_offset, 4, 6))
                pygame.draw.rect(surf, shade, (10, 24 - leg_offset, 4, 6))
                # 手臂摆动
                arm_swing = 3 if f in (1, 3) else 0
                pygame.draw.rect(surf, body_color, (2, 14 + arm_swing, 4, 10))
                
            elif dir_name == 'right':
                # 右侧面（镜像左侧）
                pygame.draw.ellipse(surf, body_color, (8, 2, 10, 10))
                pygame.draw.ellipse(surf, outline, (8, 2, 10, 10), 1)
                pygame.draw.circle(surf, (0, 0, 0), (10, 5), 1)  # 眼睛
                pygame.draw.rect(surf, body_color, (6, 12, 14, 14))
                pygame.draw.rect(surf, outline, (6, 12, 14, 14), 1)
                leg_offset = 2 if f in (1, 3) else 0
                pygame.draw.rect(surf, shade, (10, 24 + leg_offset, 4, 6))
                pygame.draw.rect(surf, shade, (14, 24 - leg_offset, 4, 6))
                arm_swing = 3 if f in (1, 3) else 0
                pygame.draw.rect(surf, body_color, (18, 14 + arm_swing, 4, 10))
            
            dir_frames.append(surf)
        frames[dir_name] = dir_frames
    return frames

def get_char_frames(name, scale=2):
    """获取角色所有方向动画帧
    返回: {direction: [surface列表]}
    """
    key = (name, scale)
    if key in _char_cache:
        return _char_cache[key]
    
    ut_name = WHO_SPRITE.get(name, name.lower().replace(" ", "_"))
    img, path = _load_sheet(ut_name)
    
    if img:
        frames = _slice_undertale_sheet(img)
    else:
        # 程序化生成
        color_map = {
            "sans": (180, 180, 180),
            "frisk": (255, 240, 180),
            "chara": (200, 120, 120),
            "undyne": (80, 180, 255),
            "papyrus": (255, 180, 120),
            "alphys": (180, 220, 120),
            "mettaton": (255, 120, 200),
            "gaster": (100, 60, 140),
            "toriel": (255, 200, 160),
            "temmie": (255, 255, 180),
            "asriel": (160, 200, 255),
            "asgore": (200, 140, 100),
            "flowey": (120, 255, 120),
            "napstablook": (100, 120, 180),
            "burgerpants": (200, 160, 120),
            "monster_kid": (140, 200, 140),
            "grillby": (255, 160, 60),
            "mufet": (100, 80, 160),
            "lesser_dog": (200, 200, 200),
            "greater_dog": (180, 180, 180),
            "doggo": (160, 160, 160),
            "dogamy": (200, 140, 140),
            "dogaressa": (180, 140, 180),
            "nice_cream": (255, 180, 200),
            "snowdrake": (200, 255, 255),
            "ice_cap": (140, 200, 255),
            "photoshop_flowey": (255, 100, 100),
        }
        color = color_map.get(ut_name, (180, 180, 200))
        frames = _gen_undertale_char(ut_name, color)
    
    # 缩放
    if scale != 1:
        for dir_name in frames:
            frames[dir_name] = [
                pygame.transform.scale(f, (f.get_width() * scale, f.get_height() * scale))
                for f in frames[dir_name]
            ]
    
    _char_cache[key] = frames
    return frames

def get_player_frames(scale=2):
    """获取玩家角色（主角）动画帧"""
    return get_char_frames("protagonist", scale)

def get_idle_frame(name, direction='down', scale=2):
    """获取角色站立帧"""
    frames = get_char_frames(name, scale)
    if direction in frames and frames[direction]:
        return frames[direction][0]  # 第0帧为站立
    return None

def get_walk_frames(name, direction='down', scale=2):
    """获取角色走路动画帧（排除站立帧）"""
    frames = get_char_frames(name, scale)
    if direction in frames and len(frames[direction]) > 1:
        return frames[direction][1:]  # 第1-3帧为走路
    return []

# 预定义 NPC 动作类型
NPC_ACTIONS = {
    "老渔夫": "fishing",      # 钓鱼
    "小女孩": "collecting",   # 捡贝壳
    "绘梨衣": "writing",      # 写字/画画
    "老科学家": "reading",    # 看报纸
    "母亲": "cooking",        # 做饭
    "赵馨语": "drawing",      # 画画
    "昂热": "thinking",       # 思考
    "暗影兽": "shadow_idle",  # 触手摆动
}

def get_npc_action_frames(name, action_type=None):
    """获取 NPC 专属动作帧（循环动画）"""
    if action_type is None:
        action_type = NPC_ACTIONS.get(name, "idle")
    
    # 这里可以扩展具体的动作动画
    # 暂时返回站立帧，后续可扩展为专用动作
    base_frames = get_char_frames(name)
    return base_frames.get('down', [base_frames.get('down', [None])[0]])