"""
Handle user input
"""

import pygame, sys
from pygame.locals import *
from tkinter import Tk 
from tkinter.filedialog import askopenfilename


class Input:
    def __init__(self, app, parameters) -> None:
        
        """Initialize Input object.
        
        Keyword arguments:
        app - Main application class
        """
        
        self.app = app
        self.config = app.config
        self.implement = "main_screen" # Only inputs allowed in here
        
        # Create dictionary for all buttons
        self.keyboard_variables, self.mouse_variables = {}, {}
        for bind, bind_data in self.config["input"].items():
            if bind_data["device"] == "keyboard":
                self.keyboard_variables[bind] = False
            elif bind_data["device"] == "mouse":
                self.mouse_variables[bind] = False
        
        
        self.reset_scroll("scroll_up", "scroll_down")
        
        self.mouse_pos = [0, 0]
        self.previous_mouse_pos = [0, 0]

        self.parameters = parameters
        if len(parameters) == 3:
            self.override = True
        
        self.keyboard_variables["import_object"] = True

        # Pause on loadup
        self.keyboard_variables["pause"] = True
        self.loadup = 1

        self.show_controls = False

        
    def reset_scroll(self, *scroll_bind) -> None:
        
        """Reset scroll buttons
        
        Keyword arguments:
        *scroll_bind: all scrolls that are to be reseted
        """
        
        for scroll in scroll_bind:
            self.mouse_variables[scroll] = {"zoom": False}
       

    def update(self) -> None:
        
        """Update user input"""
        
        # Transform mouse position
        mouse_pos = pygame.mouse.get_pos()
        self.previous_mouse_pos = self.mouse_pos
        self.mouse_pos = (int(mouse_pos[0] * (self.app.window.base_resolution[0] / self.app.window.scaled_resolution[0])),
                          int(mouse_pos[1] * (self.app.window.base_resolution[0] / self.app.window.scaled_resolution[0])))

        if self.keyboard_variables["import_object"]:

            if not self.override:
                self.app.window.app_window.fill(self.app.renderer.colors[0])
                text_object = self.app.window.large_font.render("Pick object", True, (240,240,240))
                self.app.window.app_window.blit(text_object, (400 - text_object.get_width() // 2, 300 - text_object.get_height() // 2))
                self.app.window.window.blit(pygame.transform.scale(self.app.window.app_window, self.app.window.scaled_resolution), (0, 0))
                pygame.display.update()

                Tk().withdraw() 
                self.current_file = askopenfilename(title="Pick object")

                with open(f"{self.current_file}") as file:
                    self.app.vrt_space.object_string = file.readlines()
                self.app.vrt_space.create_object()

                self.app.window.app_window.fill(self.app.renderer.colors[0])
                text_object = self.app.window.large_font.render("Pick visualisator", True, (240,240,240))
                self.app.window.app_window.blit(text_object, (400 - text_object.get_width() // 2, 300 - text_object.get_height() // 2))
                self.app.window.window.blit(pygame.transform.scale(self.app.window.app_window, self.app.window.scaled_resolution), (0, 0))
                pygame.display.update()

                Tk().withdraw() 
                self.current_file = askopenfilename(title="Pick visualisator")
                self.app.vrt_space.load_visualisator(self.current_file)
            
            else:
                with open(self.parameters[1]) as file:
                    self.app.vrt_space.object_string = file.readlines()
                self.app.vrt_space.create_object()

                self.app.vrt_space.load_visualisator(self.parameters[2])


        if self.keyboard_variables["write_blank_preset"]:
            Tk().withdraw() 
            self.current_file = askopenfilename()

            with open(f"{self.current_file}", "w") as file:
                file.write("dimensions:\n<num>\n\npoints:\n<num>\n\nedges:(optional)\n<num>\n\nsubobject_manager:(optional)\nsubobject <name>:\n<num>")

        if self.keyboard_variables["write_blank_visualiser"]:
            Tk().withdraw() 
            self.current_file = askopenfilename()

            with open(f"{self.current_file}", "w") as file:
                file.write("projection_type:\n<perspective/ortographic>\n\noffsets:(optional)\n<num>\n\nrotations:(optional)\n<num>\n\ncolors:(optional)\n<background_color>\n<object_color>\n<subobject_color>")        


        # Reset inputs that are triggered by press not by holding + scrolls
        self.reset_scroll("scroll_up", "scroll_down")
        for bind, bind_data in self.config["input"].items():
            if bind_data["device"] == "keyboard":
                if bind_data["trigger"] == "press":
                    self.keyboard_variables[bind] = False
            elif bind_data["device"] == "mouse":
                if bind_data["trigger"] == "press":
                    self.mouse_variables[bind] = False
                    
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # Update input dictionaries
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                keys = pygame.key.get_pressed()
                keys_to_disable = []

                for bind, data in self.config["input"].items():
                    if self.implement in data["implement"]:
                        if data["device"] == "keyboard":
                            if keys[data["binding"]] == 1:
                                if data["trigger"] == "hold":
                                    self.keyboard_variables[str(bind)] = True
                                elif data["trigger"] == "press":
                                    self.keyboard_variables[str(bind)] = True
                                    keys_to_disable.append(str(bind))
                                elif data["trigger"] == "toggle":
                                    if event.type == pygame.KEYDOWN:
                                        if self.keyboard_variables[str(bind)]:
                                            self.keyboard_variables[str(bind)] = False
                                        else:
                                            self.keyboard_variables[str(bind)] = True
                            else:
                                if data["trigger"] == "hold":
                                    self.keyboard_variables[str(bind)] = False
                                
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
                button = event.button
                button_status = (event.type == pygame.MOUSEBUTTONDOWN)

                for bind, data in self.config["input"].items():
                    if self.implement in data["implement"]:
                        if data["device"] == "mouse":
                            if data["button"] == button:
                                if button not in [4, 5]:
                                    self.mouse_variables[str(bind)] = button_status
                                else:
                                    self.mouse_variables[str(bind)]["zoom"] = True

        if self.mouse_pos[0] > 640 and self.mouse_pos[1] > 550:
            self.show_controls = True
        else:
            self.show_controls = False

        # Quit application
        if self.keyboard_variables["exit"]:
            pygame.quit()
            sys.exit()
        
        if self.keyboard_variables["pause"] and self.loadup:
            self.loadup = (self.loadup + 1) % 10 
            if self.loadup == 0:
                self.keyboard_variables["pause"] = False