# 织曲系统：音符 / 按键 / 序列法则（同调·对位·休止符）· 铭记旋律
import pygame

# 四元素 + 三大叙事音符（忆/光/暗，仅用于即兴填谱）
NOTES = ["wind", "fire", "water", "earth", "memory", "light", "dark"]

# J/K/L/I 四键对应 风/火/水/地
KEY_MAP = {pygame.K_j: "wind", pygame.K_k: "fire", pygame.K_l: "water", pygame.K_i: "earth"}

# 相反属性对（对位融合）
CONTRAST = {("wind", "earth"), ("earth", "wind"), ("fire", "water"), ("water", "fire")}

NOTE_SYM = {"wind": "风", "fire": "火", "water": "水", "earth": "地",
            "memory": "忆", "light": "光", "dark": "暗"}
REST_SYM = "·"  # 休止符


def is_same(a, b):
    return a == b and a is not None


def is_contrast(a, b):
    return (a, b) in CONTRAST


def parse_sequence(seq):
    """解析即兴序列（None=休止符）→ 效果描述与伤害倍率。
    法则：相同相邻=同调+50%；相反相邻=对位融合；休止符后下一音符伤害x2。"""
    dmg = 1.0
    prev_rest = False
    effects = []
    for i in range(len(seq)):
        n = seq[i]
        if n is None:
            prev_rest = True
            continue
        if prev_rest:
            dmg *= 2.0
            effects.append("休止·余韵：下一音 x2")
            prev_rest = False
        if i > 0 and seq[i - 1] is not None:
            p = seq[i - 1]
            if is_same(p, n):
                dmg *= 1.5
                effects.append(f"{NOTE_SYM[n]}{NOTE_SYM[n]} 同调 +50%")
            elif is_contrast(p, n):
                dmg *= 1.8
                fx = "蒸汽迷雾" if {p, n} == {"fire", "water"} else "沙尘暴"
                effects.append(f"{NOTE_SYM[p]}{NOTE_SYM[n]} 对位 → {fx}")
    return {"dmg_mult": dmg, "effects": effects}
