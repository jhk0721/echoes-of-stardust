# 即兴终结技：三灵韵 → 时停填谱（最多8槽）→ 序列解析 → 铭记旋律检测
from core.combat.notes import parse_sequence, NOTES, NOTE_SYM

MAX_SLOTS = 8
COMPOSE_TIME_S = 5.0   # 五秒作曲时间

# 铭记旋律（设定集第四章：见证故事后刻入音符盘的传说级序列）
MEMORIES = [
    {"name": "雨夜尼伯龙根", "seq": ["water", None, "water", None, "water"],
     "desc": "尼伯龙根：隐匿15秒 · 移动翻倍", "mult": 2.5},
    {"name": "卡西莫多的钟声", "seq": ["earth", "earth", None, "earth"],
     "desc": "铜钟庇护 · 免死护盾", "mult": 2.0},
    {"name": "不要温和地走入那个良夜", "seq": ["fire", "fire", "fire", None, "fire", "fire"],
     "desc": "200% 伤害 · 穿透灼烧", "mult": 4.5},
    {"name": "致绘梨衣的信", "seq": ["memory", "light", None, "water", "wind", "light"],
     "desc": "飘落樱花——她收到了", "mult": 3.0},
    {"name": "黑暗森林的答案", "seq": ["dark", None, None, "light"],
     "desc": "隐匿5秒 · 下一击x10", "mult": 6.0},
    {"name": "昂热的复仇", "seq": ["fire", "fire", None, "fire", "fire"],
     "desc": "折刀形态 · 300% 伤害", "mult": 5.0},
    {"name": "未完成的诗", "seq": ["water", "wind", "memory", None, "light"],
     "desc": "诗行版本 · 敌人自行离去", "mult": 3.5},
    {"name": "独行者的灯火", "seq": ["fire", None, None, "fire", "fire"],
     "desc": "化身灯塔20秒", "mult": 3.0},
    {"name": "破镜之舞", "seq": ["memory", None, "light", "memory"],
     "desc": "镜中倒影 · 羁绊均伤", "mult": 2.5},
    {"name": "花丛中的名字", "seq": ["water", "light", "memory", None, "water"],
     "desc": "守护神显形", "mult": 3.0},
]


def match_memory(seq):
    """检测铭记旋律：序列开头命中旋律且其余槽位为休止符"""
    for m in MEMORIES:
        s = m["seq"]
        if len(s) > len(seq):
            continue
        if all(seq[i] == s[i] for i in range(len(s))) and \
                all(seq[i] is None for i in range(len(s), len(seq))):
            return m
    return None


class Composer:
    """填谱状态机：左右移动光标，上下切换音符，回车确认，退格清空"""

    def __init__(self, slots=MAX_SLOTS):
        self.slots = slots
        self.seq = [None] * slots   # None = 休止符
        self.cursor = 0
        self.pick = 0               # 音符盘当前选择

    def move(self, dx):
        self.cursor = max(0, min(self.slots - 1, self.cursor + dx))

    def cycle(self, dy):
        self.pick = (self.pick + dy) % (len(NOTES) + 1)

    def fill(self):
        """填入当前选择的音符（pick==len(NOTES) 表示休止符）"""
        self.seq[self.cursor] = None if self.pick == len(NOTES) else NOTES[self.pick]

    def clear(self):
        self.seq[self.cursor] = None

    def filled_count(self):
        return sum(1 for s in self.seq if s is not None)

    def resolve(self):
        m = match_memory(self.seq)
        if m:
            return {"dmg_mult": m["mult"], "effects": [f"铭记旋律 · {m['name']}", m["desc"]],
                    "memory": m["name"]}
        return parse_sequence(self.seq)

    def symbol(self, i):
        s = self.seq[i]
        return NOTE_SYM[s] if s else REST_SYM
