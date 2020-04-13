import pygame

from sneeze.App import App
from sneeze.Level import Level

pygame.init()

app = App()
app.run()

pygame.joystick.quit()
pygame.quit()
