from sneeze.Actor import Actor
from sneeze.Sprite import Sprite

class Bloke(Actor):
    def __init__(self):
        super.__init__(self)
        self.sprite = Sprite.load('bloke')

"""chase the player:
            if self.bloke_moves():
                dx = self.x - self.bloke[0]
                dy = self.y - self.bloke[1]
                alpha = math.atan(abs(dy)/abs(dx))
                speed = self.maxspeed / 2
                self.bloke = (
                    self.bloke[0] + speed * math.copysign(math.cos(alpha), dx),
                    self.bloke[1] + speed * math.copysign(math.sin(alpha), dy)
                )
        def bloke_moves(self):
            dx = self.x - self.bloke[0]
            dy = self.y - self.bloke[1]
            c = dx * dx + dy * dy
            return c >= self.bloke_action_radius
"""
