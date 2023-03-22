"""
Virtual space object
"""

import numpy as np
import scripts.preset as presets
import scripts.matrix_utils as matrix_utils


class VrtSpace:
    def __init__(self, app) -> None:
        
        """Initialize Virtual space object.
        
        Keyword arguments:
        app - Main application class
        """
        
        self.app = app
        self.config = app.config
        
        self.presets = presets.Presets(2)
        self.matrix_utils = matrix_utils.MatrixUtils(2)

        self.object_string = "" 

        with open(f"{self.app.path}/presets/3dcube.txt") as file:
            self.object_string = file.readlines()

        self.create_object()


    def create_object(self) -> None:

        """Funtion that is used to load object from file."""

        self.number_of_points = 0
        start_points_index = -1 

        self.number_of_edges = 0
        start_edges_index = -1

        self.subobject_manager = {}
        current_subobject_start_index = -1
        current_subobject_size = 0
        self.subobject_list = []

        for i, line in enumerate(self.object_string):
            if line[:10] == "dimensions":
                self.dimensions = int(self.object_string[i + 1])

            elif line[:6] == "points":
                self.number_of_points = int(self.object_string[i + 1])
                start_points_index = i + 2
                self.points = np.empty([self.number_of_points, self.dimensions])
            
            elif start_points_index <= i < start_points_index + self.number_of_points:
                self.points[i - start_points_index] = list(map(float, line.strip().split()))

            elif line[:5] == "edges":
                self.number_of_edges = int(self.object_string[i + 1])
                start_edges_index = i + 2
                self.edges = []
            
            elif start_edges_index <= i < start_edges_index + self.number_of_edges:
                self.edges.append(list(map(int, line.strip().split())))

            elif line[:10] == "subobject_":
                pass

            elif line[:9] == "subobject":
                self.subobject_manager[line.strip().split()[1][:-1]] = []
                current_subobject = line.strip().split()[1][:-1]
                self.subobject_list.append(current_subobject)
                current_subobject_size = int(self.object_string[i + 1])
                current_subobject_start_index = i + 2

            elif current_subobject_start_index <= i < current_subobject_start_index + current_subobject_size:
                self.subobject_manager[current_subobject].append(list(map(int, line.strip().split())))

        try:
            self.subobject_index = 0
            self.current_subobject = 0
            self.subobjects = self.subobject_manager[self.subobject_list[self.subobject_index]]
        except IndexError:  # Handle objects without subobject_manager
            self.subobjects = []

        self.presets.dimensions = self.dimensions
        self.matrix_utils.dimensions = self.dimensions

        self.load_visualisator(f"{self.app.path}/visualisators/default_visualisator.txt")


    def load_visualisator(self, file) -> None:

        """Funtion that is used to load visualisators from file."""

        with open(file) as f:
            visualisator_string = f.readlines()

        self.number_of_offsets = 0
        start_offsets_index = -1

        self.number_of_rotations = 0
        start_rotations_index = -1
        
        self.offsets = []
        self.rotations = []
        self.angle_increments = []
        self.angles = []

        for i, line in enumerate(visualisator_string):
            if line[:15] == "projection_type":
                self.projection_type = visualisator_string[i + 1].strip()
            
            elif line[:7] == "offsets":
                self.number_of_offsets = int(visualisator_string[i + 1])
                start_offsets_index = i + 2

            elif start_offsets_index <= i < start_offsets_index + self.number_of_offsets:
                self.offsets.append(list(map(float, line.split())))
                self.offsets[i - start_offsets_index][0] = int(self.offsets[i - start_offsets_index][0])
                self.offsets[i - start_offsets_index][1] = int(self.offsets[i - start_offsets_index][1])

            elif line[:9] == "rotations":
                self.number_of_rotations = int(visualisator_string[i + 1])
                start_rotations_index = i + 2

            elif start_rotations_index <= i < start_rotations_index + self.number_of_rotations:
                self.rotations.append(list(map(float, line.split())))
                self.rotations[i - start_rotations_index][0] = int(self.rotations[i - start_rotations_index][0])
                self.rotations[i - start_rotations_index][1] = int(self.rotations[i - start_rotations_index][1])
                self.angle_increments.append(self.rotations[i - start_rotations_index][2])
                self.angles.append(0)

            elif line[:6] == "colors":
                self.colors = []
                for j in range(i + 1, i + 4):
                    self.colors.append(list(map(int, visualisator_string[j].split())))

                self.app.renderer.colors = self.colors

        self.rotated_points = np.empty([len(self.points), self.dimensions])
        for i in range(len(self.points)):
            self.rotated_points[i] = self.points[i]
        for offset in self.offsets:
            rotation_matrix = self.matrix_utils.rotation(offset[2], offset[0], offset[1])
            for i in range(len(self.points)):
                self.rotated_points[i] = rotation_matrix.dot(self.rotated_points[i])
        for i in range(len(self.points)):
            self.points[i] = self.rotated_points[i]

        self.app.input.keyboard_variables["pause"] = True
        self.app.input.loadup = 1


    def update(self) -> None:
        
        """Update in-app stuff"""

        if len(self.subobjects) > 0:
            if self.app.input.keyboard_variables["increment_subobject"]:
                self.current_subobject = (self.current_subobject + 1) % len(self.subobjects)

            if self.app.input.keyboard_variables["decrement_subobject"]:
                self.current_subobject = (self.current_subobject - 1) % len(self.subobjects)

            if self.app.input.keyboard_variables["increment_subobject_index"]:
                self.subobject_index = (self.subobject_index + 1) % len(self.subobject_list)
                self.subobjects = self.subobject_manager[self.subobject_list[self.subobject_index]]
                self.current_subobject = 0

            if self.app.input.keyboard_variables["decrement_subobject_index"]:
                self.subobject_index = (self.subobject_index - 1) % len(self.subobject_list)
                self.subobjects = self.subobject_manager[self.subobject_list[self.subobject_index]]
                self.current_subobject = 0


        self.rotated_points = np.empty([len(self.points), self.dimensions])
        for i in range(len(self.points)):
            self.rotated_points[i] = self.points[i]

        for i, rotation in enumerate(self.rotations):
            rotation_matrix = self.matrix_utils.rotation(self.angles[i], rotation[0], rotation[1])
            for point_index in range(len(self.points)):
                self.rotated_points[point_index] = rotation_matrix.dot(self.rotated_points[point_index])
                

        self.updated_points = np.empty([len(self.points), 2])
        if self.projection_type == "orthographic":
            for i in range(len(self.points)):
                self.updated_points[i] = self.matrix_utils.orthographic_projection(self.rotated_points[i])
        elif self.projection_type == "perspective":
            for i in range(len(self.points)):
                self.updated_points[i] = self.matrix_utils.perspective_projection(self.rotated_points[i])

        if not self.app.input.keyboard_variables["pause"]:
            for i, angle in enumerate(self.angles):
                self.angles[i] = angle + self.angle_increments[i]

        if self.app.input.keyboard_variables["rotate_positive"]:
            for i, angle in enumerate(self.angles):
                self.angles[i] = angle + self.angle_increments[i]
        
        if self.app.input.keyboard_variables["rotate_negative"]:
            for i, angle in enumerate(self.angles):
                self.angles[i] = angle - self.angle_increments[i]

        if self.app.input.mouse_variables["scroll_up"]["zoom"]:
            self.app.renderer.scale *= 1.05

        if self.app.input.mouse_variables["scroll_down"]["zoom"]:
            self.app.renderer.scale *= 0.95