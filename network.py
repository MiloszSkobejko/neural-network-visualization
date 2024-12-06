from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.arrays import vbo
import random
import math
import numpy as np

from selection import Selection


class Neuron:
    def __init__(self, idx, x, y, color):
        self.index = idx
        self.x = x
        self.y = y
        self.color = color
        self.selected = False

    def on_screen(self, viewport):
        """Checks if neuron is visible on screen"""
        x_min, y_min, x_max, y_max = viewport
        return x_min <= self.x <= x_max and y_min <= self.y <= y_max

    def draw(self):
        """Draws neuron as a circle with random color"""
        glColor3f(*self.color)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(self.x, self.y)

        radius = 5
        segments = 20

        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            glVertex2f(self.x + radius * math.cos(angle), self.y + radius * math.sin(angle))
        glEnd()

class Edge:
    def __init__(self, idx, n_start, n_end, color, weight):
        self.index = idx
        self.start = n_start
        self.end = n_end
        self.weight = weight
        self.color = color
        self.selected = False

class NetworkGL_Render(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = []
        self.neurons = []
        self.connections = []
        self.scale_factor = 1.0

        self.spacing_x = 300  # Distance between layers
        self.spacing_y = 50   # Distance between neurons
        self.start_x = 50     # x draw starting value
        self.start_y = 150    # y draw starting value

        self.last_mouse_position = QPoint()
        self.offset_x = 0
        self.offset_y = 0
        self.selection = Selection(self)

        self.vbos = []  # List of VBOs for rendering connections

    def random_color_weight(self):
        r = random.random()
        g = random.random()
        b = random.random()
        opacity = 0.3
        return [r,g,b,opacity]

    def random_color(self):
        return [random.random(), random.random(), random.random()]

    def set_network(self, layers):
        """Creates neurons and populates VBOs for connections based on the network structure."""
        self.layers = layers
        self.neurons = []
        self.connections = []
        self.vbo_layer = []
        self.vbos = []

        # Creating neurons
        for layer_idx, neuron_count in enumerate(self.layers):
            layer_x = self.start_x + layer_idx * self.spacing_x
            layer_neurons = []

            for neuron_idx in range(neuron_count):
                neuron_y = self.start_y + neuron_idx * self.spacing_y
                neuron_color = self.random_color()

                neuron = Neuron([layer_idx, neuron_idx], layer_x, neuron_y, neuron_color)
                layer_neurons.append(neuron)
            self.neurons.append(layer_neurons)

        # Creating connections
        for layer_idx, _ in enumerate(self.layers[:-1]):  # Stop at second-to-last layer
            layer_connections = []
            for start_idx, neuron_start in enumerate(self.neurons[layer_idx]):  # Current layer neurons
                neuron_connections = []
                vertices = []
                colors = []

                for end_idx, neuron_end in enumerate(self.neurons[layer_idx + 1]):  # Next layer neurons
                    # Create a new Edge object with initial color and opacity

                    # This approach works, but when handling opacity it's maybe better to 
                    # reduce opacity for out of threshold connections to 0. See if it reduces 
                    # the lag that's created by setting network again.
                    
                    # weight = random.random() * 10
                    # if weight > 5:
                    connection_color = self.random_color_weight()

                    edge = Edge([layer_idx, start_idx, end_idx], neuron_start, neuron_end, connection_color, 10.0)
                    neuron_connections.append(edge)

                    vertices.extend([edge.start.x, edge.start.y, edge.end.x, edge.end.y])
                    colors.extend(edge.color * 2)
                    

                # Store all connection coming out from neuron
                layer_connections.append(neuron_connections)

                # Create VBOs for all lines originating from this neuron
                if vertices:
                    vertex_array = np.array(vertices, dtype=np.float32)
                    color_array = np.array(colors, dtype=np.float32)

                    vbo_vertices = vbo.VBO(vertex_array)
                    vbo_colors = vbo.VBO(color_array)
                    self.vbos.append((vbo_vertices, vbo_colors))
            #self.vbos.append(self.vbo_layer)
            self.connections.append(layer_connections)

    def paintGL(self):
        """Render the network using OpenGL."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(self.offset_x, self.offset_y, 0)
        glScalef(self.scale_factor, self.scale_factor, 1.0)

        # Rendering edges using VBOs
        for vbo_vertices, vbo_colors in self.vbos:
            vbo_vertices.bind()
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(2, GL_FLOAT, 0, vbo_vertices)

            vbo_colors.bind()
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(4, GL_FLOAT, 0, vbo_colors)

            glDrawArrays(GL_LINES, 0, len(vbo_vertices) // 2)

            vbo_vertices.unbind()
            vbo_colors.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_COLOR_ARRAY)

        # Rendering neurons
        for layer in self.neurons:
            for neuron in layer:
                if neuron.on_screen(self.viewport()):
                    neuron.draw()

        # Draw selection rectangle
        if self.selection.is_selecting and self.selection.selection_start and self.selection.selection_end:
            x1, y1 = self.selection.selection_start
            x2, y2 = self.selection.selection_end
            glColor4f(0.2, 0.5, 1.0, 0.3)  # Semi-transparent blue
            glBegin(GL_QUADS)
            glVertex2f(x1, y1)
            glVertex2f(x2, y1)
            glVertex2f(x2, y2)
            glVertex2f(x1, y2)
            glEnd()

    def viewport(self):
        """Returns the visible area of the viewport for optimization."""
        w, h = self.width(), self.height()
        x_min = -self.offset_x / self.scale_factor
        x_max = (w - self.offset_x) / self.scale_factor
        y_min = -self.offset_y / self.scale_factor
        y_max = (h - self.offset_y) / self.scale_factor
        return (x_min, y_min, x_max, y_max)

    def resizeGL(self, w, h):
        """Resizing OpenGL viewport to the size of window."""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def initializeGL(self):
        """Initialization of OpenGL."""
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Start dragging (panning)
            self.last_mouse_position = event.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            # Start rectangle selection
            self.selection.is_selecting = True
            self.selection.selection_start = self.map_to_scene(event.pos())
            self.selection.selection_end = self.selection.selection_start  # Initialize to same point
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            # Handle dragging (panning)
            delta = event.pos() - self.last_mouse_position
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_mouse_position = event.pos()
            self.update()
        elif self.selection.is_selecting and event.buttons() == Qt.MouseButton.RightButton:
            # Update selection rectangle
            self.selection.selection_end = self.map_to_scene(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self.selection.is_selecting:
            # Complete selection
            self.selection.is_selecting = False
            self.selection.perform_selection()
            self.selection.selection_start = None
            self.selection.selection_end = None
            self.update()

    def update_vbo(self):
        """
        This is helper function showing how to access and modify single element from vbo 
        data array. 
        """
        vbo_index = 0
        for layer in self.connections:
            for layer_connections in layer:

                current_vbo = self.vbos[vbo_index][1]
                modify_layer_color_array = np.array(current_vbo, dtype=np.float32)

                for line_idx, line in enumerate(layer_connections):
                    print(line)

    def cleanup(self):
        for vbo_vertices, vbo_colors in self.vbos:
            vbo_vertices.delete()
            vbo_colors.delete()

    def map_to_scene(self, pos):
        """Maps a screen position to the scene coordinates considering transformations."""
        x = (pos.x() - self.offset_x) / self.scale_factor
        y = (pos.y() - self.offset_y) / self.scale_factor
        return x, y
