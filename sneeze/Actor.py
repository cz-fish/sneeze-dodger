import abc

from sneeze.Sprite import Sprite
from sneeze.Types import *
from typing import Optional


class Actor(abc.ABC):
    def __init__(self):
        self.pos = Pos(0, 0)
        self.prev_pos = Pos(0, 0)
        self.speed_vec = Pos(0, 0)
        self.max_speed = 10
        self.accel = 5
        self.slowdown = 1.3
        self.sprite: Optional[Sprite] = None
        self.animation = Animation('idle', 0)

    @abc.abstractmethod
    def move(self, player_pos: Pos) -> None:
        pass
    
    def move_to(self, pos: Pos) -> None:
        self.prev_pos = self.pos
        self.pos = Pos(pos.x, pos.y)

    def update_speed(self, xmove: int, ymove: int) -> None:
        def one_axis(velocity, input):
            if input == -1:
                return max(-self.max_speed, velocity - self.accel)
            elif input == 1:
                return min(self.max_speed, velocity + self.accel)
            else:
                return velocity / self.slowdown

        self.speed_vec = Pos(
            one_axis(self.speed_vec.x, xmove),
            one_axis(self.speed_vec.y, ymove)
        )

    def get_size(self) -> Pos:
        if self.sprite is None:
            return Pos(0, 0)
        return self.sprite.get_size()
