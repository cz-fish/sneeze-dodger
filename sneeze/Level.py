import json
import pygame

from sneeze.Actor import Actor
from sneeze.Background import Background
from sneeze.Bloke import Bloke
from sneeze.Player import Player
from sneeze.Setup import Setup
from sneeze.Types import *
from typing import Dict


class Level:
    def __init__(self):
        with open('levels/lev1.json', 'rt') as fp:
            self.info = json.load(fp)
        self.background = Background(self.info['layers'])

        self.player = Player()
        self.player.pos = Pos(
            self.info['player']['start']['x'],
            self.info['player']['start']['y']
        )

        self.actors: Dict[str, Actor] = {
            'player': self.player
        }

    def get_actors(self) -> Dict[str, Actor]:
        return self.actors

    def tick(self, inputs: Inputs) -> None:
        def collision(old_pos: Pos, speed_vec: Pos) -> Pos:
            x = max(0, min(Setup.logical_size[0], old_pos.x + speed_vec.x))
            y = max(0, min(Setup.logical_size[1], old_pos.y + speed_vec.y))
            return Pos(x, y)

        self.player.move(inputs, collision)
        # TODO: move other actors

    def add_layers(self, layer_dict: Dict[int, pygame.Surface]) -> None:
        self.background.add_layers(layer_dict)


    class State:
        # FIXME: all of this class is deprecated
        maxspeed = 10
        accel = 5
        slowdown = 1.3
        joy_thresh = 0.3
        bloke_action_radius = 3600

        def __init__(self):
            self.x = Setup.log_size[0] / 2
            self.y = Setup.log_size[1] / 2
            self.vec = [0, 0]
            self.phase = 0
            self.bloke = (random.randint(100, Setup.log_size[0] - 100), random.randint(100, Setup.log_size[1] - 100))

        def tick(self, xaxis, yaxis):
            vx = self.vec[0]
            vy = self.vec[1]

            if xaxis < -self.joy_thresh:
                vx = max(-self.maxspeed, vx - self.accel)
            elif xaxis > self.joy_thresh:
                vx = min(self.maxspeed, vx + self.accel)
            else:
                vx /= self.slowdown

            if yaxis < -self.joy_thresh:
                vy = max(-self.maxspeed, vy - self.accel)
            elif yaxis > self.joy_thresh:
                vy = min(self.maxspeed, vy + self.accel)
            else:
                vy /= self.slowdown

            self.x = max(0, min(Setup.log_size[0], self.x + vx))
            self.y = max(0, min(Setup.log_size[1], self.y + vy))
            self.vec = [vx, vy]

            # walk phase; reset if not moving
            if abs(vx) < 2 and abs(vy) < 2:
                self.phase = 0
            else:
                self.phase += 1

            # the bloke
            if self.bloke_moves():
                dx = self.x - self.bloke[0]
                dy = self.y - self.bloke[1]
                alpha = math.atan(abs(dy)/abs(dx))
                speed = self.maxspeed / 2
                self.bloke = (
                    self.bloke[0] + speed * math.copysign(math.cos(alpha), dx),
                    self.bloke[1] + speed * math.copysign(math.sin(alpha), dy)
                )

        def get_pos(self):
            return (int(self.x), int(self.y))

        def get_phase(self):
            return self.phase

        def get_bloke(self):
            return (int(self.bloke[0]), int(self.bloke[1]))

        def bloke_moves(self):
            dx = self.x - self.bloke[0]
            dy = self.y - self.bloke[1]
            c = dx * dx + dy * dy
            return c >= self.bloke_action_radius
