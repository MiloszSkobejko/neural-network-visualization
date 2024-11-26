import random
import math
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *

from selection import Selection

class Edge:
    def __init__(self, idx, n_start, n_end, color):
        self.index = idx
        self.start = n_start
        self.end = n_end
        self.color = color
        self.selected = False

    def on_screen(self, viewport):
        """Checks if line is visible in screen"""
        x_min, y_min, x_max, y_max = viewport

        if (self.start.x < x_min and self.end.x < x_min) or \
        (self.start.x > x_max and self.end.x > x_max):
            return False
        if (self.start.y < y_min and self.end.y < y_min) or \
        (self.start.y > y_max and self.end.y > y_max):
            return False

        return True

    def draw(self):
        """Draws a line with given weight"""
        opacity = 0.2
        if self.selected:
            opacity = 1.0

        glColor4f(*self.color, opacity)
        glVertex2f(self.start.x, self.start.y)
        glVertex2f(self.end.x, self.end.y)

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

class NetworkGL_Render(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layers = []
        self.neurons = []
        self.connections = []
        self.scale_factor = 1.0

        self.spacing_x = 1000  # Distance between layers
        self.spacing_y = 50   # Distance between neurons
        self.start_x = 50     # x draw starting value
        self.start_y = 150    # y draw starting value

        self.last_mouse_position = QPoint()
        self.offset_x = 0
        self.offset_y = 0
        self.selection = Selection(self)

    def random_color(self):
        return [random.random(), random.random(), random.random()]

    def set_network(self, layers):
        self.layers = layers
        self.prepare_network()

    def set_network(self, layers):
        """Creates neuron and weights connections based on structure"""
        self.layers = layers
        self.neurons = []
        self.connections = []

        # Creating neurons
        for layer_idx, neuron_count in enumerate(self.layers):
            layer_x = self.start_x + layer_idx * self.spacing_x
            layer_neurons = []

            for neuron_idx in range(neuron_count):
                neuron_y = self.start_y + neuron_idx * self.spacing_y
                neuron_color = self.random_color()

                neuron = Neuron([layer_idx, neuron_idx], 
                                 layer_x, neuron_y, 
                                 neuron_color)
                layer_neurons.append(neuron)
            self.neurons.append(layer_neurons)

        # Creating connections
        for i in range(len(self.neurons) - 1):
            for start_idx, neuron_start in enumerate(self.neurons[i]):
                for end_idx, neuron_end in enumerate(self.neurons[i + 1]):
                    connection_color = self.random_color()
                    line = Edge([i, start_idx, end_idx], 
                                 neuron_start, neuron_end, 
                                 connection_color)
                    self.connections.append(line)

    def paintGL(self):
        """Rendering using OpenGL"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(self.offset_x, self.offset_y, 0)
        glScalef(self.scale_factor, self.scale_factor, 1.0)

        # Calculate visible area of viewport, so objects
        # out of scene don't have to be rendered
        w, h = self.width(), self.height()
        x_min = -self.offset_x / self.scale_factor
        x_max = (w - self.offset_x) / self.scale_factor
        y_min = -self.offset_y / self.scale_factor
        y_max = (h - self.offset_y) / self.scale_factor
        viewport = (x_min, y_min, x_max, y_max)

        # [OPTIMIZATION 1]
        # Draw n-th line when zoom is far out 
        skip_factor = max(1, int(1 / self.scale_factor))

        # Drawing lines
        glBegin(GL_LINES)
        for idx, line in enumerate(self.connections):
            if idx % skip_factor == 0:
                # [OPTIMIZATION 2]
                # Don't draw objects when they are out
                # of viewport.
                if not line.on_screen(viewport):
                    continue
                line.draw()
        glEnd()

        # Drawing neurons
        for layer in self.neurons:
            for neuron in layer:
                # [OPTIMIZATION 2]
                # Don't draw objects when they are out
                # of viewport.
                if not neuron.on_screen(viewport):
                    continue
                neuron.draw()

        # Drawing selection rectangle
        if self.selection.is_selecting and \
           self.selection.selection_start and \
           self.selection.selection_end:
            glColor4f(1, 1, 1, 0.3)  # Transparent white
            glBegin(GL_QUADS)
            x1, y1 = self.selection.selection_start
            x2, y2 = self.selection.selection_end 
            glVertex2f(x1, y1)
            glVertex2f(x2, y1)
            glVertex2f(x2, y2)
            glVertex2f(x1, y2)
            glEnd()

    def resizeGL(self, w, h):
        """Resizing OpenGL viewport to the size of window"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def initializeGL(self):
        """Initialization of OpenGL."""
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)  # Włącz tryb mieszania
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # Ustaw funkcję mieszania

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_position = event.pos()
        elif event.button() == Qt.RightButton:
            # Start of rectangle selection
            self.selection.is_selecting = True
            self.selection.selection_start = self.map_to_scene(event.pos())
            self.selection.selection_end = self.selection.selection_start

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.pos() - self.last_mouse_position
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_mouse_position = event.pos()
            self.update()
        elif self.selection.is_selecting and event.buttons() == Qt.RightButton:
            # Update selection rectangle
            self.selection.selection_end = self.map_to_scene(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.selection.is_selecting:
            self.selection.is_selecting = False
            self.selection.perform_selection()
            self.selection.selection_start = None
            self.selection.selection_end = None
            self.update()

    def map_to_scene(self, pos):
        """Maps a screen position to the scene coordinates considering transformations."""
        x = (pos.x() - self.offset_x) / self.scale_factor
        y = (pos.y() - self.offset_y) / self.scale_factor
        return x, y
