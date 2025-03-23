from threading import Thread, Event, Lock
from time import sleep
from PySide6.QtWidgets import QGraphicsObject, QGraphicsScene, QGraphicsView, QWidget
import numpy as np
import helpers as hlpr
import poseestim as pe

# Setting up GUI, signals, and threads to run the level
# If you want to make drastic changes to level UI, do it here
def start_level(layout_ref, level=0):
    '''
    Initializes the GUI elements common to all levels (the dialogue box, NPCs, etc) before
    starting the pose estimation camera thread and the level thread.

    To prematurely quit a level, call cmr_thrd.stop() and game_loop.clear()

    Arguments
    - layout_ref, a reference to pass a QT layout for the UI elements to be added to
    - level, an int corresponding to the level you want to pick (defaults to 0, a demo level)

    Returns
    - game_loop, a threading event which when cleared stops the game loop
    - graphics_lock, a threading lock/mutex for when the game logic thread needs to access QGraphicsView returns
    - camera_thread, a reference/pointer to the pose estimation thread reading the camera
    - level_thread, a reference/pointer to the thread controlling the level

    - canvas, a QGraphicsScene object to hold game assets
    - canvas_view, a QGraphicsView object to view the scene TODO 
    - overlay, a custom QWidget to display game stats
    '''

    print("Creating GUI QWidgets...")
    # QGraphicsScene and View to hold all the visuals
    canvas = None
    canvas_view = None
    layout_ref.addWidget(canvas_view)
    # Overlay containing NPC Portrait, Dialogue Box, and Player Portrait
    overlay = None
    layout_ref.addWidget(overlay) # look for way to parent canvas so overlay is always over it

    print("Adding to layout...")
    # Layout to hold bottom bar UI like a fancy visual novel

    print("\nStarting camera ML thread...")
    # The poseestim thread needs some time to properly boot up
    camera_thread = pe.Pose_Estimation()
    sleep(5)

    print("Creating thread safe communication...")
    # The invoker was already instantiated on importing helpers.py, but that allows sending GUI commands to execute from main thread
    game_loop = Event()
    graphics_lock = Lock()

    #__________________________

    # Calling function of selected level in another thread
    match level:
        case 0: # Demo Level
            print("\nDemo Level Selected!")
            print("Starting demo_level thread...")

            # Create thread to run level func in parallel - for target put just the name of the func, for args put the args in []
            level_thread = Thread(target=demo_level, args=[canvas, overlay, game_loop, graphics_lock, camera_thread])
            
            #Starting the thread and game loop
            level_thread.start()
            game_loop.set()

        case 1:
            print("\nLevel 1 Slected!")
            print("Starting level1 thread...")

        case _: # Default is the Demo Level
            print("\nERROR: Level does not exist")
            print("Starting default level...")

            # Use the demo level as the default case
            print("Starting demo_level thread...")
            
            level_thread = Thread(target=demo_level, args=[canvas, overlay, game_loop, graphics_lock, camera_thread])
            
            #Starting the thread and game loop
            level_thread.start()
            game_loop.set()
    
    # Return the references/pointers
    print("\nReturning pointers to all created objects and threads...")
    # You really only NEED to return the thread and game loop references
    # The rest of the QObjects can be handled and deleted in thread with hlprs.invoke_in_main_thread(fn, args)
    return game_loop, graphics_lock, camera_thread, level_thread, canvas, canvas_view, overlay

# DEMO SETUP + EXPLANATION
# MUST RETURN THREAD REFERENCE/POINTER
def setup_demo_level():
    pass

# DEMO LEVEL + EXPLANATION
def demo_level(canvas:QGraphicsScene, canvas_view:QGraphicsView, overlay:QGraphicsObject, object_list:list|dict,  
               game_loop:Event, graphics_lock:Lock, cam_thread:pe.Pose_Estimation):
    '''
    - Canvas is where all the assets are loaded to, canvas_view is the container for it (prob won't be used, feel free to not include)
    - Overlay just holds some stats and options buttons and shows dialogue
    - Game loop controls whether the game loop is still running or not
    - Graphics lock is intended to be used if you're doing complex stuff with the canvas and need a return from it (rare)
    - Cam thread is the camera pose estimation thread that tracks player input

    - The third argument, object_list, holds a list/dict with the references to all the QObjects created in the setup func
    - Whenever you want to update those assets, always use hlpr.invoke_in_main_thread(obj.func, args)
    '''
    
    pass

#__________________________ 

# This is where you can write your level functions. Make sure to add a case in the start_level func above to call the setup.
# Feel free to use the skeleton setup and level provided below in level 1! 
# Here are some parts of Qt that may be useful when making your level: 
# https://doc.qt.io/qtforpython-6/PySide6/QtCore/QPropertyAnimation.html 
# https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QTextEdit.html#PySide6.QtWidgets.QTextEdit.setText 
# https://doc.qt.io/qt-6/qgraphicsview.html
# https://doc.qt.io/qt-6/qgraphicsscene.html 
# https://doc.qt.io/qt-6/qgraphicsitem.html 

# SKELETON SETUP
#

# SKELETON LEVEL
# 

def level1():
    feed = hlpr.PlayerFeed()
    
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

    feed.update_frame(image)

    return feed # still just testing these level funcs normally wouldnt return anything


def level2(): # still just testing these level funcs normally wouldnt return anything
    feed = hlpr.PlayerFeed() #maybe eventually pass it dimensions

    t1 = pe.Pose_Estimation()

    t1.start()
    sleep(1)

    feed.update_frame(t1.image)
        
    t1.set_exercise(2)

    return feed, t1

def testtt(feed, loop): # level func args should contain refs to all GUI elements to be manipultd - poseestim should be created inside
    # ALSO PASS A GAME LOOP BOOL VAR SO WE CAN DO WHILE GAMELOOP AFTER INITIALIZING THE CAM
    t1 = pe.Pose_Estimation()
    t1.start()
    img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    feed.update_frame(img)
    sleep(5)
    cntr = 0
    while loop[0]:
        cntr = cntr + 1
        img = t1.get_default_annotation()
        res = t1.get_results()
        hp = ((int(res[-2][-1]) + 1) * 33) + 1

        hlpr.invoke_in_main_thread(feed.update_frame, img)
        hlpr.invoke_in_main_thread(feed.update_hp_bar, int(hp))
        sleep(0.06)

        if (cntr % 50) == 0: #print results every fifty iter
            print(res[-2][-1])
            cntr = 1
    t1.stop()
    