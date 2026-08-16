# 入口：python run.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 显卡偏好：优先 MX150 独显（失败静默）
try:
    from tools import gpu_pref
    gpu_pref.apply()
except Exception:
    pass

# 首次运行自动生成素材（音频/精灵图），此后跳过
from tools import generate_assets
generate_assets.ensure()

from core.main import main
main()
