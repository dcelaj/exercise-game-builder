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
import time
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
    bob = hlp.Q_NPC(0, [bob2, bob1], 0.1, 0.1)
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
    # However, animation groups do not have this function, only singular animations.

    # Enemy NPC
    ghost1 = os.path.join(op.root_dir, "assets", "characters", "enemies", "ghost.png")
    ghost = hlp.Q_NPC("ghost", [ghost1], 0.7, 0.2)
    scene.addItem(ghost)
    ghost.setVisible(False)

    q_objects = {"alice": alice, 
                 "bob": bob, 
                 "a_enter": a_enter,
                 "ghost": ghost}
    return q_objects

# DEMO LEVEL + EXPLANATION
def level_demo(scene:QGraphicsScene, view:QGraphicsView, overlay:hlp.Overlay, obj_list:list|dict,  
               game_loop:Event, cam_thread:pe.Pose_Estimation):
    '''
    This is a level function, where the camera ml results will be read and used as input for the game. This 
    holds the gameplay logic and loop. The arguments are explained below.

    REMEMBER: When you want to use the object_list assets, always use hlpr.invoke(obj.func, args) to be thread
    safe. If you want to receive returns from a QObject func, you're gonna have to implement that.

    The arguments are...
    - scene is where all the assets are loaded to
    - view is the container for the scene (would only used for entire screen transforms, rare)
    - overlay just holds some stats and options buttons and shows dialogue
    - obj_list is the list or dict holding all the objects you created for your level in the setup
    - game_loop controls whether the game loop is still running or not
    - cam_thread is the camera pose estimation thread that tracks player input
    '''
    # Smaller mini setup

    # Internal variables
    phase = 0 
    # Used to create different phases within a level by checking this with an if
    # and having conditions for changing it within that if
    counter = 0
    player_hp = 100
    enemy_1_hp = 15
    results = None
    combo = 0 # successes in a row

    # Setting background
    trans = os.path.join(op.root_dir, "assets", "backgrounds", "transition.png")
    bg_path = os.path.join(op.root_dir, "assets", "backgrounds", "moonlit.png")
    bg_path_2 = os.path.join(op.root_dir, "assets", "backgrounds", "gym.png")
    bg_pixmap = QPixmap(bg_path_2) 
    bg_pixmap = bg_pixmap.scaledToWidth(w + 50)
    hlp.invoke(scene.setBackgroundBrush, bg_pixmap)

    # Showing first NPC + Enter animation
    hlp.invoke(obj_list["alice"].setVisible, True)
    hlp.invoke(obj_list["a_enter"].start)

    # First line of dialogue
    hlp.invoke(overlay.set_text, "Hi, I'm Alice. Welcome to the gym!")
    sleep(2) # Time for player to read

    # Game loop begins
    while game_loop.is_set():
        # Constantly update the UI Overlay (np is NPC portrait, pp is player portrait)
        frame = cam_thread.get_default_annotation()
        hlp.invoke(overlay.pp.update_frame, frame)

        # Updating HP constantly based off player head visibility for no reason other than it looks neat
        nose_pos, nose_vis = cam_thread.get_body_part()
        hlp.invoke(overlay.pp.update_stat_bar, int(nose_vis * 100))
        
        # Begin first phase
        if phase == 0:
            # Gameplay logic
            # Updating results list and checking for successes every 200 loops (about every 2 sec on my machine)
            # this is necessary because our loop is much faster than the machine learning models can inference
            if (counter % 200) == 0:
                results = cam_thread.ex_results
                results = list(results)
                if len(results) < 32:
                    extras = 32 - len(results)
                    for i in range(1, extras):
                        results.append(0)
                
                # Let's make multiple successes in a row build a combo! 
                # I'll count over half the results being positive as a success.
                if sum(results) > 16:
                    # Increase combo
                    combo += 1
                elif sum(results) == 0:
                    # If all are fail, let's decrease combo
                    combo += -1
                
                # If you build a big enough combo, things happen!
                if combo > 25:
                    hlp.invoke(overlay.set_text, "Wow, great job!")
                    hlp.invoke(obj_list["alice"].cycle_img, 0)
                elif combo < -35:
                    hlp.invoke(overlay.set_text, "Looks like you need a breather. Take a moment to recover.")
                    hlp.invoke(obj_list["alice"].cycle_img, 1)
                    combo = 0
            #

            # I'll increment counter each time the if block is executed so these are one time events:
            if counter == 0:
                hlp.invoke(overlay.set_text, "Here we enter the first phase! Let's start off with some high-knees.")
                hlp.invoke(obj_list["alice"].cycle_img, 1)
            elif counter == 600:
                a = "Each distinct phase of the game is held in a big if statement within the game loop - if phase == 1"
                b = ": do the checks for the specific exercise, etc. This is nice because each section ends up organized under "
                c = "it's own if statement, but they can share data. This level uses an additional counter variable to check how many"
                d = a + b + c + " loops have been spent in one phase. Right now the game is frozen so you have time to read this."
                hlp.invoke(overlay.set_text, d)
                sleep(10)
            elif counter == 1800:
                a = "Right now, the level thread is getting the last two seconds of results from the camera thread and seeing "
                b = "how many frames were successfully doing the exercise. It does this every few seconds by using an "
                c = "if statement like this in the game loop: if (counter % 200) == 0: results = cam_thread.ex_results"
                d = a + b + c + ". This is necessary because the game loop is far faster than the ML inference."
                hlp.invoke(overlay.set_text, d)
                sleep(10)
            elif counter == 3000:
                a = "It's recommended to use time.time() rather than relying on loop timing to time checks though, so it's consistent "
                b = "on faster machines. Finally, don't forget an if statement at the very end checking for the criteria to "
                c = "change the level phase or win the level. Otherwise I'm stuck working my shift at this gym for all eternity. "
                d = a + b + c + " There are lots of if statements when making a game with this but it ends up pretty neat."
                hlp.invoke(overlay.set_text, d)
                sleep(10)
            elif counter == 4200:
                d = "Now let's get back to exercising!"
                hlp.invoke(overlay.set_text, d)

            # Incrementing counter and checking for next phase condition
            counter += 1
            if counter > 20000 or combo > 50:
                phase = 1
                counter = 0
                hlp.invoke(overlay.set_text, "Great job! Let's take a breather.")
                hlp.invoke(obj_list["alice"].cycle_img, 0)

                # Transition screen
                sleep(5)
                hlp.invoke(obj_list["alice"].setVisible, False)
                hlp.invoke(overlay.set_text, " ")
                bg_pixmap = QPixmap(trans)
                bg_pixmap = bg_pixmap.scaledToWidth(w + 50)
                hlp.invoke(scene.setBackgroundBrush, bg_pixmap)

                # Setting new exercise model
                cam_thread.set_exercise(op.Exercises.SWING_SWORD.value)
                sleep(5)

                # Change setting for new phase
                bg_pixmap = QPixmap(bg_path) 
                bg_pixmap = bg_pixmap.scaledToWidth(w + 50)
                hlp.invoke(scene.setBackgroundBrush, bg_pixmap)

                hlp.invoke(obj_list["bob"].setVisible, True)
                hlp.invoke(overlay.set_text, "Hi, I'm Bob! I found you knocked out cold in this forest.")
                sleep(5)
        
        # Begin second phase
        if phase == 1:
            # Dialogue/Cutscene
            if counter == 0:
                hlp.invoke(overlay.set_text, "These woods are dangerous - and perfect for showing off combat mechanics.")
                sleep(5)
                hlp.invoke(overlay.set_text, "Oh no, is that a g-g-g-g-g-g-ghost?")
                hlp.invoke(obj_list["ghost"].setVisible, True)
                sleep(5)
                hlp.invoke(overlay.set_text, "Quickly, use the sword you have because this is a fantasy RPG setting! TAKE A SWING!")
                sleep(5)
            
            if (counter % 200) == 0:
                # Getting results
                results = cam_thread.ex_results
                results = list(results)
                if len(results) < 32:
                    extras = 32 - len(results)
                    for i in range(1, extras):
                        results.append(0)
                
                # Input check
                if sum(results) > 16:
                    enemy_1_hp += -5
                elif sum(results) == 0:
                    player_hp += -5
                    enemy_1_hp += 5
                
                # Health check
                if enemy_1_hp < 5 or enemy_1_hp > 100: # the second part is just giving you the win if you're losing bc it's a tutorial
                    hlp.invoke(obj_list["ghost"].setVisible, False)
                    hlp.invoke(overlay.set_text, "You saved us AND you demonstrated the potential gameplay mechanics!")
                    hlp.invoke(obj_list["bob"].cycle_img)
                    sleep(5)
                    hlp.invoke(overlay.set_text, "Level Complete!")
                    sleep(5)
                    # artificially setting counter high so level ends - probably best to use time.time() for these but I'm lazy rn
                    counter = 19800
                
            # Counter and win condition check
            counter += 1
            if counter > 19998:
                phase = 3
                game_loop.clear()
        #

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
    img = os.path.join(op.root_dir, "assets", "characters", "Alice", "YOUR_NPC_IMAGE_1.png")
    name = hlp.Q_NPC("NAME", [img], 0, 0)
    scene.addItem(name)

    # Making an Animation
    anim1 = QPropertyAnimation(name, b'PROPERTY_NAME_TO_ANIMATE')
    anim1.setStartValue()
    anim1.setEndValue()
    anim1.setEasingCurve()
    # Combining Animations
    anim2 = QPropertyAnimation(name, b'PROPERTY_NAME_TO_ANIMATE')
    combo = QParallelAnimationGroup()
    combo.addAnimation(anim1)
    combo.addAnimation(anim2)

    # Putting it all in a dict and returning it
    q_objects = {
        "NPC Name": name,
        "Animation": combo
    }
    return q_objects

