"""Measure update/drawing time without a window or the 60 FPS display cap."""

import argparse
import json
import os
from pathlib import Path
import statistics
import sys
import time

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from main import App


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frames', type=int, default=240)
    parser.add_argument('--preview', type=Path, help='Also save a 4D cube preview')
    args = parser.parse_args()
    if args.frames < 1:
        parser.error('--frames must be positive')
    app = App(['main.py', str(ROOT / 'presets/4dcube.txt'),
               str(ROOT / 'visualisators/4d_orthographic.txt')])
    app.input.update()
    app.input.loadup = 0
    results = {}

    def load(preset, visualisator):
        app.vrt_space.object_string = (ROOT / 'presets' / preset).read_text().splitlines(True)
        app.vrt_space.create_object()
        app.vrt_space.load_visualisator(ROOT / 'visualisators' / visualisator)

    try:
        for preset, visualisator in [('4dcube.txt', '4d_orthographic.txt'),
                                     ('hexacosichoron.txt', '4d_perspective.txt'),
                                     ('6dcube.txt', '6d_default.txt')]:
            load(preset, visualisator)
            app.input.keyboard_variables['pause'] = False
            samples = []
            for index in range(args.frames + 20):
                start = time.perf_counter()
                app.vrt_space.update()
                app.renderer.render()
                elapsed = (time.perf_counter() - start) * 1000
                if index >= 20:
                    samples.append(elapsed)
            results[preset] = {'median_ms': round(statistics.median(samples), 3),
                               'points': len(app.vrt_space.points), 'edges': len(app.vrt_space.edges)}
        if args.preview:
            load('4dcube.txt', '4d_orthographic.txt')
            app.vrt_space.angles = [0.9, 0.4]
            app.input.keyboard_variables['pause'] = True
            app.vrt_space.update()
            app.renderer.render()
            args.preview.parent.mkdir(parents=True, exist_ok=True)
            pygame.image.save(app.window.app_window, str(args.preview))
    finally:
        pygame.quit()
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
