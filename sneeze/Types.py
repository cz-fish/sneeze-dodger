from collections import namedtuple

Animation = namedtuple('Animation', ['action', 'phase'])
Inputs = namedtuple('Inputs', ['xvalue', 'yvalue'])
Pos = namedtuple('Pos', ['x', 'y'])

class RenderLayers:
    Background = 0
    Actors = 1
    Overlays = 2
    Debug = 10