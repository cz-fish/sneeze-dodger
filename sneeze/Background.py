import pygame

from sneeze.Types import *
from typing import Dict, List

class Background:
    def __init__(self, layers):
        self.surfaces: List[pygame.Surface] = []
        for layer in layers:
            surface = pygame.image.load(f'levels/{layer["file"]}')
            if layer['type'] == 'overlay':
                surface = surface.convert_alpha()
            self.surfaces.append(surface)

    def add_layers(self, layer_dict: Dict[int, pygame.Surface]) -> None:
        # Add background layer
        layer_dict[RenderLayers.Background] = self.surfaces[0]
        # And all other (overlay) layers
        for i, surface in enumerate(self.surfaces[1:]):
            layer_dict[i + RenderLayers.Overlays] = surface

