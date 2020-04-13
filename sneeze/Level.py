import json
import pygame

from sneeze.Actor import Actor
from sneeze.Background import Background
from sneeze.Bloke import Bloke
from sneeze.Player import Player
from sneeze.Setup import Setup
from sneeze.Types import *
from typing import Dict, List


class Level:
    class Limit:
        class StayOn:
            Left = 0
            Right = 1
            Above = 2
            Below = 3
            fromStr = {
                'left': Left,
                'right': Right,
                'above': Above,
                'below': Below
            }

        def __init__(self, limit_json):
            StayOn = Level.Limit.StayOn
            self.stay_on = StayOn.fromStr[limit_json['stayon']]
            self.a = Pos(limit_json['x1'], limit_json['y1'])
            self.b = Pos(limit_json['x2'], limit_json['y2'])
            self.finish = 'finish' in limit_json and limit_json['finish']
            self.diff = Pos(self.b.x - self.a.x, self.b.y - self.a.y)

            # Check that coords are in the right order so that we can
            # simplift the code
            if self.stay_on in [StayOn.Left, StayOn.Right]:
                assert(self.a.y > self.b.y)
            elif self.stay_on in [StayOn.Above, StayOn.Below]:
                assert(self.a.x < self.b.x)

        def within(self, point: Pos) -> bool:
            StayOn = Level.Limit.StayOn
            if self.stay_on in [StayOn.Left, StayOn.Right]:
                if point.y < self.b.y or point.y > self.a.y:
                    return True
                dy = point.y - self.a.y
                x = self.a.x + dy * self.diff.x / self.diff.y
                return (point.x < x) == (self.stay_on == StayOn.Left)
            else:
                if point.x < self.a.x or point.x > self.b.x:
                    return True
                dx = point.x - self.a.x
                y = self.a.y + dx * self.diff.y / self.diff.x
                return (point.y < y) == (self.stay_on == StayOn.Above)


    def __init__(self, level_file):
        with open(level_file, 'rt') as fp:
            self.info = json.load(fp)

        self.limits = [Level.Limit(lim) for lim in self.info['limits']]

        self.background = Background(self.info['layers'])

        self.player = Player()
        self.player.move_to(Pos(
            self.info['player']['start']['x'],
            self.info['player']['start']['y']
        ))
        # FIXME: load actors from the level json
        self.actors: List[Actor] = []

    def get_actors(self) -> List[Actor]:
        return [self.player] + self.actors

    def tick(self, inputs: Inputs) -> None:
        def collision(old_pos: Pos, speed_vec: Pos) -> Pos:
            new_pos = Pos(old_pos.x + speed_vec.x, old_pos.y + speed_vec.y)
            # FIXME: just replace all of this with point in polygon test
            for limit in self.limits:
                if not limit.within(new_pos):
                    if limit.finish:
                        # TODO: level finished
                        pass
                    return old_pos
            return new_pos

        self.player.move(inputs, collision)
        # TODO: move other actors

    def add_layers(self, layer_dict: Dict[int, pygame.Surface]) -> None:
        self.background.add_layers(layer_dict)

        # Draw boundary lines onto Debug layer
        """
        limit_lines = pygame.Surface(Setup.logical_size, pygame.SRCALPHA, 32)
        for limit in self.info['limits']:
            pygame.draw.line(
                limit_lines,
                (255,0,0),
                (limit['x1'], limit['y1']),
                (limit['x2'], limit['y2'])
            )
        layer_dict[RenderLayers.Debug] = limit_lines
        """
