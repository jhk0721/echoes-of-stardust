# 解压用户下载的素材压缩包（不删除原文件，避免占用报错）
import glob
import os
import zipfile

for z in glob.glob("assets/*.zip"):
    if z.lower().endswith("fp.zip"):
        continue
    try:
        zf = zipfile.ZipFile(z)
        names = zf.namelist()
        base = "assets/stardew" if "stardew" in z.lower() else "assets/_new"
        os.makedirs(base, exist_ok=True)
        zf.extractall(base)
        print(os.path.basename(z), "->", base, len(names), "项")
    except Exception as ex:
        print(os.path.basename(z), "FAIL", ex)
print()
print("stardew:", sorted(os.listdir("assets/stardew"))[:12])
print("_new:", sorted(os.listdir("assets/_new"))[:12])
