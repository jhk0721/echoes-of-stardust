# 素材生成管线：程序化合成全部音频与精灵图
# 策略：零下载、零版权风险 —— 音效用波形合成，图片用几何绘制，字体走系统字体链
# 这同时是"美工差"的最优解：全部素材由代码生成，风格天然统一
import math
import os
import random
import struct
import wave

from core import config

SPRITE_CHECKS = ["harp_real.png"]


# ---------- 音频：波形合成 ----------
def _sine(freq, dur, vol=0.5, decay=6.0, overtones=()):
    n = int(44100 * dur)
    tot = 1.0 + sum(a for _, a in overtones)
    out = []
    for i in range(n):
        t = i / 44100.0
        env = math.exp(-decay * t)
        v = math.sin(2 * math.pi * freq * t)
        for fm, a in overtones:
            v += a * math.sin(2 * math.pi * freq * fm * t)
        out.append(int(32767 * vol * env * v / tot))
    return out


def _save_wav(name, samples, rate=44100):
    path = os.path.join(config.AUDIO, name + ".wav")
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack("<%dh" % len(samples), *samples))


def gen_audio():
    # 四元素拨弦（风高音/火低音/水中音/地重低音）
    base = {"wind": 880, "fire": 220, "water": 440, "earth": 110}
    for note, f in base.items():
        _save_wav("note_" + note, _sine(f, 0.5, 0.5, 7.0,
                                         ((2.0, 0.4), (3.0, 0.2), (0.5, 0.5))))
    # UI 音效
    _save_wav("ui_move", _sine(660, 0.06, 0.3, 20.0))
    _save_wav("ui_ok", _sine(880, 0.12, 0.4, 10.0, ((2.0, 0.3),)))
    _save_wav("ui_select", _sine(440, 0.10, 0.35, 14.0))
    # 共鸣：不和谐泛音叠加，象征"记忆碰撞"
    _save_wav("resonance", _sine(520, 0.35, 0.5, 5.0, ((1.5, 0.5), (2.0, 0.35), (2.5, 0.2))))
    # 受伤 / 敌人弹
    _save_wav("hurt", _sine(160, 0.25, 0.5, 8.0, ((1.5, 0.4),)))
    # 氛围低语（柔和低通噪声，两秒循环）
    n = int(44100 * 2.0)
    prev = 0.0
    noise = []
    for i in range(n):
        prev = 0.9 * prev + 0.1 * random.uniform(-1.0, 1.0)
        noise.append(int(6000 * prev * (1.0 - i / n)))
    _save_wav("whisper", noise)
    # 雨声（低通噪声，两秒循环，可无缝 loop）
    n = int(44100 * 2.0)
    prev = 0.0
    rain = []
    rng = random.Random(7)
    for i in range(n):
        w = rng.uniform(-1.0, 1.0)
        prev = 0.92 * prev + 0.08 * w
        rain.append(int(14000 * (0.7 * prev + 0.3 * w)))
    _save_wav("rain", rain)
    # BGM：竖琴风氛围琶音（Am-F-C-G 分解和弦，16 秒循环，22050Hz）
    gen_bgm()


def gen_bgm():
    """程序化 BGM：A 小调琶音 + 低音点（Am-F-C-G 分解和弦，16 秒循环）"""
    rate = 22050
    dur = 16.0
    n = int(rate * dur)
    out = [0] * n
    # 和弦进行（每 8 个十六分换一个和弦）
    prog = [
        [220.0, 261.63, 329.63, 440.0],   # Am: A3 C4 E4 A4
        [174.61, 220.0, 261.63, 349.23],  # F:  F3 A3 C4 F4
        [261.63, 329.63, 392.0, 523.25],  # C:  C4 E4 G4 C5
        [196.0, 246.94, 293.66, 392.0],   # G:  G3 B3 D4 G4
    ]
    beat = 0.25
    total = int(dur / beat)
    for i in range(total):
        chord = prog[(i // 8) % 4]
        f = chord[i % 4]
        for k in range(int(beat * rate)):
            t = k / rate
            env = math.exp(-6.0 * t)
            v = math.sin(2 * math.pi * f * t) + 0.2 * math.sin(2 * math.pi * f * 2 * t)
            idx = int((i * beat + t) * rate)
            if idx < n:
                out[idx] += int(32767 * 0.13 * env * v)
    # 低音点：每拍根音低八度
    for i in range(0, total, 8):
        chord = prog[(i // 8) % 4]
        bass = chord[0] / 2
        for k in range(int(2.0 * rate)):
            t = k / rate
            env = math.exp(-2.5 * t)
            v = math.sin(2 * math.pi * bass * t) + 0.3 * math.sin(2 * math.pi * bass * 2 * t)
            idx = int((i * beat + t) * rate)
            if idx < n:
                out[idx] += int(32767 * 0.10 * env * v)
    for k in range(rate // 2):
        out[k] = int(out[k] * k / (rate // 2))
        out[n - 1 - k] = int(out[n - 1 - k] * k / (rate // 2))
    _save_wav("bgm", out, rate=rate)


# ---------- 精灵图：几何绘制 ----------
def _planet(rgb, size=48):
    import pygame
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = cy = size // 2
    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            d = math.sqrt(dx * dx + dy * dy)
            if d > cx:
                continue
            t = d / cx  # 0=中心 1=边缘
            col = [int(rgb[i] * (1.0 - 0.65 * t)) for i in range(3)]
            if random.random() < 0.02 * (1.0 - t):  # 表面亮斑
                col = [min(255, c + 60) for c in col]
            s.set_at((x, y), (*col, 255))
    # 边缘光晕（记忆星球特征）
    pygame.draw.circle(s, (*rgb, 90), (cx, cy), cx + 3, 2)
    return s


def gen_sprites():
    import pygame
    pygame.init()

    # 竖琴：深蓝琴身 + 金色琴弦
    hp = pygame.Surface((48, 64), pygame.SRCALPHA)
    pygame.draw.arc(hp, (34, 46, 102), (8, 6, 32, 52), math.radians(20), math.radians(160), 4)
    pygame.draw.rect(hp, (44, 32, 70), (12, 56, 24, 5))
    pygame.draw.line(hp, config.GOLD, (10, 30), (38, 22), 2)  # 顶梁
    for i in range(5):
        x = 14 + i * 5
        pygame.draw.line(hp, config.GOLD, (x, 12), (x - 2, 56), 1)
    pygame.image.save(hp, os.path.join(config.SPRITES, "harp.png"))

    # 记忆星球（蓝 / 琥珀 两色调色板）
    pygame.image.save(_planet((86, 140, 210)), os.path.join(config.SPRITES, "planet_blue.png"))
    pygame.image.save(_planet((226, 168, 108)), os.path.join(config.SPRITES, "planet_amber.png"))

    # 音符弹丸（4x4 白色光点，运行时染色）
    b = pygame.Surface((8, 8), pygame.SRCALPHA)
    pygame.draw.circle(b, (255, 255, 255), (4, 4), 3)
    pygame.image.save(b, os.path.join(config.SPRITES, "bolt.png"))

    pygame.quit()


def ensure():
    """素材缺失时自动生成；已有则跳过"""
    need = not all(os.path.exists(os.path.join(config.SPRITES, f)) for f in SPRITE_CHECKS)
    if need:
        gen_sprites()
    if not os.listdir(config.AUDIO):
        gen_audio()


if __name__ == "__main__":
    gen_audio()
    gen_sprites()
    print("素材生成完毕：", os.listdir(config.AUDIO), os.listdir(config.SPRITES))
