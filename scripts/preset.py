import numpy as np
from itertools import combinations, combinations_with_replacement


class Presets():
    def __init__(self, dimensions) -> None:
        self.dimensions = dimensions

    def distance_between_two_points(self, point1, point2) -> float:
        ans = 0
        for i, j in zip(point1, point2):
            ans += pow(j - i, 2)
        return np.sqrt(ans) 

    def generate_cube(self) -> np.matrix:
        return ((np.arange(2**self.dimensions)[:,None] & (1 << np.arange(self.dimensions))) > 0) - 1/2

    def find_edge_paris(self, hypercube, dist) -> list:
        edge_pairs = []
        for i in range(len(hypercube)):
            for j in range(i + 1, len(hypercube)):
                if dist - 1e-6 <= self.distance_between_two_points(hypercube[i], hypercube[j]) <= dist + 1e-6:
                    edge_pairs.append([i, j])
        return edge_pairs

    def fibonacci_sphere(self, samples):
        points = []
        offset = 2./samples
        increment = np.pi * (3. - np.sqrt(5.));

        for i in range(samples):
            y = ((i * offset) - 1) + (offset / 2);
            r = np.sqrt(1 - pow(y,2))

            phi = ((i) % samples) * increment

            x = np.cos(phi) * r
            z = np.sin(phi) * r

            points.append([x,y,z])

        return points

    def create_subobjects(self, points, subobject_dimension) -> list:
        subobjects = []

        for comb in combinations(range(self.dimensions), self.dimensions - subobject_dimension):
            for comb2 in combinations_with_replacement([-.5, .5], len(comb)):
                final_points = []
                for index, point in enumerate(points):
                    valid = True
                    for i, value in enumerate(comb):
                        if point[value] != comb2[i]:
                            valid = False
                    if valid:
                        final_points.append(index)
                subobjects.append(final_points)

        return subobjects

    def print_preset_file(self, dim, points, edges, subobject_manager={}):
        print("dimensions:")
        print(dim)
        print()
        print("points:")
        print(len(points))
        print(*[" ".join(map(str, i)) for i in points], sep="\n")
        print()
        print("edges:")
        print(len(edges))
        print(*[" ".join(map(str, i)) for i in edges], sep="\n")
        print("subobject_manager:")
        for key, item in subobject_manager.items():
            print(f"subobject {key}:")
            print(len(item))
            print(*[" ".join(map(str, i)) for i in item], sep="\n")
            print()