# SKELETON LEVEL
# 
def level_1(scene:QGraphicsScene, view:QGraphicsView, overlay:hlp.Overlay, obj_list:list|dict,  
               game_loop:Event, cam_thread:pe.Pose_Estimation):
    # REMEMBER: Use invoke_in_main_thread (or just invoke) when changing GUI elements

    # Smaller mini setup
    # Counter and phase variable to help control how frequently things get checked and pacing of level
    phase = 0
    counter = 0
    t = time.time()
    # Background
    bg_path = os.path.join(op.root_dir, "assets", "backgrounds", "YOUR_BACKGROUND_HERE.png")
    bg_pixmap = QPixmap(bg_path) 
    bg_pixmap = bg_pixmap.scaledToWidth(w)
    hlp.invoke(scene.setBackgroundBrush, bg_pixmap)
    # NPC
    hlp.invoke(obj_list["NPC Name"].setVisible, True)
    # Dialogue
    hlp.invoke(overlay.set_text, "YOUR TEXT HERE")
    
    # Game loop
    while game_loop.is_set():
        # Update player frame if needed
        frame = cam_thread.get_default_annotation()
        hlp.invoke(overlay.pp.update_frame, frame)

        # YOUR GAME LOGIC HERE

# _________________________
def start_3d_level():
    # Since Qt doesn't have a container for 3d items, it would instead be best to handle 3d assets with some other library
    # that supports efficiently reading and interacting with them, and also ideally has some camera funtion. You could then
    # continually read the virtual camera, perhaps move it based on player input, and print that output onto a QPixmap or
    # any normal image container.
    # You'd probably also want to do interpolation and manage the input delay since movement will be slightly delayed and 
    # choppy. This might be a project for another time, but it may be more efficient to just write a wrapper for MediaPipe
    # to work with pre-existing 3D game software like Godot. That might be instead what I tackle next.

    # Resources for future me or someone else who decides to tackle the 3D support:
    # https://github.com/wikibook/dl-vision/blob/master/Chapter07/ch7_nb3_render_images_from_3d_models.ipynb 
    # https://pypi.org/project/plyfile/
    # https://pypi.org/project/PyOpenGL/
    pass
# _________________________
