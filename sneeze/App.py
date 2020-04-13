import pygame

from sneeze.Actor import Actor
from sneeze.Color import Color
from sneeze.Controller import Controller
from sneeze.Level import Level
from sneeze.Player import Player
from sneeze.Setup import Setup
from sneeze.Types import *
from typing import Dict, List

class App:
    def __init__(self):
        self.controller = Controller()
        self.display = pygame.display.set_mode(Setup.window_size)
        pygame.display.set_caption('Sneeze Dodger')
        self.clock = pygame.time.Clock()
        self.level = Level()

    def tick(self):
        self.clock.tick(Setup.fps)
        inputs = self.controller.get_inputs()
        self.level.tick(inputs)

    def render(self):
        layers: Dict[int, pygame.Surface] = {}

        self.level.add_layers(layers)

        actor_layer = pygame.Surface(Setup.logical_size, pygame.SRCALPHA, 32)
        # buf = pygame.Surface(Setup.logical_size, pygame.SRCALPHA, 32)

        # TODO: level.draw_background()
        actors = self.level.get_actors()
        # player first
        actor_order = ['player'] + [a for a in actors.keys() if a != 'player']

        blits = []
        for actor_name in actor_order:
            actor = actors[actor_name]
            if not actor.sprite:
                continue
            sprite = actor.sprite
            anim, phase = actor.animation
            blit = sprite.get_blit(anim, phase)
            width = blit.rect[2]
            height = blit.rect[3]
            left = actor.pos.x - width // 2
            top = actor.pos.y - height // 2
            blits += [(blit.surface, (left, top), blit.rect)]

        actor_layer.blits(blit_sequence=blits)
        layers[RenderLayers.Actors] = actor_layer

        # FIXME: somewhere here, we'll have to transform if window_size != logical_size
        for k, surface in sorted(layers.items(), key=lambda x: x[0]):
            self.display.blit(surface, (0, 0), (0, 0, Setup.logical_size[0], Setup.logical_size[1]))
        pygame.display.update()

    def run(self):
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.stop()

            self.tick()
            self.render()

    def stop(self):
        self.running = False
