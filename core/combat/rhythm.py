# 共鸣判定：节奏型复现
# 逐拍状态机，判定核心走 native 桥（C++ DLL 缺失时自动降级纯 Python）
from core.combat import notes as N
from native import bridge

# 敌人数仓（v0 内置两种，后续可扩展为数据驱动）
ENEMIES = {
    "shadow_beast": {"name": "暗影兽", "notes": ["wind", "fire", "wind"], "gap_ms": 460, "hp": 60},
    "void_singer": {"name": "虚空歌者", "notes": ["water", "earth", "water", "fire"], "gap_ms": 400, "hp": 90},
}


class Judge:
    """逐拍共鸣判定器。press() 返回 'perfect'/'hit'/'miss'/'early'/'done'"""

    def __init__(self, target, gap_ms, win_ms=150):
        self.target = list(target)
        self.gap = gap_ms
        self.win = win_ms
        self.idx = 0
        self.last_t = None

    def press(self, note, t_ms):
        if self.idx >= len(self.target):
            return "done"
        exp = N.NOTES.index(self.target[self.idx])
        got = N.NOTES.index(note)
        if self.last_t is None:
            self.last_t = t_ms
            self.idx += 1
            return "hit" if got == exp else "miss"
        dt = t_ms - self.last_t
        st = bridge.step(got, exp, dt, self.gap, self.win)
        if st == 0:          # 太早：忽略
            return "early"
        self.last_t = t_ms
        self.idx += 1
        return "hit" if st == 1 else "miss"

    @property
    def done(self):
        return self.idx >= len(self.target)

    @property
    def progress(self):
        return self.idx
