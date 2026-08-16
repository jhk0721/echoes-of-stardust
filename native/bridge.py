# C++ 判定核心桥接：优先加载 rhythm_core DLL，缺失时降级纯 Python（同构实现）
# 构建方式见 docs/开发文档.md「C++ 部分」
import ctypes
import os

from core import config

_mode = "python"
_lib = None


def _py_step(note, expected, dt_ms, gap_ms, win_ms):
    """与 rhythm_core.cpp::step 同构"""
    if dt_ms < gap_ms - win_ms:
        return 0
    if dt_ms <= gap_ms + win_ms:
        return 1 if note == expected else 2
    return 2


def load():
    """尝试加载 C++ DLL；返回实际使用的后端名 'cpp' / 'python'"""
    global _mode, _lib
    dll = os.path.join(config.NATIVE, "rhythm_core.dll")
    if os.path.exists(dll):
        try:
            lib = ctypes.CDLL(dll)
            lib.step.restype = ctypes.c_int
            lib.step.argtypes = [ctypes.c_int, ctypes.c_int,
                                 ctypes.c_float, ctypes.c_float, ctypes.c_float]
            lib.judge_sequence.restype = ctypes.c_int
            lib.judge_sequence.argtypes = [ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_int),
                                           ctypes.POINTER(ctypes.c_float),
                                           ctypes.c_int, ctypes.c_float, ctypes.c_float]
            _lib = lib
            _mode = "cpp"
            return "cpp"
        except Exception:
            pass
    _mode = "python"
    return "python"


def step(note, expected, dt_ms, gap_ms, win_ms):
    if _mode == "cpp":
        return _lib.step(note, expected, dt_ms, gap_ms, win_ms)
    return _py_step(note, expected, dt_ms, gap_ms, win_ms)


def judge_sequence(target, presses, times, gap_ms, win_ms):
    n = min(len(target), len(presses), len(times))
    if _mode == "cpp":
        t = (ctypes.c_int * n)(*target[:n])
        p = (ctypes.c_int * n)(*presses[:n])
        tm = (ctypes.c_float * n)(*times[:n])
        return _lib.judge_sequence(t, p, tm, n, gap_ms, win_ms)
    hits = 0
    idx = 0
    last = None
    for i in range(n):
        if last is None:
            last = times[i]
            hits += 1 if presses[i] == target[idx] else 0
            idx += 1
            continue
        dt = times[i] - last
        if dt < gap_ms - win_ms:
            continue
        last = times[i]
        if idx < n and presses[i] == target[idx] and dt <= gap_ms + win_ms:
            hits += 1
        idx += 1
    return hits


# 启动即探测后端（供日志/文档展示）
load()
