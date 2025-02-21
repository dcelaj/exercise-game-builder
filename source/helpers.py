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
import cv2
import sys

# This is gonna be helper functions to be used in the levels.py file to make it a lot more streamlined to build a level
# This should not be accessed by pose estim, nor pose estim by this
# Pose Estim carries 

# LEVEL UI - include classes for video feed, which will eventually take capture input from pose estim but only as input by levels.py
# TODO: Clean up this whole file, Jesus man
class VideoFeed(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.video_size = QSize(320, 240)
        self.setup_ui()

    def setup_ui(self):
        self.image_label = QLabel()
        self.image_label.setFixedSize(self.video_size)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close) #TODO: make close func that properly releases the capture

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.image_label)
        self.main_layout.addWidget(self.quit_button)

        #setting the structure of the widget
        self.setLayout(self.main_layout)

    #def setup_camera(self):
        #self.capture = cv2.VideoCapture(0) # NO NEED - SHOULD BE HANDLED IN poseestim.py
        # self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_size.width())
        # self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_size.height())

        # Consider deleting these 3 lines and relying on main game loop to call VideoFeed.display_video_stream()
        #self.timer = QTimer()
        #self.timer.timeout.connect(self.display_video_stream)
        #self.timer.start(42) 

    # Read frame from camera and repaint QLabel widget.
    def update_frame(self, frame):
        #_, frame = self.capture.read()
        # Converting from OpenCV's format to general image
        #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #frame = cv2.flip(frame, 1)
        self.frame = frame

        # Converting to Qt's format
        image = QImage(self.frame, self.frame.shape[1], self.frame.shape[0], 
                       self.frame.strides[0], QImage.Format_RGB888)
        
        # Passing image to the "image_label" widget
        self.image_label.setPixmap(QPixmap.fromImage(image))



# This is gonna be helper functions to be used in the levels.py file to make it a lot more streamlined to build a level
# This should not be accessed by pose estim, nor pose estim by this
# Pose Estim carries 

# LEVEL UI - include classes for video feed, which will eventually take capture input from pose estim but only as input by levels.py