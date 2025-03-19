from PySide6.QtCore import (
    QSize, 
    Qt,
    QEvent,
    QCoreApplication,
    QObject,
    QPointF,
    QRectF,
)
from PySide6.QtGui import (
    QImage,
    QPixmap,
    QPainter,
    QMouseEvent,
)
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QProgressBar,
    QGraphicsObject,
    QTextEdit,
)
import numpy as np
import cv2
import enumoptions as op

'''
This is gonna be helper functions to be used in the levels.py file to make it a lot more streamlined to build a level
This should not be accessed by pose estim, nor pose estim by this.

This essentially contains some custom UI elements and animations to move around sprites. Also the signal handler for QT.
If you plan to port this over to a different GUI library, the signal handler is probably the most important thing here.
It is the first class in the document.
'''

########## 
# FUNCTION TO UPDATE GUI FROM OUTSIDE THREAD 
# if you want to adapt this code to work without PySide, it's important you change this

# Function invoke_in_main_thread to update GUI from a different thread
# written by Stack Overflow users chfoo and Petter, taken from this post
# https://stackoverflow.com/questions/10991991/pyside-easier-way-of-updating-gui-from-another-thread

class InvokeEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, fn, *args, **kwargs):
        QEvent.__init__(self, InvokeEvent.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

class Invoker(QObject):
    def event(self, event):
        event.fn(*event.args, **event.kwargs)

        return True

_invoker = Invoker()

def invoke_in_main_thread(fn, *args, **kwargs):
    QCoreApplication.postEvent(_invoker,
        InvokeEvent(fn, *args, **kwargs))

##########
# TODO: ADD MEDIAPIPE ANNOTATION OR MAKE YOUR OWN FUNC

##########
# LEVEL UI - include classes for video feed, which will eventually take capture input from pose estim but only as input by levels.py
class PlayerPortrait(QWidget):
    '''
    RETURNS A Q CLASS - DO NOT USE OUTSIDE OF MAIN THREAD

    '''
    # Constructor
    def __init__(self, player_name, width=320, height=240, show_name=True, show_coords=True, still_portrait=False):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Size of player video/portrait
        self.video_size = QSize(width, height)
        self.new_frame = None

        # These can't change dynamically or it breaks
        self._show_name = show_name
        self._show_coords = show_coords
        self._player_name = player_name
        self._still_portrait = still_portrait

        self.setup_ui()
    
    # Created the nested widgets to hold the UI
    def setup_ui(self):
        # QLabel to hold user camera feed
        self.frame_label = QLabel()
        self.frame_label.setFixedSize(self.video_size)

        # Player name and coordinates under portrait for aesthetics
        self.name_xyz_layout = QHBoxLayout()
        if self._show_name:
            self.display_name = QLabel(self._player_name)
            self.name_xyz_layout.addWidget(self.display_name)
        if self._show_name and self._show_coords:
            # Separator if name and coord are both displayed
            self.name_spacer = QLabel(" - ")
            self.name_xyz_layout.addWidget(self.name_spacer)
        if self._show_coords:
            self.head_x = QLabel()
            self.head_y = QLabel()
            self.head_z = QLabel()
            self.name_xyz_layout.addWidget(self.head_x)
            self.name_xyz_layout.addWidget(self.head_y)
            self.name_xyz_layout.addWidget(self.head_z)

        # Status bar (just HP in this case)
        self.stat_layout = QHBoxLayout()
        self.hp_label = QLabel("HP")
        self.hp_bar = QProgressBar()
        self.hp_bar.setMaximum(100)
        self.stat_layout.addChildWidget(self.hp_label)
        self.stat_layout.addChildWidget(self.hp_bar)

        # Arranging the layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self.frame_label)
        self.main_layout.addLayout(self.name_xyz_layout)
        self.main_layout.addLayout(self.stat_layout)

        #setting the structure of the widget
        self.setLayout(self.main_layout)
    
    #
    # These next few functions are meant to be accessible publicly 
    #
    
    # Updates the video feed with a new input frame
    def update_frame(self, mp_frame: np.ndarray):
        '''
        Pass an annotated mediapipe frame image, or even a plain cam feed frame, to draw onto the UI portrait.
        Takes any image formatted as ndarray or matlike - color should be BGR, because OpenCV and mediapipe
        are weird. 
        
        Only call this func using invoke_in_main_thread().
        
        If colors come out weird, just use cv2.cvtColor(img, cv2.COLOR_RGB2BGR) before passing here.
        '''
        # If player didn't want a live feed and just wants a still portrait, ignore 
        # (ideally do this check in game logic loop to prevent unnecessary calls)
        if self._still_portrait:
            return None

        # Resize down, flip image, and correct BGR to RGB
        new_frame = reformat_image(mp_frame)

        # Converting from numpy array to Qt's format
        self.image = QImage(new_frame, new_frame.shape[1], new_frame.shape[0], 
                       new_frame.strides[0], QImage.Format_RGB888)
        
        # Passing image to the "frame_label" widget
        self.frame_label.setPixmap(QPixmap.fromImage(self.image))
    
    # Updates hp bar - TODO: add option in future for case of multiple status bars
    def update_stat_bar(self, new_val: int, status=0):
        '''
        Function to update hp. Takes two ints as input, first being the new stat value to set,
        second being an int corresponding to the stat bar to update.

        Call using invoke_in_main_thread().

        By default only updates hp, which has the status value 0. If modified for additional
        stat bars, list the codes in this docstring.
        '''
        # TODO: WRITE MORE STAT BARS 
        if status == 0:
            self.hp_bar.setValue(new_val)
        else:
            self.hp_bar.setValue(new_val)

    def update_head_coords(self, new_x: float, new_y: float, new_z: float):
        '''
        Updates the coordinates displayed under the head. 3 inputs for floats corresponding to x y z.

        Call using invoke_in_main_thread()
        '''
        # If player doesn't want to show coordinates, return nothing.
        # (ideally do this in the game logic loop to prevent needless calls)
        if not self._show_coords:
            return None
        
        # Truncating floats and making them into strings
        x = 'X:' + trunc_float_to_str(new_x)
        y = 'Y:' + trunc_float_to_str(new_y)
        z = 'Z:' + trunc_float_to_str(new_z)

        # Setting label text
        self.head_x.setText(x)
        self.head_y.setText(y)
        self.head_z.setText(z)

# Helper functions for portrait      
def reformat_image(image: np.ndarray, new_height = 200, new_width = 200, reformat_mode = 3):
    '''
    Reformat image to fit in frame. Takes as input the image ndarray, the new height, the new width, and the 
    reformat mode.

    Reformat mode is how to manipulate image if the aspect ratio doesn't match. Default is it resizes to height,
    centers the image, and cuts off the overhand on the left and right (if your camera is vertical this does not
    work).

    Mode 0 is stretch
    Mode 1 is preserve ratio and scale down to width
    Mode 2 (and the default case) is scale to width, center, and truncate to desired dimensions
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

def trunc_float_to_str(f_val: float, n=2):
    '''
    Helper to truncate floats and make them into strings.

    Two arguments, f_val for the float to be truncated, and n for how many decimal places (default 2)
    '''
    # Convert to string
    s_val = str(f_val)
    # Check for exponential/scientific notation
    if 'e' in s_val or 'E' in s_val:
        return '{0:.{1}f}'.format(f_val, n)
    # Using a decimal point as the separator, partition return the ones place, the decimal itself, and the decimals
    int_val, point, dec_val = s_val.partition('.')
    # Join the int and decimals with a point between (the list stuff at the end adds extra 0s in case not enough decimals)
    return '.'.join([int_val, (dec_val+'0'*n)[:n]])

##########
# NPC Class
class Q_NPC(QGraphicsObject):
    def __init__(self, name: str, img_paths: list, x_norm=0.0, y_norm=0.0,
                 z_abs: int =None, width_norm: float =None, height_norm=1.0, parent=None): 
        '''
        A QGraphicsObject container for you to put and manipulate NPCs. Use QPropertyAnimation to
        animate as you see fit (just make sure you instantiate both this and the anim in the setup
        func, as they need to be created in the main thread).

        Has access to all the functions of QGraphicsItem, but also some from QObject - the object
        thing really only becomes relevant in that it uses QPropertyAnimation, which only works on
        QObjects but is easier to use and smoother than the deprecated QGraphicsItemAnimation.

        I made instantiation position relative (ie an x val of 0.5 is halfway across the width of
        the screen) and added a set_norm_pos function that sets position this way for convenience.
        If you'd like to use these relative coords, helpers has a global function norm_to_pixel.

        Assume all variables are private, you can't get a return from invoke_in_main_thread and 
        acessing a QObject is not thread safe. 

        Arguments
        - name, just a string holding name, no real use, more for housekeeping
        - img_paths, a list of paths to images associated with object to cycle thru (shows idx 0)
        - x_norm, normalized x value of screen width, defaults to 0 (same as pixel value of zero)
        - y_norm, same as above, maps the height pixels to a value from 0 to 1, also defaults to 0
        - z_abs, the z value if you want to set it at a particular place (default None, takes ints)
        - width_norm, scales the image to a given width (normalized). Only works if height_norm is
          None. If both height_norm and width_norm are None, loads image as is. Default is None.
        - height_norm, scales the image to a given height (normalized, 1 being the height of the 
          screen, always maintaining ratio). Default is 1.0.

        - parent, the parent graphics object - use the QGraphicsItem built in funcs to alter this
        PLEASE KEEP IN MIND IF AN OBJECT HAS A PARENT, ALL COORDS ARE NOW RELATIVE TO THAT PARENT
        '''
        # Calling parent init, with object parent as input
        super().__init__(parent)

        # starting position variables (normalized against fullscreen size)
        self._screen_width, self._screen_height = op.screen_res
        self.x_coord = norm_to_pixel(x_norm, 0)
        self.y_coord = norm_to_pixel(y_norm, 1)

        # Input handling - if only one str path provided
        if type(img_paths) is str:
            img_paths = [img_paths]
        elif type(img_paths) is not list:
            raise Exception("img_paths must be either a string or list of strings containing image paths")
        
        # Image path list stats
        self.idx = 0 # Index of first image in list
        self.num_paths = len(img_paths)
        self.img_paths = img_paths

        # Setting image and scaling it
        self.pixmap = QPixmap(img_paths[0])
        # TODO: give option for wonky stretch/scale if both width and height given (only true scale if one is none)
        if height_norm is not None:
            self.pixmap = self.pixmap.scaledToHeight(norm_to_pixel(height_norm, 1))
        elif width_norm is not None:
            self.pixmap = self.pixmap.scaledToWidth(norm_to_pixel(width_norm, 0))
        
        # Getting initial size
        self.size = self.pixmap.size()
        self.width = self.size.width()
        self.height = self.size.height()

        # Calculate inital bounding box
        self._rect = QRectF(self.x_coord, self.y_coord, self.size.width(), self.size.height())
        self._old_bounds = self._rect

        # Setting Q flags
        # ... 
    
    def boundingRect(self):
        self._rect = QRectF(self.x_coord, self.y_coord, self.width, self.height)
        return self._rect
    
    def paint(self, painter, option, widget):
        # Painter settings
        painter.setRenderHint(QPainter.Antialiasing)

        # Clear out old drawing using old bounds
        painter.fillRect(self._old_bounds, Qt.GlobalColor.transparent)

        # Draw new pixmap
        painter.drawPixmap(self.x_coord, self.y_coord, self.pixmap)
    
    def set_new_img(self, new_path, new_width_norm: float =None, new_height_norm=1.0):
        '''
        Set a new image for the pixmap - one required argument, a string holding the path to the
        new image file.

        Two optional arguments, normalized width and heigh, scales to either, height overrides
        width. If both none imports it as is. By default scales height to screen height.
        '''
        # Store old image dimensions to properly erase it (in case new pix is smaller)
        self._old_bounds = self.boundingRect()

        # Setting an entirely new image, so reassign pixmap
        self.pixmap = QPixmap(new_path)

        # Resize if desired TODO: give option for wonky resize
        if new_height_norm is not None:
            self.pixmap = self.pixmap.scaledToHeight(norm_to_pixel(new_height_norm, 1))
        elif new_width_norm is not None:
            self.pixmap = self.pixmap.scaledToWidth(norm_to_pixel(new_width_norm, 0))

        # Updating size variables
        self.size = self.pixmap.size()
        self.width = self.size.width()
        self.height = self.size.height()

        # Repaint the scene
        self.update()

    def cycle_img(self, index:int =None, resize_mode=2):
        '''
        Function for cycling to the next image (if multiple image paths were given at instantiation). By
        default scales to the previous image's height.

        Two optional args: 
        - index - jump to that given index in list. If none, just shows the next index (default is None)
        - resize_mode - if 0, no resizing, if 1 resizes to prev image width, if 2 resizes to previous img
          height. Default is 2. TODO: make so if valid tuple is input for resize_mode, it resizes to (w,h)
        '''
        # List index input handling
        if index is None:
            # adds one, looping back to zero if out of range
            self.idx = ((self.idx + 1) % self.num_paths)
        else:
            index = (index % self.num_paths)
        
        # Store old image dimensions to properly erase it (in case new pix is smaller)
        self._old_bounds = self.boundingRect()

        # Setting an entirely new image, so reassign pixmap
        self.pixmap = QPixmap(self.img_paths)

        # Resize if desired TODO give option for wonky resize
        if resize_mode == 1:
            self.pixmap = self.pixmap.scaledToWidth(self.width)
        elif resize_mode == 2:
            self.pixmap = self.pixmap.scaledToHeight(self.height)

        # Updating size variables
        self.size = self.pixmap.size()
        self.width = self.size.width()
        self.height = self.size.height()

        # Repaint scene
        self.update()
    
    def set_norm_pos(self, new_x_norm: float, new_y_norm: float):
        '''
        Convenience function for setting the position of NPC using normalized coords.

        Takes two floats, the new x and y values. Values > 1 and < 0 show off screen.
        '''
        x = norm_to_pixel(new_x_norm)
        y = norm_to_pixel(new_y_norm)
        p = QPointF(x, y)
        self.setPos(p)

# Some helpers for the above class, and for use elsewhere
def norm_to_pixel(normalized_value: float, mode: int, resolution: tuple =None):
    '''
    Converts normalized float value to pixel value (ie 0.5 x is halfway across the width, returns 960).
    Always returns an int. Reads screen resolution from config.
    
    Takes one float corresponding to the value, and one int "mode" corresponding to whether the input is
    height or width. Mode 0 returns width, mode 1 returns height. Optionally takes a tuple for resolution
    (w, h), otherwise uses the resolutions in the config file.
    '''
    # Getting resolution
    if resolution is not None and len(resolution) == 2 and type(resolution[0-1]) is int:
        width, height = resolution
    else:
        width, height = op.screen_res
    
    # mode 0 returns width, mode 1 returns height
    if mode == 0:
        return int(normalized_value * width)
    else:
        return int(normalized_value * height)

def pixel_to_norm(pixel_value: int, mode: int, resolution: tuple =None):
    '''
    Converts pixel value to normalized float value (ie 960 x is halfway across the width, returns 0.5).
    Always returns an int. Reads screen resolution from config.
    
    Takes one float corresponding to the value, and one int "mode" corresponding to whether the input is
    height or width. Mode 0 returns width, mode 1 returns height. Optionally takes a tuple for resolution
    (w, h), otherwise uses the resolutions in the config file.
    '''
    # Getting resolution
    if resolution is not None and len(resolution) == 2 and type(resolution[0-1]) is int:
        width, height = resolution
    else:
        width, height = op.screen_res
    
    # mode 0 returns width, mode 1 returns height
    if mode == 0:
        return (pixel_value/width)
    else:
        return (pixel_value/height)

#########
# TODO Maybe some helper functions for background QImage manipulation?
# TODO Maybe some helper functions for custom animations?