"""
File that contains non-trivial matrix operations.
For example projections and rotations.
"""


import numpy as np


class MatrixUtils():
    def __init__(self, dimensions) -> None:
        self.dimensions = dimensions
        self.distance = 2

    def perspective_projection(self, point) -> np.array:
        projected_point = point
        for i in range(self.dimensions - 1, 1, -1):
            self.projection_matrix = np.zeros([i, i + 1])
            factor = 1.5 / (self.distance - projected_point[-1])
            for j in range(i):
                self.projection_matrix[j, j] = factor
            projected_point = self.projection_matrix.dot(projected_point)
        return projected_point

    def orthographic_projection(self, point) -> np.array:
        projected_point = point[:2]
        return projected_point
    
    def rotation(self, angle, axis1, axis2) -> np.matrix:
        self.rotation_matrix = np.identity(self.dimensions)
        self.rotation_matrix[axis1, axis1] = np.cos(angle)
        self.rotation_matrix[axis1, axis2] = -1 * np.sin(angle)
        self.rotation_matrix[axis2, axis1] = np.sin(angle)
        self.rotation_matrix[axis2, axis2] = np.cos(angle)
        return self.rotation_matrix