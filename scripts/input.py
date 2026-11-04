"""
Handle user input
"""

import pygame, sys
from pygame.locals import *


def select_file(title="Select file"):
    # Tk is only needed for dialogs; command-line presets also work without it.
    try:
        from tkinter import Tk
        from tkinter.filedialog import askopenfilename
    except ImportError:
        print("File dialogs need Tk. You can pass a preset and visualisator to main.py instead.", file=sys.stderr)
        return ""
    root = Tk()
    root.withdraw()
    try:
        return askopenfilename(parent=root, title=title)
    finally:
        root.destroy()


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
        self.override = len(parameters) == 3
        
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
                          int(mouse_pos[1] * (self.app.window.base_resolution[1] / self.app.window.scaled_resolution[1])))

        if self.keyboard_variables["import_object"]:

            if not self.override:
                self.app.window.app_window.fill(self.app.renderer.colors[0])
                text_object = self.app.window.large_font.render("Pick object", True, (240,240,240))
                self.app.window.app_window.blit(text_object, (400 - text_object.get_width() // 2, 300 - text_object.get_height() // 2))
                self.app.window.window.blit(pygame.transform.scale(self.app.window.app_window, self.app.window.scaled_resolution), (0, 0))
                pygame.display.update()

                self.current_file = select_file("Pick object")
                if not self.current_file:
                    self.keyboard_variables["import_object"] = False
                    return

                with open(f"{self.current_file}") as file:
                    self.app.vrt_space.object_string = file.readlines()
                self.app.vrt_space.create_object()

                self.app.window.app_window.fill(self.app.renderer.colors[0])
                text_object = self.app.window.large_font.render("Pick visualisator", True, (240,240,240))
                self.app.window.app_window.blit(text_object, (400 - text_object.get_width() // 2, 300 - text_object.get_height() // 2))
                self.app.window.window.blit(pygame.transform.scale(self.app.window.app_window, self.app.window.scaled_resolution), (0, 0))
                pygame.display.update()

                self.current_file = select_file("Pick visualisator")
                if self.current_file:
                    self.app.vrt_space.load_visualisator(self.current_file)
            
            else:
                with open(self.parameters[1]) as file:
                    self.app.vrt_space.object_string = file.readlines()
                self.app.vrt_space.create_object()

                self.app.vrt_space.load_visualisator(self.parameters[2])


        if self.keyboard_variables["write_blank_preset"]:
            self.current_file = select_file()
            if self.current_file:
                with open(f"{self.current_file}", "w") as file:
                    file.write("dimensions:\n<num>\n\npoints:\n<num>\n\nedges:(optional)\n<num>\n\nsubobject_manager:(optional)\nsubobject <name>:\n<num>")

        if self.keyboard_variables["write_blank_visualiser"]:
            self.current_file = select_file()
            if self.current_file:
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
                    
        events = pygame.event.get()
        has_wheel_event = any(event.type == pygame.MOUSEWHEEL for event in events)
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # Only the key carried by this event may toggle or trigger a binding.
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                for bind, data in self.config["input"].items():
                    if (self.implement in data["implement"] and data["device"] == "keyboard"
                            and event.key == data["binding"]):
                        if data["trigger"] == "hold":
                            self.keyboard_variables[bind] = event.type == pygame.KEYDOWN
                        elif event.type == pygame.KEYDOWN and not getattr(event, "repeat", False):
                            if data["trigger"] == "toggle":
                                self.keyboard_variables[bind] = not self.keyboard_variables[bind]
                            else:
                                self.keyboard_variables[bind] = True

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self.mouse_variables["scroll_up"]["zoom"] = True
                elif event.y < 0:
                    self.mouse_variables["scroll_down"]["zoom"] = True

            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
                button = event.button
                if button in (4, 5) and has_wheel_event:
                    continue
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