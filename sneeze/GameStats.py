import math

from sneeze.Types import Pos
from sneeze.Setup import Setup


class GameStats:
    def __init__(self):
        self.dist_sum = 0
        self.min_dist = -1
        self.samples = 0
        self.vector = None
        self.prev_vector = None
        self.time = 0.0
    
    def tick(self, time, level):
        prev_time = self.time
        self.time += time

        player = level.get_player()
        enemies = level.get_enemies()

        if not enemies:
            return

        player_size = player.get_size()
        px = player.pos.x
        py = player.pos.y + player_size.y // 2

        closest = None
        distance = None

        for e in enemies:
            enemy_size = e.get_size()
            ex = e.pos.x
            ey = e.pos.y + enemy_size.y // 2
            dx = (ex - px) / Setup.pixels_per_meter[0]
            dy = (ey - py) / Setup.pixels_per_meter[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if closest is None or dist < distance:
                closest = Pos(ex, ey)
                distance = dist

        self.prev_vector = self.vector
        self.vector = (Pos(px, py), closest)

        if self.min_dist < 0 or distance < self.min_dist:
            self.min_dist = distance

        if self.time // 1000 > prev_time // 1000:
            self.dist_sum += distance
            self.samples += 1
            if self.samples == 3600:
                # poor man's overflow protection
                self.dist_sum = self.distance_avg() / 10
                self.samples = 1

    def distance_avg(self) -> int:
        "returns average distance from enemies in tenths of meters"
        if self.samples == 0:
            return 0
        return int(self.dist_sum / self.samples * 10)

    def distance_min(self) -> int:
        if self.min_dist < 0:
            return -1
        return int(self.min_dist * 10)
