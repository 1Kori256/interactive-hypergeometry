"""Rotations and projections for individual points or batches of points."""

import numpy as np


class MatrixUtils:
    def __init__(self, dimensions) -> None:
        self.dimensions = dimensions
        self.distance = 2

    def perspective_projection(self, point) -> np.ndarray:
        projected = np.asarray(point, dtype=float)
        for _ in range(self.dimensions - 1, 1, -1):
            denominator = self.distance - projected[..., -1:]
            factor = np.divide(1.5, denominator,
                               out=np.full_like(denominator, np.nan),
                               where=np.abs(denominator) > 1e-12)
            projected = projected[..., :-1] * factor
        return projected

    def orthographic_projection(self, point) -> np.ndarray:
        return np.asarray(point)[..., :2]

    def rotation(self, angle, axis1, axis2) -> np.ndarray:
        self.rotation_matrix = np.identity(self.dimensions)
        cosine, sine = np.cos(angle), np.sin(angle)
        self.rotation_matrix[axis1, axis1] = cosine
        self.rotation_matrix[axis1, axis2] = -sine
        self.rotation_matrix[axis2, axis1] = sine
        self.rotation_matrix[axis2, axis2] = cosine
        return self.rotation_matrix