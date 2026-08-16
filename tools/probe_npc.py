# 查角色图尺寸（选正确的 NPC 素材）
import glob
import os

import pygame

pygame.init()
NPC = "assets/_new/Lively_NPCs_v3.0/individual sprites/medieval"
for name in ["elder", "princess", "captain", "villager_01", "beggar", "priestess"]:
    files = sorted(glob.glob(f"{NPC}/{name}/*.png"))
    if files:
        i = pygame.image.load(files[0])
        print(name, files[0].split("/")[-1], i.get_size())

# 暗影兽：Bitcrawl Wraith
w = glob.glob("assets/_new/Bitcrawl_Free_Roguelike_v1/Characters/Normal_Outline_Sheet/*Wraith*.png")
if w:
    i = pygame.image.load(w[0])
    print("Wraith", os.path.basename(w[0]), i.get_size())

# Sea 分层背景尺寸
for f in ["BG_DAY", "BOAT", "OCEANF_DAY", "OCEANB_DAY", "CLOUDS_DAY", "SUN_DAY"]:
    p = glob.glob(f"assets/_new/FREE - Pixel Art Sidescroller Sea Backgrounds/**/{f}.png",
                   recursive=True)
    if p:
        i = pygame.image.load(p[0])
        print(f, i.get_size())
pygame.quit()
