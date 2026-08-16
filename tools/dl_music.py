# 下载 Kenney RPG/Digital 音频包并解压
import glob
import os
import urllib.request
import zipfile

URLS = {
    "rpg": "https://kenney.nl/media/pages/assets/rpg-audio/8e99002d76-1677590336/kenney_rpg-audio.zip",
    "digital": "https://kenney.nl/media/pages/assets/digital-audio/216eac4753-1677590265/kenney_digital-audio.zip",
}
os.makedirs("assets/audio/kenney2", exist_ok=True)
for name, url in URLS.items():
    zf = f"_dl_{name}.zip"
    try:
        urllib.request.urlretrieve(url, zf)
        zipfile.ZipFile(zf).extractall("assets/audio/kenney2")
        os.remove(zf)
        print(name, "OK")
    except Exception as ex:
        print(name, "FAIL", ex)
print("文件数:", len(glob.glob("assets/audio/kenney2/**/*.*", recursive=True)))
