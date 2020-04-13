from sneeze.Actor import Actor
from sneeze.Sprite import Sprite

class Bloke(Actor):
    def __init__(self):
        super.__init__(self)
        self.sprite = Sprite.load('bloke')
