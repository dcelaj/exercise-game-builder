from PySide6.QtCore import (
    QSize, 
    Qt,
)
from PySide6.QtGui import (
    QAction, 
    QPalette, 
    QColor,
    QImage,
    QPixmap,
)
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QProgressBar,
)
import numpy as np
import cv2
import sys

'''
This is gonna be helper functions to be used in the levels.py file to make it a lot more streamlined to build a level
This should not be accessed by pose estim, nor pose estim by this.

This essentially contains some custom UI elements and animations to move around sprites. Also the signal handler for QT.
If you plan to port this over to a different GUI library, the signal handler is probably the most important thing here.
It is the first class in the document.
'''

class SignalHandler():
    #TODO: Write
    pass
 
# TODO: ADD MEDIAPIPE ANNOTATION OR MAKE YOUR OWN FUNC
# TODO: WRITE SIGNAL HANDLER FOR QT

# LEVEL UI - include classes for video feed, which will eventually take capture input from pose estim but only as input by levels.py
class PlayerFeed(QWidget):
    '''

    '''
    # Constructor
    def __init__(self, width=320, height=240):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.video_size = QSize(width, height)
        self.new_frame = None
        # TODO: make boolean var to give option to show head coordinates n bars
        self.setup_ui()
    
    # Created the nested widgets to hold the UI
    def setup_ui(self):
        # QLabel to hold user camera feed
        self.frame_label = QLabel()
        self.frame_label.setFixedSize(self.video_size)

        # Coordinates of head - just aesthetics, having some XYZ labels underneath player cam
        self.head_x = QLabel()
        self.head_y = QLabel()
        self.head_z = QLabel()
        self.xyz_layout = QHBoxLayout()
        self.xyz_layout.addWidget(self.head_x)
        self.xyz_layout.addWidget(self.head_y)
        self.xyz_layout.addWidget(self.head_z)
        #quit button, temporary
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close) #TODO: get rid of quit button, handle feed.close in levels.py

        # HP and Progress bars
        self.hp_bar = QProgressBar()
        self.progress_bar = QProgressBar()

        # Arranging the layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.frame_label)
        self.main_layout.addLayout(self.xyz_layout)
        self.main_layout.addWidget(self.hp_bar)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.quit_button)

        #setting the structure of the widget
        self.setLayout(self.main_layout)
    
    #
    # These next few functions are meant to be accessible publicly 
    #
    
    def update_frame(self, mp_frame: cv2.typing.MatLike):
        '''
        Pass an annotated mediapipe frame image, or even a plain cam feed frame, to draw onto the UI portrait.
        Takes any image formatted as ndarray or matlike - color should be BGR, because OpenCV and mediapipe
        are weird. If colors come out weird, just use cv2.cvtColor(img, cv2.COLOR_RGB2BGR) before passing here.
        '''
        # Resize down, flip image, and correct BGR to RGB
        new_frame = reformat_image(mp_frame)

        # Converting from numpy array to Qt's format
        self.image = QImage(new_frame, new_frame.shape[1], new_frame.shape[0], 
                       new_frame.strides[0], QImage.Format_RGB888)
        
        # Passing image to the "frame_label" widget
        self.frame_label.setPixmap(QPixmap.fromImage(self.image))
    
    def update_hp_bar(self, new_hp: int):
        '''

        '''
        pass # TODO: WRITE
    
    def update_progress_bar(self, new_prog: int):
        '''

        '''
        pass # TODO: WRITE

    def update_head_coords(self, new_x: float, new_y: float, new_z: float):
        '''

        '''
        pass

# A function to be used in the above class, but has standalone utility
# Downsize, flip, and adjust the colors of the image. 
# TODO: write description in ''s
def reformat_image(image: cv2.typing.MatLike, new_height = 200, new_width = 200, reformat_mode = 2):
    '''
    '''
    # Set up return variable
    new_image = None

    # Getting current image shape
    image_shape = image.shape
    height = image_shape[0]
    width = image_shape[1]

    # Deciding how to resize image
    if reformat_mode == 0: 
        # Stretch
        new_res = (new_height, new_width)
        new_image = cv2.resize(image, new_res, interpolation= cv2.INTER_AREA)
    elif reformat_mode == 1: 
        # Perserve ratio, scale down to specified width
        ratio = (new_width / width)

        new_image = cv2.resize(image, None, fx= ratio, fy= ratio, interpolation= cv2.INTER_AREA)
    else:
        # Default, scale down to height and crop to get a square, perserving the center
        ratio = (new_height / height)
        scaled_width = int(width * ratio)

        temp = cv2.resize(image, None, fx= ratio, fy= ratio, interpolation= cv2.INTER_AREA)

        # Cropping so as to leave a strip of the center equal to height
        left = int((scaled_width / 2) - (new_height / 2))
        right = left + new_height
        new_image = temp[0:new_height, left:right]

    # Fixing the color and mirroring it
    new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    new_image = cv2.flip(new_image, 1)
    
    return new_image
