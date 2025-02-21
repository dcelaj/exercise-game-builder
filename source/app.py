from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
)
import sys
import levels

# TODO: try to keep a pure python threading pool and only using GUI to listen for a quit command.
# but I'll need to use QT's stuff to accomplish the animation helpers, something to look into



# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.label = QLabel()

        self.image_label = QLabel()
        self.image_label.setFixedSize(QSize(320, 240))

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        self.feed = None
        self.started = False

        # adding them all to the layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.image_label)

        container = QWidget()
        container.setLayout(self.layout)

        # Level Select Buttons
        for i in range(1, 6):  # Creating 5 buttons with values 1 to 5
            level_button = QPushButton(f"Level {i}")
            level_button.clicked.connect(lambda checked, x=i: self.level_button_clicked(x))
            self.layout.addWidget(level_button)

        # Add quit button    
        self.layout.addWidget(self.quit_button)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

    #...
    def level_button_clicked(self, value):
        self.label.setText(f"Loading Level {value}")
        QApplication.processEvents()

        #...
        if not self.started:
            #self.started = True # TODO: re-enable and find a way to make it false again when threads exit
            levels.start_level(value)
        else:
            print("already started bosss")
        
        #...
        self.label.setText(f"Done!")


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
