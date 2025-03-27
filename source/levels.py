# Imports
from threading import (
    Thread, 
    Event,
)
from PySide6.QtWidgets import (
    QGraphicsObject, 
    QGraphicsScene, 
    QGraphicsView, 
    QWidget,
)
from PySide6.QtCore import (
    QObject, 
    QRect, 
    QPoint, 
    QSize, 
    Qt, 
    QPropertyAnimation, 
    QEasingCurve, 
    QParallelAnimationGroup, 
    QSequentialAnimationGroup,
)
from PySide6.QtGui import (
    QPixmap, 
    QTransform,
)
from time import sleep
import numpy as np
import helpers as hlp
import poseestim as pe
import enumoptions as op
import os

# Making dimensions global to use in level func - to be assigned values in start_level
h = None
w = None

# Setting up GUI, signals, and threads to run the level
# If you want to make drastic changes to level UI, do it here
def start_level(parent_ref:QObject | None, level=0):
    '''
    Initializes the GUI elements common to all levels (the dialogue box, NPCs, etc) before
    starting the pose estimation camera thread and the level thread.

    To prematurely quit a level, call cmr_thrd.stop() and game_loop.clear()

    Arguments
    - parent_ref, a reference to the widget which will become the parent of the widgets 
    - level, an int corresponding to the level you want to pick (defaults to 0, a demo level)

    Returns
    - game_loop, a threading event which when cleared stops the game loop
    - camera_thread, a reference/pointer to the pose estimation thread reading the camera
    - level_thread, a reference/pointer to the thread controlling the level

    - scene, a QGraphicsScene object to hold game assets
    - view, a QGraphicsView object to view the scene 
    - overlay, a custom QWidget to display game stats
    '''
    # Getting available screen geometry in local coordinates
    global w, h
    w, h = hlp.get_avail_geo()
    h = h+50 # couldn't figure out why but height was reading slightly too short - had to manually add 50

    # Creating GUI widgets...
    # QGraphicsScene and View to hold all the visuals 
    scene = QGraphicsScene(0, 0, w, h, parent=parent_ref)
    view = QGraphicsView(scene, parent=parent_ref)
    view.setGeometry(0, 0, w, h)
    view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    view.setInteractive(False) # Change this if you want to be able to interact with view by mouse
    view.show()
    # Overlay containing NPC Portrait, Dialogue Box, and Player Portrait
    overlay = hlp.Overlay("Test", parent=view)
    overlay.SIGNAL.CLOSE.connect(parent_ref.close_children)
    overlay.show()

    # Starting camera ML thread...
    camera_thread = pe.Pose_Estimation()
    camera_thread.daemon = True

    # More thread stuff...
    # The invoker was already instantiated on importing helpers.py, and that allows sending GUI commands to execute from main thread
    game_loop = Event()

    # LEVEL SELECTION

    # Calling function of selected level in another thread
    match level:
        case 0: # Demo Level
            # Setup the level objects needed - returns a list or dict of these objects
            setup_objects = setup_demo(scene)

            # Create thread to run level func in parallel - for target put just the name of the func, for args put the args in []
            level_thread = Thread(target=level_demo, args=[scene, view, overlay, setup_objects, game_loop, camera_thread])
            level_thread.daemon = True
            
            #Starting the threads and game loop... needs some time to properly boot up
            camera_thread.start()
            sleep(6)
            game_loop.set()
            level_thread.start()

        case 1:
            # # SKELETON CASE - copy/paste and modify as you see fit
            # # Setup the object levels needed
            # setup_objects = setup_1(scene)
            # # Create thread to run level func in parallel - for target put just the name of the func, for args put the args in []
            # level_thread = Thread(target=level_demo, args=[scene, view, overlay, setup_objects, game_loop, camera_thread])
            # level_thread.daemon = True
            pass

        case _: # Default is the Demo Level
            print("\nERROR: Level does not exist")
            print("Starting default level...")
            setup_objects =  setup_demo(scene)
            
            level_thread = Thread(target=level_demo, args=[scene, view, overlay, setup_objects, game_loop, camera_thread])
            level_thread.daemon = True
            
            #Starting the thread and game loop
            game_loop.set()
            level_thread.start()
    
    # Return the references/pointers
    print("\nReturning pointers to all created objects and threads...")
    # You really only NEED to return the thread and game loop references
    # The rest of the QObjects can be handled and deleted in thread with hlprs.invoke_in_main_thread(fn, args)
    return game_loop, camera_thread, level_thread, scene, view, overlay

