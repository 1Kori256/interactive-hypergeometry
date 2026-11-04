import os
from pathlib import Path
import unittest
from unittest.mock import patch

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import numpy as np
import pygame

from main import App

ROOT = Path(__file__).resolve().parents[1]


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = App(['main.py', str(ROOT / 'presets/4dcube.txt'),
                        str(ROOT / 'visualisators/4d_orthographic.txt')])
        self.app.input.update()
        self.app.input.loadup = 0
        pygame.event.clear()

    def tearDown(self):
        pygame.quit()

    def key(self, key, event_type=pygame.KEYDOWN):
        pygame.event.post(pygame.event.Event(event_type, key=key))
        self.app.input.update()

    def test_command_line_load_and_render_preserve_original_palette(self):
        self.app.vrt_space.update()
        self.app.renderer.render()
        self.assertEqual(self.app.vrt_space.dimensions, 4)
        self.assertEqual(self.app.renderer.colors, [[20, 20, 20], [255, 255, 255], [255, 0, 0]])
        self.assertEqual(self.app.window.app_window.get_size(), (800, 600))

    def test_only_the_matching_key_changes_pause(self):
        self.assertTrue(self.app.input.keyboard_variables['pause'])
        self.key(pygame.K_w)
        self.assertTrue(self.app.input.keyboard_variables['pause'])
        self.key(pygame.K_SPACE)
        self.assertFalse(self.app.input.keyboard_variables['pause'])
        self.key(pygame.K_SPACE, pygame.KEYUP)
        self.assertFalse(self.app.input.keyboard_variables['pause'])

    def test_held_step_stops_on_key_release(self):
        self.key(pygame.K_e)
        self.assertTrue(self.app.input.keyboard_variables['rotate_positive'])
        self.key(pygame.K_e, pygame.KEYUP)
        self.assertFalse(self.app.input.keyboard_variables['rotate_positive'])

    def test_modern_and_legacy_scroll_events_do_not_double_zoom(self):
        pygame.event.post(pygame.event.Event(pygame.MOUSEWHEEL, y=1, x=0))
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=4))
        self.app.input.update()
        self.app.vrt_space.update()
        self.assertAlmostEqual(self.app.renderer.scale, 315)

    def test_cancelled_file_picker_retains_the_current_object(self):
        self.app.input.override = False
        self.app.input.keyboard_variables['import_object'] = True
        original = self.app.vrt_space.points.copy()
        with patch('scripts.input.select_file', return_value=''):
            self.app.input.update()
        np.testing.assert_array_equal(self.app.vrt_space.points, original)
        self.assertFalse(self.app.input.keyboard_variables['import_object'])

    def test_no_argument_startup_initializes_picker_flag(self):
        app = App(['main.py'])
        self.assertFalse(app.input.override)
        with patch('scripts.input.select_file', return_value=''):
            app.update()

    def test_mouse_coordinates_follow_both_scale_axes(self):
        self.app.window.scaled_resolution = [1600, 600]
        with patch('pygame.mouse.get_pos', return_value=(800, 300)):
            self.app.input.update()
        self.assertEqual(self.app.input.mouse_pos, (400, 300))

    def test_help_overlay_and_projection_singularity_render(self):
        self.app.vrt_space.update()
        self.app.vrt_space.updated_points[0] = np.nan
        self.app.renderer.render()
        self.app.input.show_controls = True
        self.app.renderer.render()

    def test_equal_size_window_skips_scaling_and_other_sizes_still_work(self):
        self.app.vrt_space.update()
        self.app.renderer.render()
        with patch('pygame.transform.scale', wraps=pygame.transform.scale) as scale:
            self.app.window.render_screen()
            scale.assert_not_called()
            self.app.window.scaled_resolution = [1000, 500]
            self.app.window.window = pygame.display.set_mode((1000, 500))
            self.app.window.render_screen()
            self.assertEqual(scale.call_count, 1)


if __name__ == '__main__':
    unittest.main()
