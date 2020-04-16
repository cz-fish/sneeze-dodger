import math

from sneeze.Actor import Actor
from sneeze.Sprite import Sprite
from sneeze.Types import *

class Bloke(Actor):
    def __init__(self, bloke_json):
        super().__init__()
        self.sprite = Sprite.load(bloke_json['sprite'])
        self.move_to(Pos(bloke_json['start']['x'], bloke_json['start']['y']))
        self.type = bloke_json['type']
        if self.type == 'patrol':
            self._init_patrol(bloke_json)
        elif self.type == 'chase':
            self._init_chase(bloke_json)

    def _init_patrol(self, bloke_json):
        self.move_fn = self._move_patrol
        self.waypoints = [self.pos]  # starting pos is the first waypoint
        for wp in bloke_json['waypoints']:
            self.waypoints.append(Pos(wp['x'], wp['y']))
        # Make sure there are always at least 2 waypoints.
        # Special case - only 2 points and both the same - the guy
        # stays in place.
        if len(self.waypoints) == 1:
            self.waypoints += [self.waypoints[-1]]
        self.next_waypoint = 1

    def _init_chase(self, bloke_json):
        self.action_radius = bloke_json['action_radius']
        self.move_fn = self._move_chase

    def move(self, player_pos: Pos) -> None:
        self.prev_pos = self.pos
        self.move_fn(player_pos)

    def _next_frame(self, action):
        if self.animation.action == action:
            self.animation = Animation(action, self.animation.phase + 1)
        else:
            self.animation = Animation(action, 0)

    def _move_patrol(self, player_pos: Pos):
        # TODO: move towards the next waypoint
        pass

    def _move_chase(self, player_pos: Pos):
        "chase the player"
        dx = player_pos.x - self.pos.x
        dy = player_pos.y - self.pos.y

        dist_from_player = dx * dx + dy * dy
        if dist_from_player > self.action_radius:
            # chasing
            alpha = math.atan(abs(dy)/abs(dx))
            speed = self.max_speed / 2
            self.pos = Pos(
                self.pos.x + speed * math.copysign(math.cos(alpha), dx),
                self.pos.y + speed * math.copysign(math.sin(alpha), dy)
            )
            self._next_frame('walk')
        else:
            # sneezing
            self._next_frame('sneeze')
