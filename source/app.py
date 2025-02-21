from PySide6.QtCore import (
    QSize, 
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QAction, 
    QPalette, 
    QColor,
    QImage,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QMenu,
)
import sys
import levels

#try to keep a pure python threading pool and only using GUI to listen for a quit command.
#but maybe I'll need to use QT's stuff to accomplish the animations, something to look into



# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.label = QLabel("Loading")
        self.startbutt = QPushButton("Start Level 1")
        self.startbutt.clicked.connect(self.startb)

        self.image_label = QLabel()
        self.image_label.setFixedSize(QSize(320, 240))

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        self.feed = None
        self.started = False

        # adding them all to the layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.startbutt)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.quit_button)

        container = QWidget()
        container.setLayout(self.layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

    
    def startb(self): #start video feed
        self.label.setText("LOADING")

        if not self.started:
            self.started = True
            self.label.setText("Starting")
            
            #self.image_label.setPixmap(QPixmap.fromImage(image))
        else:
            print("already startd bosss")
    

    # also changing the label by detecting events with e - since we inherited that shit hell yeah subclasssing
    # events are similar to signals sent out by individ objects, but they're just detected by the event loop
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            # handle the left-button press in here
            self.label.setText("mousePressEvent LEFT")
            self.t1.stop()

        elif e.button() == Qt.MouseButton.MiddleButton:
            # handle the middle-button press in here.
            self.label.setText("mousePressEvent MIDDLE")

        elif e.button() == Qt.MouseButton.RightButton:
            # handle the right-button press in here.
            self.label.setText("mousePressEvent RIGHT")

# Widget containing the video feed - code by https://gist.github.com/bsdnoobz/8464000
# TODO: alter so it takes info from POSEESTIM.PY's already set up cv feed object, THEN MOVE TO HELPER FUNCS

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
