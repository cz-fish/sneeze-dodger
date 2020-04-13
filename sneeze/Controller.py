import pygame

from sneeze.Types import *

class Controller:
    joystick_threshold = 0.3

    def __init__(self):
        pygame.joystick.init()
        num_joysticks = pygame.joystick.get_count()
        if not num_joysticks:
            raise RuntimeError("At least one controller is required")

        for j in range(num_joysticks):
            joystick = pygame.joystick.Joystick(j)
            joystick.init()
            print(f'joystick {j}: {joystick.get_name()}')

    def get_inputs(self) -> Inputs:
        joystick = pygame.joystick.Joystick(0)
        xvalue = joystick.get_axis(0)
        yvalue = joystick.get_axis(1)

        def digitize_value(value):
            if value <= -self.joystick_threshold:
                return -1
            elif value >= self.joystick_threshold:
                return 1
            else:
                return 0

        return Inputs(digitize_value(xvalue), digitize_value(yvalue))
