import pygame
from sneeze.App import App

pygame.init()

app = App()
app.run()

pygame.joystick.quit()
pygame.quit()
