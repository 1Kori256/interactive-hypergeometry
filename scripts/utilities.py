"""
Useful function for the app
"""


import json
from functools import lru_cache
import os
import pygame


def load_config(path) -> dict:
    
    """Load all configs
    
    Keyword argument:
    path - path to config folder
     
    Returns:
    dict: dict of all configs
    """
    
    config = {}
    config_paths = os.listdir(path)
    
    for current_path in config_paths:
        if current_path[-12:] == "_config.json":
            with open(f"{path}/{current_path}") as file:
                current_config = json.load(file)
            config[current_path[:-12]] = current_config
        
    return config
    

def debug(surface, font, pos, color, *args) -> None:
    
    """Function that displays certain values, used for debugging purposes.
    
    Keyword arguments:
    surface - surface to blit debug values
    font - font to use to blit debug values
    *args - values to show in debugging menu
    """
    
    surface.blit(_debug_surface(font, tuple(str(arg) for arg in args)), pos)


@lru_cache(maxsize=128)
def _debug_surface(font, lines):
    """Reuse the static help text and repeated FPS/subobject labels."""
    debug_surface = pygame.Surface((800, 8 + 16 * max(0, len(lines) - 1)))
    debug_surface.set_colorkey((0, 0, 0))
    for index, line in enumerate(lines):
        debug_surface.blit(font.render(line, True, (240, 240, 240)), (0, index * 16))
    return debug_surface