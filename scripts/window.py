"""
Window object
"""

import time
import pygame
from pygame.locals import *

class Window:
    def __init__(self, app) -> None:
        
        """Initialize Window object.
        
        Keyword arguments:
        app - Main application class
        """
        
        self.app = app
        self.config = app.config
        
        pygame.init()
        
        # Base resolution - "in-game", Scaled resolution - "Real resolution"
        self.base_resolution = self.config["window"]["base_resolution"]
        self.scaled_resolution = self.config["window"]["scaled_resolution"]
        
        # Initialize window variables
        pygame.display.set_icon(pygame.image.load(f"{self.app.path}/data/images/icon.png"))
        pygame.display.set_caption(self.config["window"]["caption"])
        self.window = pygame.display.set_mode(self.scaled_resolution)
        self.app_window = pygame.Surface(self.base_resolution)
        self.clock = pygame.time.Clock()
        self.dt = 0.001
        self.frame_start = time.perf_counter()
        self.fps = 0
        self.frame_history = [self.dt]
        
        pygame.font.init()
        self.font = pygame.font.Font(f"{self.app.path}/data/font/game_font.ttf", 8)
        self.mid_font = pygame.font.Font(f"{self.app.path}/data/font/game_font.ttf", 16)
        self.large_font = pygame.font.Font(f"{self.app.path}/data/font/game_font.ttf", 32)
    
    def calculate_fps(self) -> float:
        avg_dt = sum(self.frame_history) / len(self.frame_history)
        avg_fps = 1 / avg_dt
        return avg_fps    
    
    def render_screen(self) -> None:
        
        """Redner screen"""
        
        self.window.blit(pygame.transform.scale(self.app_window, self.scaled_resolution), (0, 0))
        pygame.display.update()
        self.app_window.fill(self.config["window"]["background_color"])
        
        # Get delta time
        self.dt = time.perf_counter() - self.frame_start
        self.frame_start = time.perf_counter()
        self.frame_history.append(self.dt)
        self.frame_history = self.frame_history[-100:]
        self.fps = round(self.calculate_fps())
        self.clock.tick(60)