import threading
import helpers
import poseestim
from time import sleep

def level1(): #would need a kill button that closes the threads
    signals = []

    #t1 = threading.Thread(target=helpers.thread1, args=(signals,))
    #t2 = threading.Thread(target=helpers.thread2, args=(signals,))
    #t1 = poseestim.PoseEstimation()
    t1 = poseestim.PoseEstimation()

    t1.start()
    #t2.start()
        
    sleep(5)
    t1.change_exercise(2)

    return t1.image

#try to keep a pure python threading pool and only using GUI to listen for a quit command.
#but maybe I'll need to use QT's stuff to accomplish the animations, something to look into
#also, make sure to use signals to comm with main thread if you wanna change GUI stuff - levels should only 
#be called in the main thread anyway, but if it blocks its a func call, may have to mcgyver a solution

#   WAIT MAYBE JUST MAKE LEVELS FUCKING CLASSES HOLY SHIT YEAH NO FUCKING SHIT DUDE IM SO DUMB  
# will still need to have func calls within the class (making the threads), but we can make them run at instantiation
# delete class object upon quitting level

#t1 = poseestim.PoseEstimation(1, False)

#t1.start()   
#sleep(5)
#t1.change_exercise(2)
#t1.stop()

def level2():
    # Maybe straight up build the level UI FROM INSIDE THE LEVELS.PY
    # so like import helpers, 
    # when the outside calls level2(), have it pass a blank self widget and clear everything else
    # then have the first helper class you call be a custom QWIDGET CONTAINING THE LEVEL LAYOUT
    # BUT HOW WILL I SET UP THJE THREAD COKMUINICATIPN it sucks that people are so awful at explaining this
    print("fuck me")
    # Fallback plan - still do the helper UI thing, just have some extra messy functions in your main app.py code that trigger 
    # those built in ones - then just connect to the thread code as soon as the level startup func returns with the thread
    # pointers. Follow some bullshit generic tutorial to do that, since you'll have the thread pointers anyway.