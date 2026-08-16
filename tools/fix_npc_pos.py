# 修正 NPC 站位（站到海面/船/沙滩，不浮空）
p = "core/story/map_scene.py"
s = open(p, encoding="utf-8").read()
for old, new in [('"npc_pos": (300, 150)', '"npc_pos": (300, 195)'),
                 ('"npc_pos": (300, 160)', '"npc_pos": (300, 200)'),
                 ('"npc_pos": (150, 150)', '"npc_pos": (150, 195)'),
                 ('"npc_pos": (240, 170)', '"npc_pos": (240, 205)'),
                 ('"npc_pos": (340, 150)', '"npc_pos": (340, 195)')]:
    s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
print("站位修正完成")
