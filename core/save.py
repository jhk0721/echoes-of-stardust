# 存档系统：新旅程建档 / 继续聆听读档
import json
import os

from core import config

SAVE_PATH = os.path.join(config.BASE, "save.json")

DEFAULT = {
    "planet": None,        # 当前星球 id
    "scene": None,         # 当前场景节点
    "fragments": [],       # 已收集记忆碎片
    "pois": [],            # 已完成的探索点
    "memory": {"主线": 0, "互动": 0, "残片": 0, "聆听": 0},
    "done": False,         # 是否完成挽歌
    "unlocked": [],        # 已解锁星球
}


def load():
    """读档；无档返回 None"""
    if not os.path.exists(SAVE_PATH):
        return None
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        d = dict(DEFAULT)
        d.update(data)
        return d
    except Exception:
        return None


def save(data):
    """写档"""
    d = dict(DEFAULT)
    d.update(data)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def new_game():
    """新旅程：重置存档"""
    save({"planet": None, "scene": None, "fragments": [], "memory": dict(DEFAULT["memory"]),
          "done": False, "unlocked": ["qianhai"]})
    return load()
