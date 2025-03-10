from threading import Thread, Event
from time import sleep
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
    - level, an int corresponding to the level you want to pick

    Returns
    - game_loop, a threading event which when cleared stops the game loop
    - cmr_thrd, a reference/pointer to the pose estimation thread reading the camera
    - lvl_thrd, a reference/pointer to the thread controlling the level
    '''

    print("Creating custom GUI QWidgets...")
    # Allocating default variables - feel free to add more to fit your custom UI needs
    # but careful not to delete vars other levels rely on (reuse them all you want though)
    background = None                       # 1 QWidget for background
    dialogue_box = None                     # 1 QWidget for NPC Portrait + dialogue box
    player_portrait = hlpr.PlayerFeed()     # 1 QWidget for Player Feed/Portrait
    # 2 QWidgets for potential NPCs (only to hold/display visuals, not tied to specific NPCs. Num of QWidgets = max NPCs on screen)
    npc1 = None
    npc2 = None
    # 2 QWidgets for misc. objects (again, only to display visuals concurrently, use your own variables to hold state)
    misc1 = None
    misc2 = None

    print("Adding to layout...")
    # Layout to hold bottom bar UI like a fancy visual novel

    #__________________________

    print("\nStarting camera ML thread...")
    # The poseestim thread needs some time to properly boot up
    cmr_thrd = pe.Pose_Estimation()
    sleep(2.5)
    print('...')
    sleep(2.5)

    print("Creating event invoker and flags...")
    # The invoker was done on importing helpers.py, so only creating game loop event flag (a threading event, not a QT event)
    game_loop = Event()

    #__________________________

    # Calling function of selected level in another thread
    match level:
        case 0: # Demo Level
            print("\nDemo Level Selected!")
            print("Starting demo_level thread...")

            # Create thread to run level func in parallel - for target put just the name of the func, for args put the args in []
            lvl_thrd = Thread(target=demo_level, args=[game_loop, cmr_thrd, player_portrait, dialogue_box,
                                                       background, npc1, npc2, misc1, misc2])
            
            #Starting the thread and game loop
            lvl_thrd.start()
            game_loop.set()

        case 1:
            print("\nLevel 1 Slected!")
            print("Starting level1 thread...")

        case _: # Default is the Demo Level
            print("\nERROR: Level does not exist")
            print("Starting default level...")

            # Use the demo level as the default case
            print("Starting demo_level thread...")
            
            lvl_thrd = Thread(target=demo_level, args=[game_loop, cmr_thrd, player_portrait, dialogue_box,
                                                       background, npc1, npc2, misc1, misc2])
            
            #Starting the thread and game loop
            lvl_thrd.start()
            game_loop.set()
    
    # Return the references/pointers
    print("\nReturning pointers to all created objects and threads...")
    # You really only NEED to return the thread and game loop references
    # The rest of the QObjects can be handled and deleted in thread with hlprs.invoke_in_main_thread(fn, args)
    return game_loop, cmr_thrd, lvl_thrd

# DEMO LEVEL
# First arg of a level should be a threading event flag called game_loop - as long as it is set, the game loop continues
# Second arg of a level should be the handle of the pose estim thread given to it (with type hinting so you get auto fill in)
# The rest of the func args should be passed refs to all GUI elements to be manipulated (ONLY USE hlpr.invoke_in_main_thread FUNC)
def demo_level(game_loop:Event, cam_thread:pe.Pose_Estimation, 
               player_feed:hlpr.PlayerFeed, dialogue_box,
               background, npc1, npc2, misc1, misc2):
    
    pass

#__________________________ 

# This is where you can write your level functions. Make sure to modify the start_level func up top to fit your level's needs.
# If you don't need more than 4 changable images on screen (not including the background, dialogue box, or player portrait),
# feel free to use the skeleton provided below in level 1!

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
    while loop.strtd:
        cntr = cntr + 1
        img = t1.get_default_annotation()
        hlpr.invoke_in_main_thread(feed.update_frame, img)
        sleep(0.06)

        if (cntr % 50) == 0: #print results every fifty iter
            res = t1.get_results()
            print(res[-2][-1])
            cntr = 1
    t1.stop()
    