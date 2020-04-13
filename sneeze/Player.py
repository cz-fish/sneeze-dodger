from sneeze.Actor import Actor
from sneeze.Sprite import Sprite
from sneeze.Types import *

class Player(Actor):
    def __init__(self):
        super().__init__()
        self.sprite = Sprite.load('guy')

    def move(self, inputs: Inputs, collision) -> None:
        self.update_speed(inputs.xvalue, inputs.yvalue)
        new_pos = collision(self.pos, self.speed_vec)
        if new_pos == self.pos:
            self.speed_vec = Pos(0, 0)
        self.pos = new_pos

        # walk phase; reset if not moving
        if abs(self.speed_vec.x) < 2 and abs(self.speed_vec.y) < 2:
            self.animation = Animation('idle', 0)
        else:
            key, phase = self.animation
            if key == 'walk':
                self.animation = Animation(key, phase + 1)
            else:
                self.animation = Animation('walk', 0)

