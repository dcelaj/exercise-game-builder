from threading import Thread, Event, Lock
from time import sleep
from PySide6.QtWidgets import QGraphicsObject, QGraphicsScene, QGraphicsView, QWidget
from PySide6.QtCore import QObject, QRect, QPoint, Qt
import numpy as np
import helpers as hlpr
import poseestim as pe

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
    w, h = hlpr.get_avail_geo()
    h = h+50 # couldn't figure out why but height was reading slightly too short - had to manually add 50

    # Creating GUI widgets...
    # QGraphicsScene and View to hold all the visuals 
    scene = QGraphicsScene(0, 0, w, h, parent=parent_ref)
    view = QGraphicsView(scene, parent=parent_ref)
    view.setGeometry(0, 0, w, h)
    view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    view.setInteractive(False) # Change this is you want to be able to interact with view by mouse
    view.show()
    # Overlay containing NPC Portrait, Dialogue Box, and Player Portrait
    overlay = hlpr.Overlay("Test", parent=view)
    overlay.dialogue_box.SIGNAL.CLOSE.connect(parent_ref.close_children)
    overlay.show()

    
    return level, 0, 0, 0, 0, 0 #TODO DELETE THIS IS JUST A TEST STOP

    # Starting camera ML thread... - needs some time to properly boot up
    camera_thread = pe.Pose_Estimation()
    camera_thread.daemon = True
    sleep(5)

    # More thread stuff...
    # The invoker was already instantiated on importing helpers.py, and that allows sending GUI commands to execute from main thread
    game_loop = Event()

    #__________________________

    # Calling function of selected level in another thread
    match level:
        case 0: # Demo Level
            print("\nDemo Level Selected!")
            print("Starting demo_level thread...")

            # Setup the level objects needed - returns a list or dict of these objects
            setup_objects =  setup_level()

            # Create thread to run level func in parallel - for target put just the name of the func, for args put the args in []
            level_thread = Thread(target=level_demo, args=[scene, view, overlay, setup_objects, game_loop, camera_thread])
            level_thread.daemon = True
            
            #Starting the thread and game loop
            game_loop.set()
            level_thread.start()

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
    return game_loop, camera_thread, level_thread, scene, view, overlay

# DEMO SETUP + EXPLANATION
# MUST LIST OF OBJECTS TO BE USED (if you wanna do something else, modify the start_level func accordingly)
def setup_demo():
    pass

# DEMO LEVEL + EXPLANATION
def level_demo(scene:QGraphicsScene, view:QGraphicsView, overlay:QGraphicsObject, object_list:list|dict,  
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
    - object_list is the list or dict holding all the objects you created for your level in the setup
    - game_loop controls whether the game loop is still running or not
    - cam_thread is the camera pose estimation thread that tracks player input
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
    