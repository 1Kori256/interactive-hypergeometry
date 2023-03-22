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
        
    def render(self) -> None:
        
        """Renders everything"""
        
        self.app.window.app_window.fill(self.colors[0])
        self.surface = self.app.window.app_window
        
        try:
            for edge in self.app.vrt_space.edges:
                if (edge[0] not in self.app.vrt_space.subobjects[self.app.vrt_space.current_subobject]) or (edge[1] not in self.app.vrt_space.subobjects[self.app.vrt_space.current_subobject]):
                    pygame.draw.line(self.app.window.app_window, self.colors[1], -self.scale * np.array(self.app.vrt_space.updated_points[edge[0]]) + [400, 300],
                                                                                  -self.scale * np.array(self.app.vrt_space.updated_points[edge[1]]) + [400, 300])
                else:
                    pygame.draw.line(self.app.window.app_window, self.colors[2], -self.scale * np.array(self.app.vrt_space.updated_points[edge[0]]) + [400, 300],
                                                                              -self.scale * np.array(self.app.vrt_space.updated_points[edge[1]]) + [400, 300])
        except IndexError:
            try:
                for edge in self.app.vrt_space.edges:
                    pygame.draw.line(self.app.window.app_window, self.colors[1], -self.scale * np.array(self.app.vrt_space.updated_points[edge[0]]) + [400, 300],
                                                                                  -self.scale * np.array(self.app.vrt_space.updated_points[edge[1]]) + [400, 300])
            except: # Edges are optional
                pass


        for index, point in enumerate(self.app.vrt_space.updated_points):
            try:
                if index not in self.app.vrt_space.subobjects[self.app.vrt_space.current_subobject]:
                    pygame.draw.circle(self.app.window.app_window, self.colors[1], -self.scale * point + [400, 300], 2)
                else:
                    pygame.draw.circle(self.app.window.app_window, self.colors[2], -self.scale * point + [400, 300], 2) 
            except IndexError: # Subobjects are optional
                pygame.draw.circle(self.app.window.app_window, self.colors[1], -self.scale * point + [400, 300], 2)
                
        # Show debug values
        try:
            utilities.debug(self.surface, self.app.window.font, (750, 10), self.colors[1], 
                            self.app.window.fps,
                            self.app.vrt_space.subobject_list[self.app.vrt_space.subobject_index])
        except IndexError:
            utilities.debug(self.surface, self.app.window.font, (750, 10), self.colors[1],
                            self.app.window.fps)

        text_object = self.app.window.mid_font.render("Controls", True, (240,240,240))
        self.app.window.app_window.blit(text_object, (720 - text_object.get_width() // 2, 575 - text_object.get_height() // 2))

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