import glfw
from OpenGL.GL import *
import numpy as np
import time

# Funkcja inicjalizująca OpenGL
def initialize_window():
    # Inicjalizacja GLFW
    if not glfw.init():
        raise Exception("Nie udało się zainicjować GLFW")

    # Tworzenie okna
    window = glfw.create_window(800, 600, "PyOpenGL Rotating Triangle with FPS", None, None)
    if not window:
        glfw.terminate()
        raise Exception("Nie udało się utworzyć okna")

    # Ustawienie kontekstu OpenGL
    glfw.make_context_current(window)
    return window

# Funkcja do tworzenia VBO
def create_vbo():
    # Wierzchołki trójkąta (x, y, r, g, b)
    vertices = np.array([
        0.0,  0.5, 1.0, 0.0, 0.0,  # Góra - czerwony
       -0.5, -0.5, 0.0, 1.0, 0.0,  # Lewy dół - zielony
        0.5, -0.5, 0.0, 0.0, 1.0   # Prawy dół - niebieski
    ], dtype=np.float32)

    # Tworzenie bufora
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    return vbo

# Funkcja do rysowania tekstu FPS
def draw_fps(fps):
    glPushMatrix()
    glLoadIdentity()

    # Ustawienie ortogonalnego widoku 2D
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 0, 600, -1, 1)
    glMatrixMode(GL_MODELVIEW)

    # Rysowanie tekstu
    glColor3f(1, 1, 1)
    glRasterPos2f(10, 570)  # Lewy górny róg (x, y)
    text = f"FPS: {fps:.1f}"
    print(fps)

    # Przywrócenie pierwotnych macierzy
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

# Funkcja do rysowania sceny
def draw_scene(vbo, angle, fps):
    glClear(GL_COLOR_BUFFER_BIT)

    # Ustawienie macierzy modelu
    glPushMatrix()
    glLoadIdentity()
    glRotatef(angle, 0, 0, 1)  # Obrót wokół osi Z

    # Włączanie VBO
    glBindBuffer(GL_ARRAY_BUFFER, vbo)

    # Włączenie atrybutów wierzchołków
    glEnableVertexAttribArray(0)  # Pozycje wierzchołków
    glEnableVertexAttribArray(1)  # Kolory wierzchołków

    # Pozycje wierzchołków (pierwsze 2 liczby z każdego wiersza)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
    # Kolory wierzchołków (kolejne 3 liczby z każdego wiersza)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))

    # Rysowanie trójkąta
    glDrawArrays(GL_TRIANGLES, 0, 3)

    # Wyłączanie atrybutów
    glDisableVertexAttribArray(0)
    glDisableVertexAttribArray(1)

    # Przywrócenie pierwotnej macierzy modelu
    glPopMatrix()

    # Wyświetlenie liczby FPS
    draw_fps(fps)

# Główna funkcja programu
def main():
    window = initialize_window()
    vbo = create_vbo()

    # Zmienna do animacji
    angle = 0
    last_time = time.time()
    frame_count = 0
    fps = 0

    # Główna pętla renderująca
    while not glfw.window_should_close(window):
        # Liczenie FPS
        current_time = time.time()
        frame_count += 1
        if current_time - last_time >= 1.0:
            fps = frame_count / (current_time - last_time)
            frame_count = 0
            last_time = current_time

        # Obracanie trójkąta
        angle += 1
        if angle >= 360:
            angle -= 360

        # Rysowanie sceny
        draw_scene(vbo, angle, fps)

        # Odświeżanie okna
        glfw.swap_buffers(window)
        glfw.poll_events()

    # Sprzątanie zasobów
    glfw.terminate()
if __name__ == "__main__":
    main()
