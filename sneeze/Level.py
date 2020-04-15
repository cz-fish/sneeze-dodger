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
    def point_in_limits(self, point: Pos) -> bool:
        last = self.limits[-1]
        answer = False
        for vertex in self.limits:
            if (vertex.y > point.y) != (last.y > point.y) \
                and (point.x < (last.x - vertex.x) * (point.y - vertex.y) / (last.y - vertex.y) + vertex.x):
                answer = not answer
            last = vertex
        return answer

    def __init__(self, level_file):
        with open(level_file, 'rt') as fp:
            self.info = json.load(fp)

        self.limits = [Pos(lim['x'], lim['y']) for lim in self.info['limits']]
        finish = self.info['finish']
        self.finish = pygame.Rect(
            finish['x1'], finish['y1'],
            finish['x2'] - finish['x1'],
            finish['y2'] - finish['y1']
        )

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
            if self.finish.collidepoint(new_pos):
                # TODO: level finished
                print("Level finished")
                return old_pos
            if self.point_in_limits(new_pos):
                return new_pos
            return old_pos

        self.player.move(inputs, collision)
        # TODO: move other actors

    def add_layers(self, layer_dict: Dict[int, pygame.Surface]) -> None:
        self.background.add_layers(layer_dict)

        # Draw boundary lines onto Debug layer
        if False:
            limit_lines = pygame.Surface(Setup.logical_size, pygame.SRCALPHA, 32)
            pygame.draw.polygon(limit_lines, (255,0,0), self.limits, 5)
            pygame.draw.rect(limit_lines, (50, 70, 200), self.finish, 5)
            layer_dict[RenderLayers.Debug] = limit_lines
