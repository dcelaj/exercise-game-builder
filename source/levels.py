import threading
import helpers
import poseestim
from time import sleep

# Setting up GUI, signals, and threads to run the level
def start_level(level=0):
    '''
    '''
    # TODO: Write the proper GUI objects and signals startup and also the threading startup, the whole thing really
    print("Creating custom GUI QWidgets...")
    sleep(1)
    print("Creating singal handler QObjects...")
    sleep(1)
    print("Connecting singal handlers to functions...")
    sleep(1)
    print("\n")

    #__________
    # All these print statements are basically a big todo list
    print("Starting camera ML thread...")
    sleep(1.5)
    print("\n")

    #__________
    # Calling function of selected level in another thread
    match level:
        case 0:
            print("Demo Level Selected!")
            print("Starting demo_level thread...")
        case 1:
            print("Level 1 Slected!")
            print("Starting level1 thread...")
        case _:
            print("ERROR: Level does not exist")
            print("Starting default level...")

            # Use the demo level as the default case
            print("Starting demo_level thread...")
    
    # Return the references/pointers
    sleep(2)
    print("\n")
    print("Returning pointers to all created objects and threads...")


# Level functions
import numpy as np # temp, TODO: remove when not needed for testing
def level1():
    feed = helpers.PlayerFeed()
    
    image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

    feed.update_frame(image)

    return feed # still just testing these level funcs normally wouldnt return anything


def level2(): # still just testing these level funcs normally wouldnt return anything
    feed = helpers.PlayerFeed() #maybe eventually pass it dimensions

    t1 = poseestim.Pose_Estimation()

    t1.start()
    sleep(1)

    feed.update_frame(t1.image)
        
    t1.set_exercise(2)

    return feed, t1