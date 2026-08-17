import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
pygame.init()
pygame.display.set_mode((480, 270))
from core.main import Game
g = Game()
print('Game init OK')
print('Has _manual_save:', hasattr(g, '_manual_save'))
from core import save as S
d = S.load()
print('Current save:', d)
g._manual_save()
d2 = S.load()
print('After manual save:', d2)
pygame.quit()