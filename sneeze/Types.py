from collections import namedtuple

Animation = namedtuple('Animation', ['action', 'phase'])
Inputs = namedtuple('Inputs', ['xvalue', 'yvalue'])
Pos = namedtuple('Pos', ['x', 'y'])

class RenderLayers:
    Background = 0
    Actors = 1
    Overlays = 2
    Debug = 10


class GameStats:
    def __init__(self):
        self.immunity = 100
        self.time = 0.0
        self.score = 0
        