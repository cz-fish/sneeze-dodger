import pygame

from collections import namedtuple
from typing import Dict

SpriteMeta = namedtuple('SpriteInfo', ['width', 'height', 'phases'])

# FIXME: this should be in some config file
sprite_meta: Dict[str, SpriteMeta] = {
    'guy': SpriteMeta(142, 150, {
        'walk': (0, 6)
    }),
    'bloke': SpriteMeta(128, 180, {
        'walk': (0, 6),
        'sneeze': (6, 5)
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
            first, num = meta.phases[phase]
            frame = first + frame_no % num

        return Blit(self.surface, (frame * meta.width, 0, meta.width, meta.height))


sprite_cache: Dict[str, Sprite] = {}
