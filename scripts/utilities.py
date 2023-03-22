"""
Useful function for the app
"""


import json
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
    
    debug_surface = pygame.Surface((800, 8 + 16 * (len(args) - 1)))
    debug_surface.set_colorkey((0, 0, 0))
    for i, arg in enumerate(args):
        text_object = font.render(f"{arg}", True, (240,240,240))
        debug_surface.blit(text_object, (0, i * 16))
    surface.blit(debug_surface, pos)