import pygame

from collections import namedtuple
from typing import Dict

SpriteMeta = namedtuple('SpriteInfo', ['width', 'height', 'phases'])

# FIXME: this should be in some config file
sprite_meta: Dict[str, SpriteMeta] = {
    # sprite_name -> (
    #     width,
    #     height,
    #     phases {phase_name -> (
    #         first_frame,
    #         num_frames,
    #         slowdown
    #     )})
    'guy': SpriteMeta(142, 150, {
        'walk': (0, 6, 2)  # from frame 0, 6 frames, slowdown 2x
    }),
    'bloke': SpriteMeta(128, 180, {
        'walk': (0, 6, 2),  # from frame 0, 6 frames, slowdown 2x
        'sneeze': (6, 5, 5)  # from frame 6, 5 frames, slowdown 5x
    })
}

Blit = namedtuple('Blit', ['surface', 'rect'])


class Sprite():
    @classmethod
    def load(cl, key):
        if not key in sprite_cache:
            sprite_cache[key] = Sprite(key)
        return sprite_cache[key]

    def __init__(self, key):
        self.key = key
        self.surface = pygame.image.load(f'sprites/{key}.png').convert_alpha()

    def get_blit(self, phase: str, frame_no: int) -> Blit:
        frame = 0
        meta = sprite_meta[self.key]
        if phase in meta.phases:
            first, num, slowdown = meta.phases[phase]
            frame = first + (frame_no // slowdown) % num

        return Blit(
            self.surface,
            pygame.Rect(frame * meta.width, 0, meta.width, meta.height)
        )


sprite_cache: Dict[str, Sprite] = {}
