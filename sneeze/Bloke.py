import math

from sneeze.Actor import Actor
from sneeze.Sprite import Sprite
from sneeze.Types import *
from typing import Tuple

class Bloke(Actor):
    def __init__(self, bloke_json):
        super().__init__()
        self.sprite = Sprite.load(bloke_json['sprite'])
        self.move_to(Pos(bloke_json['start']['x'], bloke_json['start']['y']))
        self.type = bloke_json['type']
        self.speed = self.max_speed / 2
        self.sneeze_length = self.sprite.get_phase_length('sneeze')
        self.current_sneeze_frame = None
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

    def _start_sneezing(self):
        self._next_frame('sneeze')
        self.current_sneeze_frame = 1

    def _finish_sneezing(self) -> Tuple[bool, bool]:
        "Returns (was_sneezing, finished_sneezing)"
        if self.current_sneeze_frame is None:
            # not sneezing
            return False, False
        # the bloke is already sneezing, let him continue the animation
        self._next_frame('sneeze')
        self.current_sneeze_frame += 1
        if self.current_sneeze_frame >= self.sneeze_length:
            # sneezing finished, next frame will start chasing again
            self.current_sneeze_frame = None
            return True, True
        return True, False

    def _move_patrol(self, player_pos: Pos):
        was_sneezing, finished_sneezing = self._finish_sneezing()
        if was_sneezing:
            if finished_sneezing:
                self.next_waypoint = (self.next_waypoint + 1) % len(self.waypoints)
            return

        waypoint_pos = self.waypoints[self.next_waypoint]
        vector = Pos(waypoint_pos.x - self.pos.x, waypoint_pos.y - self.pos.y)
        vec_len = math.sqrt(vector.x * vector.x + vector.y * vector.y)
        if vec_len >= self.speed:
            scale = self.speed / vec_len
            self.pos = Pos(
                self.pos.x + vector.x * scale,
                self.pos.y + vector.y * scale)
            self._next_frame('walk')
        else:
            self.pos = waypoint_pos
            self._start_sneezing()

    def _move_chase(self, player_pos: Pos):
        was_sneezing, _ = self._finish_sneezing()
        if was_sneezing:
            return

        # chasing the player
        dx = player_pos.x - self.pos.x
        dy = player_pos.y - self.pos.y

        dist_from_player = dx * dx + dy * dy
        if dist_from_player > self.action_radius:
            # move towards the player
            alpha = math.atan(abs(dy)/abs(dx))
            self.pos = Pos(
                self.pos.x + self.speed * math.copysign(math.cos(alpha), dx),
                self.pos.y + self.speed * math.copysign(math.sin(alpha), dy)
            )
            self._next_frame('walk')
        else:
            self._start_sneezing()
