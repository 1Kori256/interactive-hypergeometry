import math
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

from scripts.matrix_utils import MatrixUtils
from scripts.virtual_space import VrtSpace

ROOT = Path(__file__).resolve().parents[1]
KEYS = ('pause', 'increment_subobject', 'decrement_subobject', 'increment_subobject_index',
        'decrement_subobject_index', 'rotate_positive', 'rotate_negative')


def make_space():
    app = SimpleNamespace(path=str(ROOT), config={}, renderer=SimpleNamespace(colors=None, scale=300))
    app.input = SimpleNamespace(keyboard_variables=dict.fromkeys(KEYS, False), loadup=0,
                                mouse_variables={'scroll_up': {'zoom': False}, 'scroll_down': {'zoom': False}})
    space = VrtSpace(app)
    return space


def legacy_rotation(dimensions, angle, axis1, axis2):
    matrix = np.eye(dimensions)
    matrix[axis1, axis1] = math.cos(angle)
    matrix[axis1, axis2] = -math.sin(angle)
    matrix[axis2, axis1] = math.sin(angle)
    matrix[axis2, axis2] = math.cos(angle)
    return matrix


def legacy_projection(point):
    point = point.copy()
    for dimension in range(len(point) - 1, 1, -1):
        matrix = np.zeros((dimension, dimension + 1))
        factor = 1.5 / (2 - point[-1])
        for axis in range(dimension):
            matrix[axis, axis] = factor
        point = matrix.dot(point)
    return point


class MatrixTests(unittest.TestCase):
    def test_batch_perspective_matches_original_pointwise_projection(self):
        rng = np.random.default_rng(42)
        for dimension in range(3, 7):
            with self.subTest(dimension=dimension):
                points = rng.uniform(-0.2, 0.2, (32, dimension))
                matrix = MatrixUtils(dimension)
                expected = np.array([legacy_projection(point) for point in points])
                np.testing.assert_allclose(matrix.perspective_projection(points), expected, atol=1e-12)
                np.testing.assert_allclose(matrix.perspective_projection(points[0]), expected[0], atol=1e-12)

    def test_rotation_preserves_distances_and_matches_original_signs(self):
        for dimension in range(3, 7):
            matrix = MatrixUtils(dimension).rotation(0.7, 0, dimension - 1)
            np.testing.assert_allclose(matrix, legacy_rotation(dimension, 0.7, 0, dimension - 1))
            np.testing.assert_allclose(matrix.T @ matrix, np.eye(dimension), atol=1e-12)

    def test_orthographic_batch_uses_the_same_two_axes(self):
        points = np.arange(24).reshape(4, 6)
        np.testing.assert_array_equal(MatrixUtils(6).orthographic_projection(points), points[:, :2])

    def test_singular_points_do_not_corrupt_other_points(self):
        result = MatrixUtils(3).perspective_projection([[1, 0, 2], [1, 0, 0]])
        self.assertTrue(np.isnan(result[0]).all())
        np.testing.assert_allclose(result[1], [0.75, 0])


class SpaceTests(unittest.TestCase):
    def test_all_presets_match_original_rotation_and_projection(self):
        for path in (ROOT / 'presets').glob('*.txt'):
            for projection in ('orthographic', 'perspective'):
                with self.subTest(preset=path.name, projection=projection):
                    space = make_space()
                    space.object_string = path.read_text().splitlines(True)
                    space.create_object()
                    space.angles = [0.3 + index * 0.07 for index in range(len(space.rotations))]
                    space.projection_type = projection
                    expected = space.points.copy()
                    for angle, rotation in zip(space.angles, space.rotations):
                        matrix = legacy_rotation(space.dimensions, angle, rotation[0], rotation[1])
                        expected = np.array([matrix.dot(point) for point in expected])
                    expected = (expected[:, :2] if projection == 'orthographic'
                                else np.array([legacy_projection(point) for point in expected]))
                    space.update()
                    np.testing.assert_allclose(space.updated_points, expected, rtol=1e-10, atol=1e-10)

    def test_pause_and_frame_stepping_keep_existing_increments(self):
        space = make_space()
        space.angles = [0.2, 0.4]
        original = np.array(space.angles)
        space.app.input.keyboard_variables['pause'] = True
        space.update()
        np.testing.assert_allclose(space.angles, original)
        space.app.input.keyboard_variables['rotate_positive'] = True
        space.update()
        np.testing.assert_allclose(space.angles, original + space.angle_increments)
        space.app.input.keyboard_variables['rotate_positive'] = False
        space.app.input.keyboard_variables['rotate_negative'] = True
        space.update()
        np.testing.assert_allclose(space.angles, original)

    def test_zoom_and_subobject_navigation_keep_existing_behavior(self):
        space = make_space()
        space.object_string = (ROOT / 'presets/4dcube.txt').read_text().splitlines(True)
        space.create_object()
        keys = space.app.input.keyboard_variables
        keys['increment_subobject'] = True
        space.update()
        self.assertEqual(space.current_subobject, 1)
        keys['increment_subobject'] = False
        keys['increment_subobject_index'] = True
        space.update()
        self.assertEqual(space.subobject_index, 1)
        self.assertEqual(space.current_subobject, 0)
        space.app.input.mouse_variables['scroll_up']['zoom'] = True
        space.update()
        self.assertAlmostEqual(space.app.renderer.scale, 315)

    def test_optional_edges_do_not_reuse_the_previous_objects_edges(self):
        space = make_space()
        self.assertGreater(len(space.edges), 0)
        space.object_string = 'dimensions:\n3\npoints:\n2\n0 0 0\n1 0 0\n'.splitlines(True)
        space.create_object()
        space.update()
        self.assertEqual(space.edges.shape, (0, 2))
        self.assertEqual(space.subobjects, [])


if __name__ == '__main__':
    unittest.main()
