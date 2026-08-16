# 查看素材尺寸与结构
import glob
import os

import pygame

pygame.init()
for f in ["assets/_new/Ocean Sunrise.png", "assets/_new/beach1.png",
          "assets/_new/Drifter.png", "assets/_new/HR_Ocean Sunrise.png"]:
    if os.path.exists(f):
        i = pygame.image.load(f)
        print(os.path.basename(f), i.get_size())
print()
print("Lively_NPCs:", os.listdir("assets/_new/Lively_NPCs_v3.0")[:15])
print("Sea:", [os.path.basename(f) for f in
               glob.glob("assets/_new/FREE - Pixel Art Sidescroller Sea Backgrounds/**/*.png",
                         recursive=True)][:15])
print("stardew 内:", [f.split("assets/stardew/")[1] for f in
                      glob.glob("assets/stardew/**/*.png", recursive=True)][:10])
pygame.quit()
