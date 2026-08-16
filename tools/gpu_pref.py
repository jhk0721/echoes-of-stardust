# 显卡偏好：强制游戏进程使用 NVIDIA MX150 独显（Windows 注册表 GpuPreference）
# 写入 HKCU\Software\Microsoft\DirectX\UserGpuPreferences
# GpuPreference=2 → 高性能独显；=1 省电核显；=0 系统默认
import os
import sys


def _app_name():
    # 优先当前 python.exe；若打包为 exe 则用 exe 名
    exe = os.path.basename(sys.executable).lower()
    return exe


def apply():
    """写入当前解释器的显卡偏好；失败静默（非致命）"""
    try:
        import winreg
        key_path = r"Software\Microsoft\DirectX\UserGpuPreferences"
        exe = sys.executable
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as k:
            cur = ""
            try:
                cur = winreg.QueryValueEx(k, exe)[0]
            except FileNotFoundError:
                pass
            if "GpuPreference=2" not in cur:
                winreg.SetValueEx(k, exe, 0, winreg.REG_SZ, "GpuPreference=2;")
                print(f"[gpu] 已设置 {os.path.basename(exe)} → MX150 独显 (GpuPreference=2)")
            else:
                print(f"[gpu] 已是独显偏好: {os.path.basename(exe)}")
    except Exception as ex:
        print(f"[gpu] 显卡偏好设置跳过: {type(ex).__name__}")


if __name__ == "__main__":
    apply()
