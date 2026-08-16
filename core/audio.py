# 音频模块：程序化 wav + Kenney CC0 ogg 双源加载
# 程序化音效：tools/generate_assets.py 波形合成；Kenney UI 音效：assets/audio/kenney (CC0)
import os
import pygame
from core import config

_sounds = {}

# UI 音效别名：程序化名字 → Kenney 真实音效
_ALIAS = {"ui_move": "rollover1", "ui_ok": "click1", "ui_select": "click2"}


def load_all():
    """加载程序化 wav（Kenney ogg 按需懒加载，省内存）"""
    global _sounds
    _sounds = {}
    if not os.path.isdir(config.AUDIO):
        return
    for fn in sorted(os.listdir(config.AUDIO)):
        if fn.endswith(".wav"):
            name = fn[:-4]
            try:
                _sounds[name] = pygame.mixer.Sound(os.path.join(config.AUDIO, fn))
            except Exception:
                pass


_missed = set()
_loops = {}


def play_loop(name, vol=0.5):
    """循环播放（雨声/环境声）"""
    key = _ALIAS.get(name, name)
    _lazy(key)
    s = _sounds.get(key)
    if s and key not in _loops:
        ch = s.play(loops=-1)
        if ch:
            ch.set_volume(vol)
            _loops[key] = ch


def stop_loop(name):
    key = _ALIAS.get(name, name)
    ch = _loops.pop(key, None)
    if ch:
        ch.stop()


def stop_all_loops():
    for ch in _loops.values():
        try:
            ch.stop()
        except Exception:
            pass
    _loops.clear()


def _lazy(name):
    """按需加载音效（程序化 wav + Kenney ogg，首次播放时）"""
    if name in _sounds or name in _missed:
        return
    # 程序化 wav（四元素拨弦等）
    p = os.path.join(config.AUDIO, name + ".wav")
    if os.path.exists(p):
        try:
            _sounds[name] = pygame.mixer.Sound(p)
            return
        except Exception:
            pass
    # Kenney ogg
    for folder in (config.KENNEY_AUDIO, config.KENNEY2_AUDIO):
        for ext in (".ogg", ".wav"):
            p = os.path.join(folder, name + ext)
            if os.path.exists(p):
                try:
                    _sounds[name] = pygame.mixer.Sound(p)
                    return
                except Exception:
                    pass
    _missed.add(name)


def play(name, vol=1.0):
    key = _ALIAS.get(name, name)
    _lazy(key)
    s = _sounds.get(key) or _sounds.get(name)
    if s:
        s.set_volume(vol)
        s.play()


def has(name):
    return name in _sounds
