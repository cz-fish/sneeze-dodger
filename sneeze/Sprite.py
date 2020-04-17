import pygame

from collections import namedtuple
from typing import Dict

SpriteMeta = namedtuple('SpriteInfo', ['width', 'height', 'phases'])
AnimFrames = namedtuple('AnimFrames', ['first', 'num', 'slowdown'])

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
        'walk': AnimFrames(
            first=0,
            num=6,
            slowdown=2)
    }),
    'bloke': SpriteMeta(128, 180, {
        'walk': AnimFrames(
            first=0,
            num=6,
            slowdown=2),
        'sneeze': AnimFrames(
            first=6,
            num=5,
            slowdown=5)
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

    def get_phase_length(self, phase: str) -> int:
        "Return number of frames of the given animation phase"
        meta = sprite_meta[self.key]
        if phase not in meta.phases:
            return 1
        else:
            return meta.phases[phase].num * meta.phases[phase].slowdown


sprite_cache: Dict[str, Sprite] = {}
