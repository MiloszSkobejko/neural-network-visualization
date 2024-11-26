import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt

from network import NetworkGL_Render

class NetworkWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenGL 2D Neural Network")
        self.setGeometry(100, 100, 800, 600)

        self.network_view = NetworkGL_Render(self)
        self.setCentralWidget(self.network_view)

        self.scale_factor = 1.0

        # Below structure of the network; 3 layers 32 x 32 x 24 neurons
        # connected all together (Dense)
        self.network_view.set_network([32, 32, 24])

    def keyPressEvent(self, event):
        """Zooming in / out using [+] and [-] keys"""
        if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.zoom_in()
        elif event.key() == Qt.Key_Minus:
            self.zoom_out()

    def zoom_in(self):
        self.scale_factor *= 1.1
        self.network_view.scale_factor = self.scale_factor
        self.network_view.update()

    def zoom_out(self):
        self.scale_factor /= 1.1
        self.network_view.scale_factor = self.scale_factor
        self.network_view.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NetworkWindow()
    window.show()
    sys.exit(app.exec_())