# DEMO SETUP
# MUST RETURN LIST OF OBJECTS TO BE USED (if you wanna do something else, modify the start_level func accordingly)
def setup_demo(scene: QGraphicsScene):
    # Making NPC Alice
    alice1 = os.path.join(op.root_dir, "assets", "characters", "Alice", "A-happy.png")
    alice2 = os.path.join(op.root_dir, "assets", "characters", "Alice", "A-neutral.png")
    alice = hlp.Q_NPC(0, [alice1, alice2], 0, 0)
    # The instantiation is the most important, the rest can be altered in thread, but
    # I took scene as an argument and added the items directly to it for convenience
    scene.addItem(alice)
    alice.setVisible(False)

    # Making NPC Bob
    bob1 = os.path.join(op.root_dir, "assets", "characters", "Bob", "B-happy.png")
    bob2 = os.path.join(op.root_dir, "assets", "characters", "Bob", "B-neutral.png")
    bob = hlp.Q_NPC(0, [bob1, bob2], 0.1, 0.1)
    scene.addItem(bob)
    bob.setVisible(False)

    # Making an animation for Alice walking to the center of the screen 
    # You can target the specific size, position, etc. QTransform is not working right now, I'll get that fixed soon
    a_pos = QPropertyAnimation(alice, b'pos')
    a_pos.setStartValue(QPoint(-500, 0))
    a_pos.setEndValue(QPoint(600, 100))
    a_pos.setDuration(1000)
    a_pos.setEasingCurve(QEasingCurve.OutCubic)
    # Make a bit smaller at first to simulate walking forward
    a_scale = QPropertyAnimation(alice, b'scale')
    a_scale.setStartValue(0.5)
    a_scale.setEndValue(1)
    a_scale.setDuration(1000)
    a_scale.setEasingCurve(QEasingCurve.OutCubic)
    # Combine them into one animation
    a_enter = QParallelAnimationGroup()
    a_enter.addAnimation(a_pos)
    a_enter.addAnimation(a_scale)
    
    # KEEP IN MIND: Qt Animations are tied to an object, but that object can be changed with .setTargetObject

    q_objects = {"alice": alice, 
                 "bob": bob, 
                 "a_enter": a_enter}
    return q_objects

# DEMO LEVEL + EXPLANATION
def level_demo(scene:QGraphicsScene, view:QGraphicsView, overlay:hlp.Overlay, obj_list:list|dict,  
               game_loop:Event, cam_thread:pe.Pose_Estimation):
    '''
    This is a level function, where the camera ml results will be read and used as input for the game. This 
    holds the gameplay logic and loop. The arguments are explained below.

    REMEMBER: When you want to use the object_list assets, always use hlpr.invoke_in_main_thread(obj.func, args)
    to be thread safe. If you want to receive returns from a QObject func, you're gonna have to implement that.

    The arguments are...
    - scene is where all the assets are loaded to
    - view is the container for the scene (would only used for entire screen transforms, rare)
    - overlay just holds some stats and options buttons and shows dialogue
    - obj_list is the list or dict holding all the objects you created for your level in the setup
    - game_loop controls whether the game loop is still running or not
    - cam_thread is the camera pose estimation thread that tracks player input
    '''
    # Smaller mini setup 

    # Setting background
    bg_path = os.path.join(op.root_dir, "assets", "backgrounds", "moonlit.png")
    bg_path_2 = os.path.join(op.root_dir, "assets", "backgrounds", "gym.png")
    bg_pixmap = QPixmap(bg_path) 
    bg_pixmap = bg_pixmap.scaledToWidth(w + 50)
    hlp.invoke(scene.setBackgroundBrush, bg_pixmap)

    # Showing first NPC + Enter animation
    hlp.invoke(obj_list["alice"].setVisible, True)
    hlp.invoke(obj_list["a_enter"].start)

    # First line of dialogue
    hlp.invoke(overlay.set_text, "Example of responsiveness - leave the frame")

    # Game loop begins
    while game_loop.is_set():
        # Constantly update the UI Overlay (np is NPC portrait, pp is player portrait)
        frame = cam_thread.get_default_annotation()
        hlp.invoke(overlay.pp.update_frame, frame)

        # Reading player head position from camera thread
        nose_pos, nose_vis = cam_thread.get_body_part()
        # Responding to that
        if nose_vis > 0.9:
            hlp.invoke(overlay.pp.update_stat_bar, 90)
        elif nose_vis > 0.6:
            hlp.invoke(overlay.pp.update_stat_bar, 60)
        elif nose_vis > 0.3:
            hlp.invoke(overlay.pp.update_stat_bar, 30)
        else:
            hlp.invoke(overlay.pp.update_stat_bar, 1)
        
        # # ANIMATION 
        # hlp.invoke(obj_list["a_breathe"].start)
        # # If a Qt animation is called on loop constantly, it may not work. Use a small sleep to give the animation some time
        # # to properly start up and work - one millisecond is enough. 
        # sleep(0.001)
        # # Normally you'd only play Qt animations on certain conditions being met though. If you want an idle loop, utilize
        # # the Q_NPC cycle_img function to cycle through frames of an idle animation

#__________________________ 

# This is where you can write your level functions. Make sure to add a case in the start_level func above to call the setup.
# Feel free to use the skeleton setup and level provided below in level 1! 
# Here are some parts of Qt that may be useful when making your level: 
# https://doc.qt.io/qtforpython-6/PySide6/QtCore/QPropertyAnimation.html 
# https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QTextEdit.html#PySide6.QtWidgets.QTextEdit.setText 
# https://doc.qt.io/qt-6/qgraphicsview.html
# https://doc.qt.io/qt-6/qgraphicsscene.html 
# https://doc.qt.io/qt-6/qgraphicsitem.html 

# Also, keep in mind python's garbage collector exists - if your code relies on an object that gets deleted as soon as setup
# ends, the program won't work.

# SKELETON SETUP
#
def setup_1(scene: QGraphicsScene):
    # Making NPC
    NPC_IMG_1 = os.path.join(op.root_dir, "assets", "characters", "Alice", "YOUR_NPC_IMAGE_1.png")
# SKELETON LEVEL
# 
#TODO