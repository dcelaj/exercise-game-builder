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
from time import sleep
from threading import Thread

# TODO: try to keep a pure python threading pool and only using GUI to listen for a quit command.
# but I'll need to use QT's stuff to accomplish the animation helpers, something to look into



# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.label = QLabel()
        self.started = [False]

        self.image_label = QLabel()
        self.image_label.setFixedSize(QSize(32, 24))

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close_two)

        self.testt = QPushButton("Start Test")
        self.testt.clicked.connect(self.start_test)

        self.feed = None

        # adding them all to the layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.testt)

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
        if not self.started[0]:
            #self.started = True # TODO: re-enable and find a way to make it false again when threads exit
            levels.start_level(value)
        else:
            print("already started bosss")
        
        #...
        self.label.setText(f"Done!")

    def start_test(self):
        if not self.started[0]:
            self.feed = levels.level1()
            self.layout.addWidget(self.feed)
            self.started[0] = True
            
            self.lvl_thread = Thread(target=levels.testtt, args=[self.feed, self.started])
            self.lvl_thread.start()
        else: 
            self.started[0] = False
            sleep(5)

    def close_two(self):
        self.started[0] = False
        sleep(1)
        super().close()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()