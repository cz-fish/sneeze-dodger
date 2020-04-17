import pygame
import pygame.freetype

from collections import namedtuple
from sneeze.Actor import Actor
from sneeze.Color import Color
from sneeze.Controller import Controller
from sneeze.Level import Level
from sneeze.Player import Player
from sneeze.Setup import Setup
from sneeze.Types import *
from typing import Dict, List

Update = namedtuple('Update', ['surface', 'src_rect', 'dst_rect'])

class App:
    def __init__(self):
        self.controller = Controller()
        self.display = pygame.display.set_mode(Setup.window_size)
        pygame.display.set_caption('Sneeze Dodger')
        pygame.freetype.init()
        self.font = pygame.freetype.Font('font/homoarakhn.ttf', 30)
        self.clock = pygame.time.Clock()
        self.level = Level('levels/lev1.json')
        self.game_stats = GameStats()

    def tick(self):
        self.clock.tick(Setup.fps)
        self.game_stats.time += self.clock.get_time()
        inputs = self.controller.get_inputs()
        self.level.tick(inputs)

    def render(self, first_render=False):
        clears: List[pygame.Rect] = []
        redraws: List[Update] = []
        updates: List[pygame.Rect] = []

        if first_render:
            "Redraw the whole screen; should be done just once at the beginning"
            layer_map: Dict[int, pygame.Surface] = {}
            self.level.add_layers(layer_map)
            self.static_layers = sorted(layer_map.items(), key=lambda x: x[0])
            clears.append(
                pygame.Rect(0, 0, Setup.logical_size[0], Setup.logical_size[1])
            )
        else:
            actors = self.level.get_actors()
            # actors ordered by y-coord
            for actor in sorted(actors, key=lambda a: a.pos.y):
                if not actor.sprite:
                    continue
                sprite = actor.sprite
                anim, phase = actor.animation
                blit = sprite.get_blit(anim, phase)
                half_width = blit.rect.w // 2
                half_height = blit.rect.h // 2

                def make_rect(pos):
                    return pygame.Rect(
                        int(pos.x) - half_width,
                        int(pos.y) - half_height,
                        blit.rect.w,
                        blit.rect.h)

                clear_rect = make_rect(actor.prev_pos)
                draw_rect = make_rect(actor.pos)

                clears.append(clear_rect)
                redraws.append(Update(blit.surface, blit.rect, draw_rect))
                # FIXME: why do we have to add 10 pixels around?
                updates.append(
                    pygame.Rect(
                        draw_rect.x - 10,
                        draw_rect.y - 10,
                        draw_rect.w + 20,
                        draw_rect.h + 20
                    ))

        # Clear hud
        clears.append(pygame.Rect(75, 75, 200, 75))

        # FIXME: somewhere here, we'll have to transform if window_size != logical_size
        
        # Clear all rects that need clearing
        for i, layer in self.static_layers:
            for clear in clears:
                self.display.blit(layer, clear.topleft, clear)

        # Redraw actors that need redrawing
        for update in redraws:
            self.display.blit(
                update.surface,
                update.dst_rect.topleft,
                update.src_rect)

        # Draw layers above the actors
        for i, layer in self.static_layers:
            if i <= RenderLayers.Actors:
                continue
            for update in redraws:
                self.display.blit(
                    layer,
                    update.dst_rect.topleft,
                    update.dst_rect)

        # Draw HUD
        tenths = int(self.game_stats.time // 100)
        time = f'{(tenths // 600) % 100:02}:{(tenths // 10) % 60:02}.{tenths % 10:1}'
        self.font.render_to(self.display, (75, 75), time)

        # Update all rects that were cleared or redrawn
        pygame.display.update(clears + updates)

    def run(self):
        self.running = True

        self.render(first_render=True)
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
