"""
Renderer object
"""

import pygame
import numpy as np
import scripts.utilities as utilities


class Renderer:
    def __init__(self, app) -> None:
        
        """Initialize Renderer object.
        
        Keyword arguments:
        app - Main application class
        """
        
        self.app = app
        self.config = app.config
        self.scale = 300

        self.default_colors = [
            [0, 0, 0],
            [255, 255, 255],
            [255, 0, 0]]

        self.colors = self.default_colors
        self.controls_label = self.app.window.mid_font.render("Controls", True, (240, 240, 240))
        
    def render(self) -> None:
        
        """Renders everything"""
        
        self.app.window.app_window.fill(self.colors[0])
        self.surface = self.app.window.app_window
        
        space = self.app.vrt_space
        selected = np.zeros(len(space.updated_points), dtype=bool)
        if space.subobjects:
            selected[space.subobjects[space.current_subobject]] = True

        # Screen coordinates and subobject membership are shared by points and edges.
        center = np.asarray(self.app.window.base_resolution, dtype=float) / 2
        screen_points = -self.scale * space.updated_points + center
        visible = np.isfinite(screen_points).all(axis=1)
        edges = space.edges
        if len(edges):
            edge_points = screen_points[edges]
            edge_selected = selected[edges].all(axis=1)
            edge_visible = visible[edges].all(axis=1)
            for points, highlighted, valid in zip(edge_points, edge_selected, edge_visible):
                if valid:
                    color = self.colors[2 if highlighted else 1]
                    pygame.draw.aaline(self.surface, color, points[0], points[1])

        for point, highlighted, valid in zip(screen_points, selected, visible):
            if valid:
                pygame.draw.circle(self.surface, self.colors[2 if highlighted else 1], point, 2)

        # Show debug values
        try:
            utilities.debug(self.surface, self.app.window.font, (750, 10), self.colors[1], 
                            self.app.window.fps,
                            self.app.vrt_space.subobject_list[self.app.vrt_space.subobject_index])
        except IndexError:
            utilities.debug(self.surface, self.app.window.font, (750, 10), self.colors[1],
                            self.app.window.fps)

        self.app.window.app_window.blit(self.controls_label,
            (720 - self.controls_label.get_width() // 2, 575 - self.controls_label.get_height() // 2))

        if self.app.input.show_controls:
            self.app.window.app_window.fill(self.colors[0])
            utilities.debug(
                self.surface, self.app.window.font, (100, 100), self.colors[1],
                "<i>           importuje objekt + visualizer",
                "<w>           prepína objekty v danom type subobjektov v poradí akom boli zadané",
                "<s>           prepína objekty v danom type subobjektov v opačnom poradí",
                "<a>           prepína skupiny subobjektov v poradí akom boli zadané",
                "<d>           prepína skupiny subobjektov v opačnom poradí ",
                "<space>       pozastaví animácie",
                "<e>           posunie objekt do ďalšieho snímku (hodí sa pri pozastavenom objekte)",
                "<q>           posunie objekt do predchádzajúceho snímku",
                "<esc>         ukončí program",
                "<mwheel_up>   zväčší objekt na obrazovke",
                "<mwheel_down> zmenší objekt na obrazovke",
                "<m>           vloži do vybraneho súboru predlohu prázdneho vizualizéru",
                "<n>           vloži do vybraneho súboru predlohu prázdneho objektu"
            )