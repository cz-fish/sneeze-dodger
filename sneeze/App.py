import pygame
import pygame.freetype

from collections import namedtuple
from sneeze.Actor import Actor
from sneeze.Color import Color
from sneeze.Controller import Controller
from sneeze.GameStats import GameStats
from sneeze.Level import Level
from sneeze.Player import Player
from sneeze.Setup import Setup
from sneeze.Sprite import Sprite
from sneeze.Types import *
from typing import Dict, List

Update = namedtuple('Update', ['surface', 'src_rect', 'dst_rect'])

def centered_rect(center, rect):
    return pygame.Rect(
        int(center.x) - rect.w // 2,
        int(center.y) - rect.h // 2,
        rect.w,
        rect.h)

def make_update_rect(draw_rect):
    # FIXME: why do we have to add some pixels around?
    #        if we don't, the moving side is flickering
    return draw_rect.inflate(15, 15)


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
        # Sprite of the shadow under the player
        self.shadow = Sprite.load('shadow')
        # Animation frame for anything that's moving, other than the actors
        self.anim_frame = 0
        # rect of the distance line from the previous frame for clearing
        self.last_line_rect = None

    def tick(self):
        self.clock.tick(Setup.fps)
        inputs = self.controller.get_inputs()
        self.level.tick(inputs)
        self.game_stats.tick(self.clock.get_time(), self.level)
        self.anim_frame += 1

    def _render_shadow(self, clears, redraws, updates):
        blit = self.shadow.get_blit('pulse', self.anim_frame)

        if self.game_stats.prev_vector is not None:
            # Clear previous shadow
            prev_vec = self.game_stats.prev_vector
            clears.append(centered_rect(prev_vec[0], blit.rect))

        if self.game_stats.vector is not None:
            # Draw new shadow
            vec = self.game_stats.vector
            draw_rect = centered_rect(vec[0], blit.rect)
            redraws.append(Update(blit.surface, blit.rect, draw_rect))
            updates.append(make_update_rect(draw_rect))
    
    def render(self, first_render=False):
        clears: List[pygame.Rect] = []
        redraws: List[Update] = []
        updates: List[pygame.Rect] = []

        hud_right = Setup.logical_size[0] - 630

        if first_render:
            "Redraw the whole screen; should be done just once at the beginning"
            layer_map: Dict[int, pygame.Surface] = {}
            self.level.add_layers(layer_map)
            self.static_layers = sorted(layer_map.items(), key=lambda x: x[0])
            clears.append(
                pygame.Rect(0, 0, Setup.logical_size[0], Setup.logical_size[1])
            )
        else:
            self._render_shadow(clears, redraws, updates)

            actors = self.level.get_actors()
            # actors ordered by y-coord
            for actor in sorted(actors, key=lambda a: a.pos.y):
                if not actor.sprite:
                    continue
                sprite = actor.sprite
                anim, phase = actor.animation
                blit = sprite.get_blit(anim, phase)

                clear_rect = centered_rect(actor.prev_pos, blit.rect)
                draw_rect = centered_rect(actor.pos, blit.rect)
                clears.append(clear_rect)
                redraws.append(Update(blit.surface, blit.rect, draw_rect))
                updates.append(make_update_rect(draw_rect))

        # Clear hud
        clears.append(pygame.Rect(75, 75, 200, 75))
        clears.append(pygame.Rect(hud_right, 75, 700, 75))

        # Clear distance line
        if self.last_line_rect is not None:
            clears += [make_update_rect(self.last_line_rect)]

        # FIXME: somewhere here, we'll have to transform if window_size != logical_size
        
        # Clear all rects that need clearing
        for i, layer in self.static_layers:
            for clear in clears:
                self.display.blit(layer, clear.topleft, clear)

        # Draw new distance line
        if self.game_stats.vector is not None:
            vec = self.game_stats.vector
            self.last_line_rect = pygame.draw.line(
                self.display,
                Color.shadow,
                vec[0],
                vec[1],
                5
            )
            updates += [self.last_line_rect]

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

        avg_dist = f'{self.game_stats.distance_avg() / 10:.1f}'
        min_dist_int = self.game_stats.distance_min()
        min_dist = '' if min_dist_int < 0 else f'{min_dist_int / 10:.1f}'
        score = f'Dist: AVG {avg_dist} / MIN {min_dist}'
        self.font.render_to(self.display, (hud_right, 75), score, fgcolor=Color.score)

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
